"""
Agent tool wrappers — CO2 geochemistry.

Wraps geochemistry.co2_brine (PHREEQC + Duan-Sun, no rock) and
geochemistry.co2_brine_rock (PHREEQC with minerals).

Design notes
------------
- Ions and minerals cross the tool boundary as JSON strings so the
  AFC-generated schema stays unambiguous (arbitrary-keyed dicts have no
  clean JSON schema representation).
- All inputs are validated against explicit allow-lists; unknown values
  return a structured error dict rather than raising or defaulting silently.
- Every function returns a JSON-serialisable dict — AFC requirement.

Units at the tool boundary
--------------------------
temperature : Kelvin
pressure    : MPa
molalities  : mol/kg water
"""

import json
from geochemistry import co2_brine as cb
from geochemistry import co2_brine_rock as cbr
from rock_physics.carbonate_model import VALID_MINERALS
import chainlit as cl


_VALID_BRINE_MODELS = {
    "phreeqc_phreeqc",
    "phreeqc_pitzer",
    "phreeqc_pitzer_mod",
    "duan_sun_2006",
    "carbonex",
}

_VALID_ROCK_MODELS = {"phreeqc", "pitzer"}


def _parse_ions(ion_molalities_json: str) -> dict:
    if not ion_molalities_json or not ion_molalities_json.strip():
        return {}
    ions = json.loads(ion_molalities_json)
    return {k: float(v) for k, v in ions.items()}


def _parse_minerals(mineral_moles_json: str) -> dict:
    if not mineral_moles_json or not mineral_moles_json.strip():
        return {}
    minerals = json.loads(mineral_moles_json)
    return {k: float(v) for k, v in minerals.items()}


# ---------------------------------------------------------------------------
# CO2-brine (no rock)
# ---------------------------------------------------------------------------

@cl.step(type="tool", name="Brine: CO2 Solubility")
async def co2_brine_solubility_fixed(
    temperature_k: float,
    pressure_mpa: float,
    ion_molalities_json: str,
    model: str = "phreeqc_phreeqc",
) -> dict:
    """Compute dissolved CO2 in brine at a single fixed temperature and pressure.

    Use this for the CO2-brine system (no rock/minerals) when the user wants
    the solubility at one specific state point.

    Args:
        temperature_k: Temperature in Kelvin.
        pressure_mpa: Pressure in MPa.
        ion_molalities_json: JSON object string mapping ion name to molality
            (mol/kg water). Allowed keys: "Na+", "Cl-", "Mg+2", "Ca+2",
            "K+", "SO4-2", "HCO3-", "CO3-2".
            Example: '{"Na+": 1.0, "Cl-": 1.0}'. Pass '{}' for pure water.
        model: Solubility model — one of "phreeqc_phreeqc", "phreeqc_pitzer",
            "phreeqc_pitzer_mod", "duan_sun_2006", "carbonex".

    Returns:
        dict with key "dissolved_co2_mol_per_kg" (float).
    """
    if model not in _VALID_BRINE_MODELS:
        return {"error": f"Unknown model '{model}'. Valid: {sorted(_VALID_BRINE_MODELS)}"}
    species = _parse_ions(ion_molalities_json)
    co2 = cb.simulate_co2_brine_fixed(temperature_k, pressure_mpa, species, model)
    return {"dissolved_co2_mol_per_kg": float(co2)}


