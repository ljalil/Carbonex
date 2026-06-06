"""
Carbonate rock physics model for CO2 storage seismic feasibility.

Workflow
--------
1. VRH average        : weight fractions → effective mineral moduli (K, G, ρ)
2. Batzle-Wang        : T, P, salinity, S_CO2 → fluid density and bulk modulus
3. Berryman DEM       : mineral moduli + aspect ratio → dry-frame K_dry, G_dry vs porosity
4. Gassmann           : K_dry, G_dry, K_mineral, K_fluid, φ → K_sat, G_sat
5. Velocities         : K_sat, G_sat, ρ_sat → Vp, Vs

All functions are pure (no side effects, no I/O). They return plain Python
floats, lists, or dicts — always JSON-serialisable — so they can be composed
in agent tool wrappers without adaptation.

Unit conventions (enforced at every function boundary)
-------------------------------------------------------
temperature  : °C
pressure     : MPa
moduli       : GPa
density      : g/cm³
velocity     : km/s
salinity     : ppm by weight  (e.g. 35 000 for seawater)
porosity     : fraction  [0, 1]
aspect ratio : fraction  [0, 1]   (0.01 = crack-like, 1.0 = spherical)
saturation   : fraction  [0, 1]

References
----------
Mavko, Mukerji & Dvorkin — The Rock Physics Handbook (2009)
Avseth, Mukerji & Mavko — Quantitative Seismic Interpretation (2010)
Batzle & Wang (1992) — Seismic properties of pore fluids, Geophysics 57(11)
Berryman (1992) — Single-scattering approximations for coefficients in
    Biot's equations of poroelasticity, J. Acoust. Soc. Am.
"""

import numpy as np
from rockphypy import EM, BW, Fluid, utils


# ---------------------------------------------------------------------------
# Mineral property tables
# ---------------------------------------------------------------------------
# Density = molar_mass / molar_volume (both sourced from the same reference).
# Placeholder shear moduli (illite, chlorite) are marked in comments.

_MOLAR_MASS = {   # g/mol
    "calcite":    100.09,
    "dolomite":   184.40,
    "siderite":   115.85,
    "quartz":      60.084,
    "k-feldspar": 278.33,
    "albite":     262.22,
    "smectite":   366.62,
    "kaolinite":  258.16,
    "illite":     343.47,
    "chlorite":   555.7973,
    "pyrite":     119.98,
    "anhydrite":  136.14,
}

_MOLAR_VOLUME = {  # cm³/mol
    "calcite":    36.9,
    "dolomite":   64.5,
    "siderite":   29.2,
    "quartz":     22.67,
    "k-feldspar": 108.15,
    "albite":     101.31,
    "smectite":   156.16,
    "kaolinite":  99.35,
    "illite":     141.48,
    "chlorite":   207.11,
    "pyrite":     23.48,
    "anhydrite":  46.1,
}

MINERAL_K = {   # bulk modulus, GPa
    "calcite":    73.3,
    "dolomite":   94.9,
    "siderite":   123.7,
    "quartz":     38.0,
    "k-feldspar": 37.5,   # orthoclase
    "albite":     56.9,
    "smectite":   22.9,   # Na-montmorillonite
    "kaolinite":  44.001,
    "illite":     11.70,
    "chlorite":   95.30,
    "pyrite":     158.0,
    "anhydrite":  54.9,
}

MINERAL_G = {   # shear modulus, GPa
    "calcite":    32.0,
    "dolomite":   45.7,
    "siderite":   59.47,
    "quartz":     44.8,
    "k-feldspar": 15.0,   # orthoclase
    "albite":     28.6,
    "smectite":   10.6,   # Na-montmorillonite
    "kaolinite":  22.552,
    "illite":     11.0,   # placeholder
    "chlorite":   11.0,   # placeholder
    "pyrite":     132.5,
    "anhydrite":  29.3,
}

MINERAL_RHO = {  # density, g/cm³  (molar_mass / molar_volume)
    m: _MOLAR_MASS[m] / _MOLAR_VOLUME[m] for m in _MOLAR_MASS
}

VALID_MINERALS = set(MINERAL_K)

