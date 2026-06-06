"""
Agent tool wrappers — carbonate rock physics.

Wraps rock_physics.carbonate_model for the Gemini AFC agent.

Pipeline per tool call: VRH mineral average → Batzle-Wang fluid mix →
Berryman DEM dry frame → Gassmann fluid substitution → Vp / Vs / impedance.

Design notes
------------
- Mineralogy crosses the tool boundary as a JSON string (weight fractions)
  for the same schema-clarity reason as geochemistry tools.
- The bridge tool (phreeqc_moles_to_rock_physics_inputs) is the join between
  the geochemistry and rock-physics modules.

Units at the tool boundary
--------------------------
temperature  : °C   (different from geochemistry tools, which use Kelvin)
pressure     : MPa
salinity     : ppm by weight
porosity     : fraction [0, 1]
aspect ratio : fraction [0, 1]  (0.01 = crack-like, 1.0 = spherical)
saturation   : fraction [0, 1]
velocity     : km/s
impedance    : MRayl  (= km/s · g/cm³)
"""

import json
import numpy as np
import rock_physics.carbonate_model as rp
import chainlit as cl


def _parse_mineralogy(mineralogy_wt_json: str) -> dict:
    if not mineralogy_wt_json or not mineralogy_wt_json.strip():
        return {}
    raw = json.loads(mineralogy_wt_json)
    unknown = set(raw) - rp.VALID_MINERALS
    if unknown:
        raise ValueError(
            f"Unknown minerals: {sorted(unknown)}. "
            f"Valid: {sorted(rp.VALID_MINERALS)}"
        )
    return {k: float(v) for k, v in raw.items()}


@cl.step(type="tool", name="Rock Physics: Seismic State")
async def carbonate_rock_seismic_state(
    mineralogy_wt_json: str,
    porosity: float,
    aspect_ratio: float,
    temperature_c: float,
    pressure_mpa: float,
    salinity_ppm: float,
    co2_saturation: float,
) -> dict:
    """Compute seismic properties of a carbonate reservoir rock at one state.

    Runs the full VRH → Batzle-Wang → Berryman DEM → Gassmann pipeline and
    returns Vp, Vs, density, acoustic impedance, and elastic moduli.

    Use this for a single reservoir condition (one porosity, one saturation).
    For sweeps use carbonate_rock_saturation_sweep; for 4D contrast use
    carbonate_rock_4d_contrast.

    Args:
        mineralogy_wt_json: JSON object string of mineral weight fractions.
            Valid keys: calcite, dolomite, siderite, quartz, k-feldspar,
            albite, smectite, kaolinite, illite, chlorite, pyrite, anhydrite.
            Example: '{"calcite": 0.88, "dolomite": 0.05, "quartz": 0.07}'.
            Fractions are normalised internally and need not sum to 1.
        porosity: Pore volume fraction [0, 1].
        aspect_ratio: Pore/crack aspect ratio [0, 1]. Use ~0.01 for crack-like
            pores (low stiffness), ~0.1-0.3 for typical carbonates,
            ~1.0 for spherical pores (stiff frame).
        temperature_c: Temperature in °C.
        pressure_mpa: Pressure in MPa.
        salinity_ppm: Formation water salinity in ppm by weight
            (e.g. 35000 for seawater, 70000 for typical saline aquifer).
        co2_saturation: CO2 fraction in pore space [0, 1].
            0 = fully brine-saturated (baseline), 1 = fully CO2-saturated.

    Returns:
        dict with keys: Vp_kms, Vs_kms, rho_gcc, acoustic_impedance_Vp,
        acoustic_impedance_Vs, Vp_Vs_ratio, K_sat_GPa, G_sat_GPa,
        K_mineral_GPa, G_mineral_GPa, rho_mineral_gcc, rho_fluid_gcc,
        K_fluid_GPa.
    """
    try:
        wt_fracs = _parse_mineralogy(mineralogy_wt_json)
        return rp.seismic_state(
            wt_fracs, porosity, aspect_ratio,
            temperature_c, pressure_mpa, salinity_ppm, co2_saturation,
        )
    except Exception as e:
        return {"error": str(e)}