@cl.step(type="tool", name="Brine: Solubility vs P")
async def co2_brine_solubility_vs_pressure(
    temperature_k: float,
    ion_molalities_json: str,
    model: str = "phreeqc_phreeqc",
) -> dict:
    """Compute dissolved CO2 in brine across a range of pressures at fixed temperature.

    CO2-brine system (no rock). Returns a curve of solubility vs pressure.

    Args:
        temperature_k: Fixed temperature in Kelvin.
        ion_molalities_json: JSON object string of ion molalities (mol/kg).
            See co2_brine_solubility_fixed for allowed keys. '{}' for pure water.
        model: One of "phreeqc_phreeqc", "phreeqc_pitzer", "phreeqc_pitzer_mod",
            "duan_sun_2006", "carbonex".

    Returns:
        dict with "Pressure (MPa)" (list) and "Dissolved CO2 (mol/kg)" (list).
    """
    if model not in _VALID_BRINE_MODELS:
        return {"error": f"Unknown model '{model}'. Valid: {sorted(_VALID_BRINE_MODELS)}"}
    ions = _parse_ions(ion_molalities_json)
    return cb.simulate_co2_brine_var_p(temperature_k, ions, model)


@cl.step(type="tool", name="Brine: Solubility vs T")
async def co2_brine_solubility_vs_temperature(
    pressure_mpa: float,
    ion_molalities_json: str,
    model: str = "phreeqc_phreeqc",
) -> dict:
    """Compute dissolved CO2 in brine across a range of temperatures at fixed pressure.

    CO2-brine system (no rock). Returns a curve of solubility vs temperature.

    Args:
        pressure_mpa: Fixed pressure in MPa.
        ion_molalities_json: JSON object string of ion molalities (mol/kg).
        model: One of "phreeqc_phreeqc", "phreeqc_pitzer", "phreeqc_pitzer_mod",
            "duan_sun_2006", "carbonex".

    Returns:
        dict with "Temperature (K)" (list) and "Dissolved CO2 (mol/kg)" (list).
    """
    if model not in _VALID_BRINE_MODELS:
        return {"error": f"Unknown model '{model}'. Valid: {sorted(_VALID_BRINE_MODELS)}"}
    ions = _parse_ions(ion_molalities_json)
    return cb.simulate_co2_brine_var_t(pressure_mpa, ions, model)


@cl.step(type="tool", name="Brine: Solution Properties")
async def co2_brine_solution_properties(
    temperature_k: float,
    pressure_mpa: float,
    ion_molalities_json: str,
) -> dict:
    """Get detailed solution properties of a CO2-saturated brine at one state point.

    CO2-brine system (no rock). Uses the PHREEQC Pitzer database. Returns
    per-ion activities and molar volumes plus bulk solution properties.

    Args:
        temperature_k: Temperature in Kelvin.
        pressure_mpa: Pressure in MPa.
        ion_molalities_json: JSON object string of ion molalities (mol/kg).

    Returns:
        dict with keys: "species" (list of {species, activity, molar_volume}),
        "density", "ionic_strength", "pH", "osmotic_coefficient",
        "partial_pressure_co2", "fugacity_co2".
    """
    species = _parse_ions(ion_molalities_json)
    (species_data, density, ionic_strength, pH, osmotic,
     pr_co2, phi_co2) = cb.simulate_co2_brine_solution_properties(
        temperature_k, pressure_mpa, species
    )
    return {
        "species": species_data,
        "density": density,
        "ionic_strength": ionic_strength,
        "pH": pH,
        "osmotic_coefficient": osmotic,
        "partial_pressure_co2": pr_co2,
        "fugacity_co2": phi_co2,
    }


# ---------------------------------------------------------------------------
# CO2-brine-rock (with minerals)
# ---------------------------------------------------------------------------