# Molar data needed for PHREEQC bridge (moles → porosity / wt fractions)
_PHREEQC_BRIDGE_MINERALS = {
    # Maps lowercase PHREEQC mineral names to table keys above.
    # Add entries here when new PHREEQC minerals are introduced.
    "calcite":    "calcite",
    "dolomite":   "dolomite",
    "siderite":   "siderite",
    "quartz":     "quartz",
    "k-feldspar": "k-feldspar",
    "albite":     "albite",
    "kaolinite":  "kaolinite",
    "illite":     "illite",
    "chlorite":   "chlorite",
    "pyrite":     "pyrite",
    "anhydrite":  "anhydrite",
}

_BULK_VOLUME_CM3 = 100.0  # reference bulk volume used in PHREEQC templates


# ---------------------------------------------------------------------------
# Step 1 — VRH mineral average
# ---------------------------------------------------------------------------

def wt_to_vol_fractions(wt_fracs: dict) -> dict:
    """Convert weight fractions to volume fractions using mineral densities.

    Parameters
    ----------
    wt_fracs : dict
        {mineral_name: weight_fraction}. Fractions need not sum to 1.

    Returns
    -------
    dict  {mineral_name: volume_fraction}  — sums to 1.
    """
    vol = {m: wt_fracs[m] / MINERAL_RHO[m] for m in wt_fracs if wt_fracs[m] > 0}
    total = sum(vol.values())
    if total == 0:
        raise ValueError("All mineral weight fractions are zero.")
    return {m: v / total for m, v in vol.items()}


def effective_mineral_moduli(wt_fracs: dict) -> tuple:
    """Voigt-Reuss-Hill average over mineral end-members.

    Parameters
    ----------
    wt_fracs : dict
        {mineral_name: weight_fraction}. Valid names: calcite, dolomite,
        siderite, quartz, k-feldspar, albite, smectite, kaolinite, illite,
        chlorite, pyrite, anhydrite.

    Returns
    -------
    K_min   : float  GPa  — Hill average bulk modulus
    G_min   : float  GPa  — Hill average shear modulus
    rho_min : float  g/cm³ — Voigt (linear) average density
    """
    vol = wt_to_vol_fractions(wt_fracs)
    minerals = list(vol.keys())
    vf      = [vol[m] for m in minerals]
    K_list  = [MINERAL_K[m] for m in minerals]
    G_list  = [MINERAL_G[m] for m in minerals]
    rho_list = [MINERAL_RHO[m] for m in minerals]

    K_min   = float(EM.VRH(vf, K_list)[-1])    # Hill average
    G_min   = float(EM.VRH(vf, G_list)[-1])    # Hill average
    rho_min = float(EM.VRH(vf, rho_list)[0])   # Voigt average (correct for density)
    return K_min, G_min, rho_min


# ---------------------------------------------------------------------------
# Step 2 — Batzle-Wang fluid mixing
# ---------------------------------------------------------------------------

def fluid_properties(
    temperature_c: float,
    pressure_mpa: float,
    salinity_ppm: float,
    co2_saturation: float,
) -> tuple:
    """Batzle-Wang properties for a CO2-brine mixture.

    Parameters
    ----------
    temperature_c  : float  °C
    pressure_mpa   : float  MPa
    salinity_ppm   : float  ppm by weight  (35 000 ≈ seawater)
    co2_saturation : float  CO2 fraction in pore space  [0, 1]

    Returns
    -------
    rho_fl : float  g/cm³
    K_fl   : float  GPa
    """
    salinity_frac = salinity_ppm / 1e6
    rho_fl, K_fl = BW.co2_brine(temperature_c, pressure_mpa, salinity_frac, co2_saturation)
    return float(np.atleast_1d(rho_fl)[0]), float(np.atleast_1d(K_fl)[0])


# ---------------------------------------------------------------------------
# Step 3 — Berryman DEM dry frame
# ---------------------------------------------------------------------------

def dem_dry_frame(
    K_host: float,
    G_host: float,
    aspect_ratio: float,
    max_porosity: float,
    K_inc: float = 0.0,
    G_inc: float = 0.0,
) -> tuple:
    """Berryman DEM: integrate inclusions into host from φ = 0 to max_porosity.

    Typical use: K_inc = G_inc = 0 for dry pores (air/vacuum inclusions).
    Pass non-zero K_inc, G_inc to embed a fluid-saturated or mineral inclusion.

    Parameters
    ----------
    K_host, G_host : float  GPa  host (grain) moduli
    aspect_ratio   : float       pore/crack aspect ratio  [0, 1]
    max_porosity   : float       upper integration limit
    K_inc, G_inc   : float  GPa  inclusion moduli  (default: 0 = dry pores)

    Returns
    -------
    K_dry_arr : np.ndarray  GPa  bulk moduli along porosity path
    G_dry_arr : np.ndarray  GPa  shear moduli along porosity path
    phi_arr   : np.ndarray       porosity values
    """
    K_dry_arr, G_dry_arr, phi_arr = EM.Berryman_DEM(
        K_host, G_host, K_inc, G_inc, aspect_ratio, max_porosity
    )
    return K_dry_arr, G_dry_arr, phi_arr