@cl.step(type="tool", name="Rock Physics: Saturation Sweep")
async def carbonate_rock_saturation_sweep(
    mineralogy_wt_json: str,
    porosity: float,
    aspect_ratio: float,
    temperature_c: float,
    pressure_mpa: float,
    salinity_ppm: float,
    n_points: int = 50,
) -> dict:
    """Compute Vp, Vs, and impedance vs CO2 saturation from 0 to 1.

    Returns curves showing how seismic velocities change as CO2 progressively
    displaces brine. The first point (S_CO2 = 0) is the brine-saturated
    baseline. Useful for 4D seismic feasibility and saturation sensitivity.

    Args:
        mineralogy_wt_json: JSON object string of mineral weight fractions.
            Same format as carbonate_rock_seismic_state.
        porosity: Pore volume fraction [0, 1].
        aspect_ratio: Pore/crack aspect ratio [0, 1].
        temperature_c: Temperature in °C.
        pressure_mpa: Pressure in MPa.
        salinity_ppm: Salinity in ppm by weight.
        n_points: Number of saturation steps from 0 to 1 (default 50).

    Returns:
        dict with lists: co2_saturation, Vp_kms, Vs_kms, rho_gcc,
        acoustic_impedance_Vp, Vp_Vs_ratio,
        delta_Vp_pct (% change from brine baseline),
        delta_Vs_pct (% change from brine baseline).
    """
    try:
        wt_fracs = _parse_mineralogy(mineralogy_wt_json)
        saturations = np.linspace(0.0, 1.0, int(n_points)).tolist()

        K_min, G_min, rho_min = rp.effective_mineral_moduli(wt_fracs)
        max_porosity = max(porosity + 0.02, 0.05)
        K_dry_arr, G_dry_arr, phi_arr = rp.dem_dry_frame(K_min, G_min, aspect_ratio, max_porosity)
        K_dry = float(np.interp(porosity, phi_arr, K_dry_arr))
        G_dry = float(np.interp(porosity, phi_arr, G_dry_arr))

        result = {
            "co2_saturation": [],
            "Vp_kms": [], "Vs_kms": [], "rho_gcc": [],
            "acoustic_impedance_Vp": [], "Vp_Vs_ratio": [],
            "delta_Vp_pct": [], "delta_Vs_pct": [],
        }
        Vp_baseline = Vs_baseline = None

        for s in saturations:
            rho_fl, K_fl = rp.fluid_properties(temperature_c, pressure_mpa, salinity_ppm, s)
            K_sat, G_sat = rp.gassmann(K_dry, G_dry, K_min, K_fl, porosity)
            rho_sat = (1.0 - porosity) * rho_min + porosity * rho_fl
            Vp, Vs = rp.acoustic_velocities(K_sat, G_sat, rho_sat)

            if Vp_baseline is None:
                Vp_baseline, Vs_baseline = Vp, Vs

            result["co2_saturation"].append(round(s, 4))
            result["Vp_kms"].append(round(Vp, 4))
            result["Vs_kms"].append(round(Vs, 4))
            result["rho_gcc"].append(round(rho_sat, 4))
            result["acoustic_impedance_Vp"].append(round(Vp * rho_sat, 4))
            result["Vp_Vs_ratio"].append(round(Vp / Vs, 4) if Vs > 0 else None)
            result["delta_Vp_pct"].append(round((Vp - Vp_baseline) / Vp_baseline * 100, 4))
            result["delta_Vs_pct"].append(
                round((Vs - Vs_baseline) / Vs_baseline * 100, 4) if Vs_baseline > 0 else None
            )

        return result
    except Exception as e:
        return {"error": str(e)}