@cl.step(type="tool", name="Brine+Rock: CO2 Solubility")
async def co2_brine_rock_fixed(
    temperature_k: float,
    pressure_mpa: float,
    ion_molalities_json: str,
    mineral_moles_json: str,
    model: str = "phreeqc",
) -> dict:
    """Compute CO2-brine-rock interaction at a single fixed state (with minerals).

    Use this when the user specifies rock mineralogy. Returns dissolved CO2
    and the change in moles of each equilibrium mineral (mineral trapping).

    Args:
        temperature_k: Temperature in Kelvin.
        pressure_mpa: Pressure in MPa.
        ion_molalities_json: JSON object string of ion molalities (mol/kg).
        mineral_moles_json: JSON object string mapping mineral name to initial
            moles. Allowed keys: "Quartz", "Calcite", "Siderite", "Dolomite",
            "Illite", "Kaolinite", "K-feldspar", "Albite", "Chlorite", "Pyrite".
            Example: '{"Calcite": 1.0, "Quartz": 5.0}'.
        model: PHREEQC database — "phreeqc" or "pitzer".

    Returns:
        dict with "trapped_co2" (float) and "mineral_equi" (dict of mineral →
        delta moles; negative = dissolution, positive = precipitation).
    """
    if model not in _VALID_ROCK_MODELS:
        return {"error": f"Unknown model '{model}'. Valid: {sorted(_VALID_ROCK_MODELS)}"}
    species = _parse_ions(ion_molalities_json)
    minerals = _parse_minerals(mineral_moles_json)
    return cbr.simulate_co2_brine_rock_fixed(
        temperature_k, pressure_mpa, species, minerals, model
    )


@cl.step(type="tool", name="Brine+Rock: Solubility vs P")
async def co2_brine_rock_vs_pressure(
    temperature_k: float,
    ion_molalities_json: str,
    mineral_moles_json: str,
    model: str = "phreeqc",
) -> dict:
    """Compute CO2-brine-rock dissolved CO2 across a pressure range at fixed temperature.

    Args:
        temperature_k: Fixed temperature in Kelvin.
        ion_molalities_json: JSON object string of ion molalities (mol/kg).
        mineral_moles_json: JSON object string of mineral initial moles.
        model: PHREEQC database — "phreeqc" or "pitzer".

    Returns:
        dict with "Pressure (MPa)" (list) and "Dissolved CO2 (mol/kg)" (list).
    """
    if model not in _VALID_ROCK_MODELS:
        return {"error": f"Unknown model '{model}'. Valid: {sorted(_VALID_ROCK_MODELS)}"}
    species = _parse_ions(ion_molalities_json)
    minerals = _parse_minerals(mineral_moles_json)
    return cbr.simulate_co2_brine_rock_var_p(temperature_k, species, minerals, model)


@cl.step(type="tool", name="Brine+Rock: Solubility vs T")
async def co2_brine_rock_vs_temperature(
    pressure_mpa: float,
    ion_molalities_json: str,
    mineral_moles_json: str,
    model: str = "phreeqc",
) -> dict:
    """Compute CO2-brine-rock dissolved CO2 across a temperature range at fixed pressure.

    Args:
        pressure_mpa: Fixed pressure in MPa.
        ion_molalities_json: JSON object string of ion molalities (mol/kg).
        mineral_moles_json: JSON object string of mineral initial moles.
        model: PHREEQC database — "phreeqc" or "pitzer".

    Returns:
        dict with "Temperature (K)" (list) and "Dissolved CO2 (mol/kg)" (list).
    """
    if model not in _VALID_ROCK_MODELS:
        return {"error": f"Unknown model '{model}'. Valid: {sorted(_VALID_ROCK_MODELS)}"}
    species = _parse_ions(ion_molalities_json)
    minerals = _parse_minerals(mineral_moles_json)
    return cbr.simulate_co2_brine_rock_var_t(pressure_mpa, species, minerals, model)


# ---------------------------------------------------------------------------
# Mineral equilibrium with explicit porosity tracking
# ---------------------------------------------------------------------------