# ---------------------------------------------------------------------------
# Step 4 — Gassmann fluid substitution
# ---------------------------------------------------------------------------

def gassmann(
    K_dry: float,
    G_dry: float,
    K_mineral: float,
    K_fluid: float,
    porosity: float,
) -> tuple:
    """Gassmann fluid substitution.

    Parameters
    ----------
    K_dry     : float  GPa  dry-frame bulk modulus
    G_dry     : float  GPa  dry-frame shear modulus
    K_mineral : float  GPa  mineral grain bulk modulus
    K_fluid   : float  GPa  pore-fluid bulk modulus
    porosity  : float       [0, 1]

    Returns
    -------
    K_sat : float  GPa
    G_sat : float  GPa  (equal to G_dry; returned for API symmetry)
    """
    K_sat, G_sat = Fluid.Gassmann(K_dry, G_dry, K_mineral, K_fluid, porosity)
    return float(K_sat), float(G_sat)


# ---------------------------------------------------------------------------
# Step 5 — Seismic velocities
# ---------------------------------------------------------------------------

def acoustic_velocities(K_sat: float, G_sat: float, rho_sat: float) -> tuple:
    """Compute Vp and Vs from saturated moduli and bulk density.

    Parameters
    ----------
    K_sat   : float  GPa
    G_sat   : float  GPa
    rho_sat : float  g/cm³

    Returns
    -------
    Vp : float  km/s
    Vs : float  km/s
    """
    # utils.V returns m/s; divide by 1000 to yield km/s.
    # With rho in g/cm³, impedance = Vp_kms * rho_gcc is in MRayl (= km/s · g/cm³).
    Vp, Vs = utils.V(K_sat, G_sat, rho_sat)
    return float(Vp) / 1000.0, float(Vs) / 1000.0


# ---------------------------------------------------------------------------
# Composed forward model
# ---------------------------------------------------------------------------

def seismic_state(
    wt_fracs: dict,
    porosity: float,
    aspect_ratio: float,
    temperature_c: float,
    pressure_mpa: float,
    salinity_ppm: float,
    co2_saturation: float,
) -> dict:
    """Full forward model: mineralogy + reservoir conditions → seismic properties.

    Pipeline: VRH → Batzle-Wang → Berryman DEM → Gassmann → velocities.

    Parameters
    ----------
    wt_fracs       : dict   {mineral_name: weight_fraction}
    porosity       : float  [0, 1]
    aspect_ratio   : float  pore aspect ratio [0, 1]
    temperature_c  : float  °C
    pressure_mpa   : float  MPa
    salinity_ppm   : float  ppm by weight
    co2_saturation : float  CO2 fraction in pore space [0, 1]

    Returns
    -------
    dict with keys:
        Vp_kms, Vs_kms, rho_gcc,
        acoustic_impedance_Vp, acoustic_impedance_Vs, Vp_Vs_ratio,
        K_sat_GPa, G_sat_GPa,
        K_mineral_GPa, G_mineral_GPa, rho_mineral_gcc,
        rho_fluid_gcc, K_fluid_GPa
    """
    K_min, G_min, rho_min = effective_mineral_moduli(wt_fracs)
    rho_fl, K_fl = fluid_properties(temperature_c, pressure_mpa, salinity_ppm, co2_saturation)

    # DEM must integrate at least slightly past the target porosity
    max_porosity = max(porosity + 0.02, 0.05)
    K_dry_arr, G_dry_arr, phi_arr = dem_dry_frame(K_min, G_min, aspect_ratio, max_porosity)

    K_dry = float(np.interp(porosity, phi_arr, K_dry_arr))
    G_dry = float(np.interp(porosity, phi_arr, G_dry_arr))

    K_sat, G_sat = gassmann(K_dry, G_dry, K_min, K_fl, porosity)
    rho_sat = (1.0 - porosity) * rho_min + porosity * rho_fl

    Vp, Vs = acoustic_velocities(K_sat, G_sat, rho_sat)

    return {
        "Vp_kms":                  round(Vp, 4),
        "Vs_kms":                  round(Vs, 4),
        "rho_gcc":                 round(rho_sat, 4),
        "acoustic_impedance_Vp":   round(Vp * rho_sat, 4),
        "acoustic_impedance_Vs":   round(Vs * rho_sat, 4),
        "Vp_Vs_ratio":             round(Vp / Vs, 4) if Vs > 0 else None,
        "K_sat_GPa":               round(K_sat, 4),
        "G_sat_GPa":               round(G_sat, 4),
        "K_mineral_GPa":           round(K_min, 4),
        "G_mineral_GPa":           round(G_min, 4),
        "rho_mineral_gcc":         round(rho_min, 4),
        "rho_fluid_gcc":           round(rho_fl, 4),
        "K_fluid_GPa":             round(K_fl, 4),
    }