@cl.step(type="tool", name="Rock Physics: 4D Contrast")
async def carbonate_rock_4d_contrast(
    mineralogy_wt_json: str,
    aspect_ratio: float,
    temperature_c: float,
    pressure_mpa: float,
    salinity_ppm: float,
    baseline_porosity: float,
    baseline_co2_saturation: float,
    monitor_porosity: float,
    monitor_co2_saturation: float,
) -> dict:
    """Compute 4D seismic contrast between a baseline and a monitor state.

    Returns absolute and percentage changes in Vp, Vs, density, and acoustic
    impedance. Porosity may differ between states to represent dissolution or
    precipitation effects from CO2-rock reactions.

    IMPORTANT: The seismic CO2 response is nonunique — a small free-gas
    saturation produces nearly the same Vp drop as a large one. Always
    interpret ΔVp together with ΔVs and ΔIp.

    Args:
        mineralogy_wt_json: JSON object string of mineral weight fractions.
        aspect_ratio: Pore/crack aspect ratio [0, 1].
        temperature_c: Temperature in °C.
        pressure_mpa: Pressure in MPa.
        salinity_ppm: Salinity in ppm by weight.
        baseline_porosity: Porosity at baseline state [0, 1].
        baseline_co2_saturation: CO2 saturation at baseline [0, 1].
            Typically 0 (brine-saturated, pre-injection).
        monitor_porosity: Porosity at monitor state [0, 1].
        monitor_co2_saturation: CO2 saturation at monitor state [0, 1].

    Returns:
        dict with "baseline" and "monitor" sub-dicts (each with full seismic
        state) and a "contrast" sub-dict with delta_Vp_kms, delta_Vs_kms,
        delta_rho_gcc, delta_Ip, delta_Vp_pct, delta_Vs_pct, delta_Ip_pct,
        Vp_Vs_ratio_baseline, Vp_Vs_ratio_monitor.
    """
    try:
        wt_fracs = _parse_mineralogy(mineralogy_wt_json)

        baseline = rp.seismic_state(
            wt_fracs, baseline_porosity, aspect_ratio,
            temperature_c, pressure_mpa, salinity_ppm, baseline_co2_saturation,
        )
        monitor = rp.seismic_state(
            wt_fracs, monitor_porosity, aspect_ratio,
            temperature_c, pressure_mpa, salinity_ppm, monitor_co2_saturation,
        )

        dVp  = monitor["Vp_kms"]  - baseline["Vp_kms"]
        dVs  = monitor["Vs_kms"]  - baseline["Vs_kms"]
        drho = monitor["rho_gcc"] - baseline["rho_gcc"]
        dIp  = monitor["acoustic_impedance_Vp"] - baseline["acoustic_impedance_Vp"]

        contrast = {
            "delta_Vp_kms":          round(dVp, 4),
            "delta_Vs_kms":          round(dVs, 4),
            "delta_rho_gcc":         round(drho, 4),
            "delta_Ip":              round(dIp, 4),
            "delta_Vp_pct":          round(dVp  / baseline["Vp_kms"]  * 100, 4) if baseline["Vp_kms"]  else None,
            "delta_Vs_pct":          round(dVs  / baseline["Vs_kms"]  * 100, 4) if baseline["Vs_kms"]  else None,
            "delta_Ip_pct":          round(dIp  / baseline["acoustic_impedance_Vp"] * 100, 4) if baseline["acoustic_impedance_Vp"] else None,
            "Vp_Vs_ratio_baseline":  baseline["Vp_Vs_ratio"],
            "Vp_Vs_ratio_monitor":   monitor["Vp_Vs_ratio"],
        }

        return {"baseline": baseline, "monitor": monitor, "contrast": contrast}
    except Exception as e:
        return {"error": str(e)}


@cl.step(type="tool", name="Bridge: Moles → Rock Physics")
async def phreeqc_moles_to_rock_physics_inputs(
    mineral_moles_json: str,
    bulk_volume_cm3: float = 100.0,
) -> dict:
    """Convert PHREEQC mineral mole output to rock physics inputs.

    Use this after a CO2-brine-rock simulation to feed geochemical results
    into the carbonate rock physics tools. PHREEQC returns mole changes per
    mineral; this tool converts the post-reaction mineral assemblage to the
    weight fractions and porosity that carbonate_rock_seismic_state requires.

    Args:
        mineral_moles_json: JSON object string of {mineral_name: moles}.
            Use absolute moles after reaction (initial + delta from
            co2_brine_rock_fixed), not the delta alone.
            Mineral names must be lowercase (e.g. "calcite", "quartz").
        bulk_volume_cm3: Total bulk volume in cm³.
            Default 100 cm³ matches the PHREEQC template reference volume.

    Returns:
        dict with "mineralogy_wt_json" (ready to pass to
        carbonate_rock_seismic_state) and "porosity" (float).
    """
    try:
        moles = {k: float(v) for k, v in json.loads(mineral_moles_json).items()}
        wt_fracs = rp.moles_to_wt_fractions(moles)
        porosity = rp.moles_to_porosity(moles, bulk_volume_cm3)
        return {
            "mineralogy_wt_json": json.dumps({k: round(v, 6) for k, v in wt_fracs.items()}),
            "porosity": round(porosity, 6),
        }
    except Exception as e:
        return {"error": str(e)}