@cl.step(type="tool", name="Brine+Rock: Mineralogy & Porosity")
async def compute_equilibrium_mineralogy_and_porosity(
    temperature_k: float,
    pressure_mpa: float,
    mineralogy_wt_json: str,
    porosity: float,
    ion_molalities_json: str,
    with_co2: bool = True,
    model: str = "phreeqc",
) -> dict:
    """Compute post-reaction mineralogy and porosity change using PHREEQC equilibrium.

    This is the correct tool when the user provides reservoir mineralogy as
    weight fractions and wants to know how CO2 injection (or brine-rock
    equilibration without CO2) changes the mineral assemblage, porosity,
    and solution chemistry.

    Unlike co2_brine_rock_fixed (which returns mole DELTAS), this tool:
    - Accepts weight fractions + porosity as the natural reservoir description.
    - Returns ABSOLUTE post-reaction moles, updated weight fractions, and the
      new porosity computed directly from the remaining mineral volumes.
    - Calculates porosity_change = porosity_post − porosity_initial.

    The returned "mineralogy_wt_post" and "porosity_post" can be passed
    directly to carbonate_rock_seismic_state to compute post-injection
    seismic properties.

    Workflow for 4D seismic with geochemical porosity change:
        1. Call with_co2=False → pre-injection equilibrium state.
        2. Call with_co2=True  → post-injection state (start from step-1 output
           if the initial brine may not be at equilibrium with the rock).
        3. Pass step-2 "mineralogy_wt_post" + "porosity_post" to
           carbonate_rock_seismic_state for post-injection Vp / Vs.

    Args:
        temperature_k: Temperature in Kelvin.
        pressure_mpa: Pressure in MPa.
        mineralogy_wt_json: JSON object string of mineral weight fractions
            (lowercase keys). Valid keys: calcite, dolomite, siderite, quartz,
            k-feldspar, albite, kaolinite, illite, chlorite, pyrite, anhydrite.
            Fractions are normalised internally and need not sum to 1.
            Example: '{"calcite": 0.75, "quartz": 0.10, "dolomite": 0.05,
                       "kaolinite": 0.05, "anhydrite": 0.05}'.
        porosity: Initial pore-volume fraction [0, 1].
        ion_molalities_json: JSON object string of ion molalities (mol/kg).
            Allowed keys: "Na+", "Cl-", "Mg+2", "Ca+2", "K+", "SO4-2",
            "HCO3-", "CO3-2". Example: '{"Na+": 1.0, "Cl-": 1.0}'.
            Pass '{}' for fresh water.
        with_co2: True (default) → include a CO2 gas phase at reservoir
            pressure (post-injection scenario). False → no CO2 gas phase
            (pre-injection baseline equilibration).
        model: PHREEQC database — "phreeqc" or "pitzer".

    Returns:
        dict with keys:
            mineral_moles_initial   : {mineral: moles} before reaction
            mineral_moles_post      : {mineral: moles} remaining after reaction
            mineralogy_wt_post      : {mineral: wt_fraction} after reaction
                                      (ready for carbonate_rock_seismic_state)
            porosity_initial        : float
            porosity_post           : float
            porosity_change         : float (positive = pores opened by dissolution)
            trapped_co2_mol_per_kg  : dissolved C(4) (mol/kg); 0 if with_co2=False
            pH_post                 : float
            solution_density_gcc    : float (g/cm³)
            salinity_ppm            : float
            ion_totals              : {Na, Cl, Mg, Ca, K, SO4, DIC} in mol/kg
    """
    if model not in _VALID_ROCK_MODELS:
        return {"error": f"Unknown model '{model}'. Valid: {sorted(_VALID_ROCK_MODELS)}"}
    try:
        wt_fracs = json.loads(mineralogy_wt_json)
        wt_fracs = {k: float(v) for k, v in wt_fracs.items()}
        unknown = set(wt_fracs) - VALID_MINERALS
        if unknown:
            return {"error": f"Unknown minerals: {sorted(unknown)}. Valid: {sorted(VALID_MINERALS)}"}
        species = _parse_ions(ion_molalities_json)
        return cbr.simulate_mineral_equilibrium(
            temperature_k, pressure_mpa, wt_fracs, porosity, species,
            with_co2=with_co2, model=model,
        )
    except Exception as e:
        return {"error": str(e)}