# ---------------------------------------------------------------------------
# PHREEQC bridge utilities
# ---------------------------------------------------------------------------
# Convert PHREEQC mineral-mole output to rock-physics inputs.
# These functions are the join between the geochemistry and rock-physics
# modules.  The reference bulk volume (100 cm³) must match the PHREEQC
# templates in phreeqc_programs/.

def moles_to_wt_fractions(moles: dict) -> dict:
    """Convert mineral mole amounts to weight fractions.

    Parameters
    ----------
    moles : dict
        {mineral_name: moles} as returned by the PHREEQC geochemistry tools.
        Only minerals present in VALID_MINERALS are used; others are ignored.

    Returns
    -------
    dict  {mineral_name: weight_fraction}
    """
    known = {m: moles[m] for m in moles if m in _PHREEQC_BRIDGE_MINERALS and moles[m] > 0}
    if not known:
        raise ValueError("No recognised minerals with positive moles found.")
    masses = {m: known[m] * _MOLAR_MASS[_PHREEQC_BRIDGE_MINERALS[m]] for m in known}
    total = sum(masses.values())
    return {m: masses[m] / total for m in masses}


def moles_to_porosity(moles: dict, bulk_volume_cm3: float = _BULK_VOLUME_CM3) -> float:
    """Compute porosity from mineral moles and bulk volume.

    Parameters
    ----------
    moles           : dict   {mineral_name: moles}
    bulk_volume_cm3 : float  bulk volume in cm³
                             (default: 100 cm³, matching PHREEQC templates)

    Returns
    -------
    porosity : float  [0, 1]
    """
    solid_volume = sum(
        _MOLAR_VOLUME[_PHREEQC_BRIDGE_MINERALS[m]] * moles[m]
        for m in moles
        if m in _PHREEQC_BRIDGE_MINERALS and moles[m] > 0
    )
    return float(np.clip((bulk_volume_cm3 - solid_volume) / bulk_volume_cm3, 0.0, 1.0))


def wt_fractions_to_moles(
    wt_fracs: dict,
    porosity: float,
    bulk_volume_cm3: float = _BULK_VOLUME_CM3,
) -> dict:
    """Convert mineral weight fractions + porosity to moles per bulk volume.

    Inverse of moles_to_wt_fractions / moles_to_porosity. The solid volume
    is bulk_volume_cm3 × (1 − porosity); weight fractions partition that mass
    among the minerals.

    Parameters
    ----------
    wt_fracs        : dict   {mineral_name: weight_fraction}  (lowercase names)
    porosity        : float  [0, 1]
    bulk_volume_cm3 : float  bulk volume reference in cm³ (default 100 cm³)

    Returns
    -------
    dict  {mineral_name: moles}
    """
    known = {
        m: wt_fracs[m]
        for m in wt_fracs
        if m in _PHREEQC_BRIDGE_MINERALS and wt_fracs[m] > 0
    }
    if not known:
        raise ValueError("No recognised minerals with positive weight fractions.")
    solid_volume = bulk_volume_cm3 * (1.0 - porosity)
    # Total solid mass: V_solid = M_total × Σ(wt_i / rho_i)
    specific_vol_sum = sum(known[m] / MINERAL_RHO[_PHREEQC_BRIDGE_MINERALS[m]] for m in known)
    total_mass = solid_volume / specific_vol_sum  # g
    return {
        m: total_mass * known[m] / _MOLAR_MASS[_PHREEQC_BRIDGE_MINERALS[m]]
        for m in known
    }
