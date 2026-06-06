import os
import math
import uuid
import pandas as pd
import subprocess
import csv
import sys
import tempfile

from rock_physics.carbonate_model import wt_fractions_to_moles, moles_to_porosity, moles_to_wt_fractions

def simulate_co2_brine_rock_solution_properties(temperature, pressure, species, minerals):
    """
    Run PHREEQC simulation for brine-rock interaction solution properties only.
    Similar to simulate_co2_brine_solution_properties but includes mineral interactions.
    
    Parameters:
        temperature: Temperature in Kelvin
        pressure: Pressure in MPa
        species: Dictionary of ion molalities
        minerals: Dictionary of mineral names and initial moles
        
    Returns:
        tuple: (species_data, density, ionic_strength, pH, osmotic_coefficient, partial_pressure_co2, fugacity_co2)
    """
    temp_files_path = tempfile.gettempdir()
    Na = species.get("Na+", 0)
    Cl = species.get("Cl-", 0)
    Mg = species.get("Mg+2", 0)
    Ca = species.get("Ca+2", 0)
    K = species.get("K+", 0)
    SO4 = species.get("SO4-2", 0)
    HCO3 = species.get("HCO3-", 0)
    CO3 = species.get("CO3-2", 0)

    pressure_atm = pressure * 9.86923
    temperature_c = temperature - 273.15
    p_co2 = pressure_atm * 0.95
    p_h2o = pressure_atm * 0.05

    state_out_file = os.path.join(temp_files_path, "co2_brine_rock_solution_properties.tsv")

    template_path = os.path.join(os.path.dirname(__file__), "phreeqc_templates", "co2_brine_rock_template.pqi")
    with open(template_path, "r") as template_file:
        phreeqc_code = template_file.read()

    # Build mineral phases section based on mineralogy dict
    mineral_phases = []
    mineral_names = {
        "Quartz": "Quartz",
        "Calcite": "Calcite",
        "Siderite": "Siderite",
        "Dolomite": "Dolomite",
        "Illite": "Illite",
        "Kaolinite": "Kaolinite",
        "K-feldspar": "K-feldspar",
        "Albite": "Albite",
        "Chlorite": "Chlorite(14A)",
        "Pyrite": "Pyrite",
        "Anhydrite": "Anhydrite",
    }

    for mineral_key, phreeqc_name in mineral_names.items():
        if mineral_key in minerals and minerals[mineral_key] >= 0:
            # Include mineral with 0 saturation index and specified initial moles
            mineral_phases.append(
                f"    {phreeqc_name}        0   {minerals[mineral_key]}"
            )
        else:
            # Comment out or skip minerals with negative values
            mineral_phases.append(f"    #{phreeqc_name}       0   0")

    mineral_phases_str = "\n".join(mineral_phases)

    phreeqc_code = phreeqc_code.replace(
        "__DATABASE__", "/usr/local/share/doc/phreeqc/database/phreeqc.dat"
    )
    phreeqc_code = phreeqc_code.replace("__TEMPERATURE__", str(temperature_c))
    phreeqc_code = phreeqc_code.replace("__NA__", str(Na))
    phreeqc_code = phreeqc_code.replace("__CL__", str(Cl))
    phreeqc_code = phreeqc_code.replace("__CA__", str(Ca))
    phreeqc_code = phreeqc_code.replace("__MG__", str(Mg))
    phreeqc_code = phreeqc_code.replace("__K__", str(K))
    phreeqc_code = phreeqc_code.replace("__SO4__", str(SO4))
    phreeqc_code = phreeqc_code.replace("__HCO3__", str(HCO3))
    phreeqc_code = phreeqc_code.replace("__PRESSURE_ATM__", str(pressure_atm))
    phreeqc_code = phreeqc_code.replace("__P_CO2__", str(p_co2))
    phreeqc_code = phreeqc_code.replace("__P_H2O__", str(p_h2o))
    phreeqc_code = phreeqc_code.replace("__MINERAL_PHASES__", mineral_phases_str)
    phreeqc_code = phreeqc_code.replace("co2_brine_rock.tsv", state_out_file)

    filename = os.path.join(temp_files_path, "co2_brine_rock_solution_properties.pqi")

    with open(filename, "w") as pqi:
        pqi.write(phreeqc_code)

    subprocess.run(
        ["phreeqc", filename, filename.replace(".pqi", ".pqo")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    # Make sure the file exists before trying to read it
    if not os.path.exists(state_out_file):
        raise FileNotFoundError(f"Output file not found: {state_out_file}")

    results = {}
    try:
        with open(state_out_file, mode="r") as file:
            reader = csv.DictReader(file, delimiter="\t")
            # Clean column names by stripping spaces
            if reader.fieldnames:
                fieldnames = [field.strip() for field in reader.fieldnames]
                reader = csv.DictReader(file, fieldnames=fieldnames, delimiter="\t")
                next(reader)  # Skip header row since we're providing our own fieldnames

                # Get the last row (final simulation state)
                for row in reader:
                    results = row  # Will keep the last row
    except Exception as e:
        print(f"Error reading {state_out_file}: {str(e)}", flush=True)
        raise

    species_data = []

    for ion in ["Na+", "Cl-", "K+", "Mg+2", "Ca+2", "SO4-2", "HCO3-", "CO3-2"]:
        activity_key = f"la_{ion}"
        molar_volume_key = f"VM_{ion}"

        # Handle potential missing keys safely
        try:
            activity_value = math.exp(float(results.get(activity_key, 0)))
            molar_volume_value = float(results.get(molar_volume_key, 0))
        except (ValueError, TypeError):
            activity_value = 0
            molar_volume_value = 0

        threshold = (
            -500
        )  # even if the species is non-existent, it will have an activity of -1000, this is to avoid including non-existing species
        species_data.append(
            {
                "species": ion,
                "activity": round(
                    activity_value if activity_value >= threshold else 0, 4
                ),
                "molar_volume": round(
                    molar_volume_value if molar_volume_value >= threshold else 0, 4
                ),
            }
        )

    # Handle potential missing keys safely
    try:
        density = float(results.get("SOL_DENSITY", 0))
        ionic_strength = float(results.get("mu", 0))
        pH = float(results.get("pH", 7.0))
        osmotic_coefficient = float(results.get("OSMOTIC", 0))
        partial_pressure_co2 = float(results.get("PR_CO2", 0))
        fugacity_co2 = float(results.get("PHI_CO2", 0))

    except (ValueError, TypeError):
        density = 0
        ionic_strength = 0
        pH = 7.0
        osmotic_coefficient = 0
        partial_pressure_co2 = 0
        fugacity_co2 = 0

    return (
        species_data,
        density,
        ionic_strength,
        pH,
        osmotic_coefficient,
        partial_pressure_co2,
        fugacity_co2,
    )

def _run_PHREEQC_brine_rock_varying_pressure(
    temperature, ion_moles, mineralogy, database="phreeqc"
):
    """
    Run PHREEQC simulation for CO2-brine-rock interaction over a pressure range.

    Parameters:
        temperature: Temperature in Kelvin
        ion_moles: Dictionary of ion molalities
        mineralogy: Dictionary of mineral names and initial moles
        database: Database model ('phreeqc' or 'pitzer')

    Returns:
        dict: Results with 'Pressure (MPa)' and 'Dissolved CO2 (mol/kg)' lists
    """
    temp_files_path = tempfile.gettempdir()
    temperature_c = temperature - 273.15

    # Load the PHREEQC template
    template_path = os.path.join(
        os.path.dirname(__file__), "phreeqc_templates", "co2_brine_rock_var_pressure_template.pqi"
    )
    with open(template_path, "r") as template_file:
        phreeqc_code = template_file.read()

    # Build mineral phases section based on mineralogy dict
    mineral_phases = []
    mineral_names = {
        "Quartz": "Quartz",
        "Calcite": "Calcite",
        "Siderite": "Siderite",
        "Dolomite": "Dolomite",
        "Illite": "Illite",
        "Kaolinite": "Kaolinite",
        "K-feldspar": "K-feldspar",
        "Albite": "Albite",
        "Chlorite": "Chlorite(14A)",
        "Pyrite": "Pyrite",
        "Anhydrite": "Anhydrite",
    }

    for mineral_key, phreeqc_name in mineral_names.items():
        if mineral_key in mineralogy and mineralogy[mineral_key] >= 0:
            # Include mineral with 0 saturation index and specified initial moles
            mineral_phases.append(
                f"    {phreeqc_name}        0   {mineralogy[mineral_key]}"
            )
        else:
            # Comment out or skip minerals with negative values
            mineral_phases.append(f"    #{phreeqc_name}       0   0")

    mineral_phases_str = "\n".join(mineral_phases)

    # Replace template placeholders with actual values
    database_path = f"/usr/local/share/doc/phreeqc/database/{database}.dat"
    output_file = os.path.join(temp_files_path, "co2_brine_rock_var_p.tsv")

    phreeqc_code = phreeqc_code.replace("__DATABASE__", database_path)
    phreeqc_code = phreeqc_code.replace("__TEMPERATURE__", str(temperature_c))
    phreeqc_code = phreeqc_code.replace("__NA__", str(ion_moles.get("Na+", 0)))
    phreeqc_code = phreeqc_code.replace("__CL__", str(ion_moles.get("Cl-", 0)))
    phreeqc_code = phreeqc_code.replace("__CA__", str(ion_moles.get("Ca+2", 0)))
    phreeqc_code = phreeqc_code.replace("__MG__", str(ion_moles.get("Mg+2", 0)))
    phreeqc_code = phreeqc_code.replace("__K__", str(ion_moles.get("K+", 0)))
    phreeqc_code = phreeqc_code.replace("__SO4__", str(ion_moles.get("SO4-2", 0)))
    phreeqc_code = phreeqc_code.replace("__HCO3__", str(ion_moles.get("HCO3-", 0)))
    phreeqc_code = phreeqc_code.replace("__MINERAL_PHASES__", mineral_phases_str)
    phreeqc_code = phreeqc_code.replace("__OUTPUT_FILE__", output_file)

    filename = "co2_brine_rock_var_pressure.pqi"
    pqi = open(os.path.join(temp_files_path, filename), "w")
    pqi.write(phreeqc_code)
    pqi.close()

    subprocess.run(
        [
            "phreeqc",
            f"{os.path.join(temp_files_path, filename)}",
            f"{os.path.join(temp_files_path, filename).replace('.pqi', '.pqo')}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    result = {"Pressure (MPa)": [], "Dissolved CO2 (mol/kg)": []}

    with open(output_file, mode="r") as file:
        reader = csv.DictReader(file, delimiter="\t")
        # Clean column names by stripping spaces
        if reader.fieldnames:
            fieldnames = [field.strip() for field in reader.fieldnames]
            reader = csv.DictReader(file, fieldnames=fieldnames, delimiter="\t")
            next(reader)  # Skip header row since we're providing our own fieldnames

        for row in reader:
            # Get pressure from gas phase data - need to check what column name is used
            # in the brine-rock template output
            try:
                # Try different possible pressure column names
                pressure = None
                if "pressure" in row:
                    pressure = float(row["pressure"])
                elif "CO2(g)" in row:
                    # If CO2(g) pressure is available
                    pressure = float(row["CO2(g)"])
                elif "PR_CO2" in row:
                    # Partial pressure from USER_PUNCH
                    pressure = float(row["PR_CO2"])

                if pressure is not None:
                    # Convert pressure from atm to MPa if needed
                    pressure_mpa = pressure * 0.101325 if pressure > 1.0 else pressure
                    pressure_mpa = round(pressure_mpa, 2)

                    trapped_co2 = float(row.get("C(4)", 0))

                    result["Pressure (MPa)"].append(pressure_mpa)
                    result["Dissolved CO2 (mol/kg)"].append(trapped_co2)

            except (ValueError, KeyError) as e:
                # Skip rows with invalid data
                continue

    # Clean up temporary files
    if os.path.exists("error.inp"):
        os.remove("error.inp")

    if os.path.exists("phreeqc.log"):
        os.remove("phreeqc.log")

    return result


def simulate_co2_brine_rock_fixed(
    temperature, pressure, species, mineralogy, model
):
    """
    Run PHREEQC simulation for brine-rock interaction at a single state.

    Parameters:
        temperature: Temperature in Kelvin
        pressure: Pressure in MPa
        species: Dictionary of ion molalities
        mineralogy: Dictionary of mineral names and initial moles
        model: Database model ('phreeqc' or 'pitzer')

    Returns:
        dict: Results including dissolved CO2, mineral deltas, and solution properties
    """
    temp_files_path = tempfile.gettempdir()
    Na = species.get("Na+", 0)
    Cl = species.get("Cl-", 0)
    Mg = species.get("Mg+2", 0)
    Ca = species.get("Ca+2", 0)
    K = species.get("K+", 0)
    SO4 = species.get("SO4-2", 0)
    HCO3 = species.get("HCO3-", 0)
    CO3 = species.get("CO3-2", 0)

    pressure_atm = pressure * 9.86923
    temperature_c = temperature - 273.15
    p_co2 = pressure_atm * 0.95
    p_h2o = pressure_atm * 0.05



    # Load the PHREEQC template
    template_path = os.path.join(os.path.dirname(__file__), "phreeqc_templates", "co2_brine_rock_template.pqi")
    with open(template_path, "r") as template_file:
        phreeqc_code = template_file.read()

    # Build mineral phases section based on mineralogy dict
    mineral_phases = []
    mineral_names = {
        "Quartz": "Quartz",
        "Calcite": "Calcite",
        "Siderite": "Siderite",
        "Dolomite": "Dolomite",
        "Illite": "Illite",
        "Kaolinite": "Kaolinite",
        "K-feldspar": "K-feldspar",
        "Albite": "Albite",
        "Chlorite": "Chlorite(14A)",
        "Pyrite": "Pyrite",
        "Anhydrite": "Anhydrite",
    }

    for mineral_key, phreeqc_name in mineral_names.items():
        if mineral_key in mineralogy and mineralogy[mineral_key] >= 0:
            # Include mineral with 0 saturation index and specified initial moles
            mineral_phases.append(
                f"    {phreeqc_name}        0   {mineralogy[mineral_key]}"
            )
        else:
            # Comment out or skip minerals with negative values
            mineral_phases.append(f"    #{phreeqc_name}       0   0")

    mineral_phases_str = "\n".join(mineral_phases)

    # Replace template placeholders with actual values
    database_name = model if model in ["phreeqc", "pitzer"] else "phreeqc"
    phreeqc_code = phreeqc_code.replace(
        "__DATABASE__", f"/usr/local/share/doc/phreeqc/database/{database_name}.dat"
    )

    brine_rock_out_file = os.path.join(temp_files_path, "co2_brine_rock.tsv")
    phreeqc_code = phreeqc_code.replace("__TEMPERATURE__", str(temperature_c))
    phreeqc_code = phreeqc_code.replace("__NA__", str(Na))
    phreeqc_code = phreeqc_code.replace("__CL__", str(Cl))
    phreeqc_code = phreeqc_code.replace("__CA__", str(Ca))
    phreeqc_code = phreeqc_code.replace("__MG__", str(Mg))
    phreeqc_code = phreeqc_code.replace("__K__", str(K))
    phreeqc_code = phreeqc_code.replace("__SO4__", str(SO4))
    phreeqc_code = phreeqc_code.replace("__HCO3__", str(HCO3))
    phreeqc_code = phreeqc_code.replace("__PRESSURE_ATM__", str(pressure_atm))
    phreeqc_code = phreeqc_code.replace("__P_CO2__", str(p_co2))
    phreeqc_code = phreeqc_code.replace("__P_H2O__", str(p_h2o))
    phreeqc_code = phreeqc_code.replace("__MINERAL_PHASES__", mineral_phases_str)
    phreeqc_code = phreeqc_code.replace("__OUTPUT_FILE__", brine_rock_out_file)

    filename = os.path.join(temp_files_path, "co2_brine_rock.pqi")

    with open(filename, "w") as pqi:
        pqi.write(phreeqc_code)

    # Run phreeqc with full paths
    subprocess.run(
        ["phreeqc", filename, filename.replace(".pqi", ".pqo")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    # Make sure the file exists before trying to read it
    if not os.path.exists(brine_rock_out_file):
        raise FileNotFoundError(f"Output file not found: {brine_rock_out_file}")

    # Initialize results with a default empty dictionary
    results = {}

    # Read the output file
    try:
        with open(brine_rock_out_file, mode="r") as file:
            reader = csv.DictReader(file, delimiter="\t")
            # Clean column names by stripping spaces
            if reader.fieldnames:
                fieldnames = [field.strip() for field in reader.fieldnames]
                reader = csv.DictReader(file, fieldnames=fieldnames, delimiter="\t")
                next(reader)  # Skip header row

                # Get the last row (final simulation state)
                for row in reader:
                    results = row  # Will keep the last row

    except Exception as e:
        print(f"Error reading {brine_rock_out_file}: {str(e)}", flush=True)
        raise

    # Extract results
    try:
        trapped_co2 = float(results.get("C(4)", 0))
        density = float(results.get("SOL_DENSITY", 0))
        ionic_strength = float(results.get("mu", 0))
        pH = float(results.get("pH", 7.0))
        osmotic_coefficient = float(results.get("OSMOTIC", 0))
        partial_pressure_co2 = float(results.get("PR_CO2", 0))
        fugacity_co2 = float(results.get("PHI_CO2", 0))

        # Extract mineral deltas
        mineral_equi = {}
        for mineral_key, phreeqc_name in mineral_names.items():
            delta_key = f'EQUI_{phreeqc_name.upper().replace("-", "").replace("(", "").replace(")", "").replace("14A", "")}'
            if mineral_key in mineralogy and mineralogy[mineral_key] >= 0:
                mineral_equi[mineral_key] = float(results.get(delta_key, 0))
            else:
                mineral_equi[mineral_key] = 0

    except (ValueError, TypeError) as e:
        print(f"Error parsing results: {e}", flush=True)
        trapped_co2 = 0
        density = 0
        ionic_strength = 0
        pH = 7.0
        osmotic_coefficient = 0
        partial_pressure_co2 = 0
        fugacity_co2 = 0
        mineral_equi = {k: 0 for k in mineral_names.keys()}

    return {
        "trapped_co2": trapped_co2,
        "mineral_equi": mineral_equi,
    }


def simulate_co2_brine_rock_var_p(temperature, ion_moles, mineralogy, model):
    """
    Simulate CO2 solubility with brine-rock interaction over a range of pressures at fixed temperature.

    Parameters:
        temperature: Fixed temperature in Kelvin
        ion_moles: Dictionary of ion molalities
        mineralogy: Dictionary of mineral names and initial moles
        model: Database model ('phreeqc' or 'pitzer')

    Returns:
        dict: Contains 'Pressure (MPa)' and 'Dissolved CO2 (mol/kg)' lists
    """

    result = _run_PHREEQC_brine_rock_varying_pressure(
        temperature, ion_moles, mineralogy, database="phreeqc"
    )

    return result


def simulate_co2_brine_rock_var_t(pressure, ion_moles, mineralogy, model):
    """
    Simulate CO2 solubility with brine-rock interaction over a range of temperatures at fixed pressure.

    Parameters:
        pressure: Fixed pressure in MPa
        ion_moles: Dictionary of ion molalities
        mineralogy: Dictionary of mineral names and initial moles
        model: Database model ('phreeqc' or 'pitzer')

    Returns:
        dict: Contains 'Temperature (K)' and 'Dissolved CO2 (mol/kg)' lists
    """
    temperatures = [
        298,
        313,
        328,
        343,
        358,
        373,
        388,
        403,
        418,
        433,
    ]  # K range (25-160°C)
    trapped_co2_values = []

    for temperature in temperatures:
        try:
            result = simulate_co2_brine_rock_fixed(
                temperature=temperature,
                pressure=pressure,
                species=ion_moles,
                mineralogy=mineralogy,
                model=model,
            )
            trapped_co2_values.append(result["trapped_co2"])
        except Exception as e:
            print(f"Error at temperature {temperature} K: {e}")
            trapped_co2_values.append(0)

    return {
        "Temperature (K)": temperatures,
        "Dissolved CO2 (mol/kg)": trapped_co2_values,
    }


# ---------------------------------------------------------------------------
# Mineral equilibrium with explicit porosity tracking
# ---------------------------------------------------------------------------

# Maps lowercase rock-physics names → PHREEQC phase names.
# Used by simulate_mineral_equilibrium.
_MINERAL_PHREEQC_NAMES = {
    "calcite":    "Calcite",
    "dolomite":   "Dolomite",
    "siderite":   "Siderite",
    "quartz":     "Quartz",
    "k-feldspar": "K-feldspar",
    "albite":     "Albite",
    "kaolinite":  "Kaolinite",
    "illite":     "Illite",
    "chlorite":   "Chlorite(14A)",
    "pyrite":     "Pyrite",
    "anhydrite":  "Anhydrite",
}


def simulate_mineral_equilibrium(
    temperature_k: float,
    pressure_mpa: float,
    mineralogy_wt: dict,
    porosity: float,
    species: dict,
    with_co2: bool = True,
    model: str = "phreeqc",
    bulk_volume_cm3: float = 100.0,
) -> dict:
    """Run PHREEQC mineral equilibrium starting from weight fractions + porosity.

    Converts the initial mineralogy (weight fractions + porosity) to absolute
    mineral moles, runs PHREEQC to equilibrium, then computes the post-reaction
    mineralogy and porosity from the remaining mineral moles reported by
    PHREEQC.  This is the correct path for calculating porosity change due to
    mineral dissolution / precipitation.

    Parameters
    ----------
    temperature_k    : Temperature in Kelvin.
    pressure_mpa     : Pressure in MPa.
    mineralogy_wt    : {mineral_name: weight_fraction}  — lowercase keys
                       (calcite, dolomite, siderite, quartz, k-feldspar,
                       albite, kaolinite, illite, chlorite, pyrite, anhydrite).
                       Fractions need not sum to 1; they are normalised
                       internally before the mole conversion.
    porosity         : Initial pore volume fraction [0, 1].
    species          : Ion molalities (mol/kg water) — keys: Na+, Cl-, Mg+2,
                       Ca+2, K+, SO4-2, HCO3-, CO3-2.
    with_co2         : True  → include CO2 gas phase (post-injection scenario).
                       False → no gas phase (pre-injection / baseline equilibrium).
    model            : PHREEQC database — "phreeqc" or "pitzer".
    bulk_volume_cm3  : Reference bulk volume in cm³ (default 100, matching
                       existing PHREEQC templates).

    Returns
    -------
    dict with keys
        mineral_moles_initial   : {mineral: moles} before reaction
        mineral_moles_post      : {mineral: moles} remaining after reaction
        mineralogy_wt_post      : {mineral: weight_fraction} after reaction
        porosity_initial        : float
        porosity_post           : float  (recomputed from remaining moles)
        porosity_change         : float  (positive = dissolution opened pores)
        trapped_co2_mol_per_kg  : dissolved C(4) total (mol/kg)
        pH_post                 : float
        solution_density_gcc    : float  (g/cm³)
        salinity_ppm            : float
        ion_totals              : {ion: mol/kg}  Na, Cl, Mg, Ca, K, S(6), C(4)
    """
    temp_files_path = tempfile.gettempdir()
    temperature_c = temperature_k - 273.15
    pressure_atm = pressure_mpa * 9.86923
    p_co2 = pressure_atm * 0.95
    p_h2o = pressure_atm * 0.05

    Na  = species.get("Na+",   0)
    Cl  = species.get("Cl-",   0)
    Mg  = species.get("Mg+2",  0)
    Ca  = species.get("Ca+2",  0)
    K   = species.get("K+",    0)
    SO4 = species.get("SO4-2", 0)
    HCO3 = species.get("HCO3-", 0) + species.get("CO3-2", 0)

    # Convert weight fractions + porosity → absolute mineral moles
    # (normalise wt_fracs so they sum to 1 over known minerals)
    known_wt = {m: v for m, v in mineralogy_wt.items() if m in _MINERAL_PHREEQC_NAMES and v > 0}
    total_wt = sum(known_wt.values())
    norm_wt = {m: v / total_wt for m, v in known_wt.items()}
    initial_moles = wt_fractions_to_moles(norm_wt, porosity, bulk_volume_cm3)

    # Water mass (kg): approximate water density 1.0 g/cm³ at reservoir conditions
    water_volume_cm3 = porosity * bulk_volume_cm3
    water_mass_kg = water_volume_cm3 / 1000.0  # 1.0 g/cm³ × cm³ / 1000 → kg

    # Build EQUILIBRIUM_PHASES block — only include minerals with positive moles
    mineral_phase_lines = []
    selected_minerals = []
    for py_name, phreeqc_name in _MINERAL_PHREEQC_NAMES.items():
        moles = initial_moles.get(py_name, 0.0)
        if moles > 0:
            mineral_phase_lines.append(f"    {phreeqc_name}    0    {moles:.8f}")
            selected_minerals.append(phreeqc_name)
        else:
            mineral_phase_lines.append(f"    #{phreeqc_name}    0    0")

    mineral_phases_str = "\n".join(mineral_phase_lines)
    selected_minerals_str = " ".join(selected_minerals)

    # Load appropriate template
    if with_co2:
        template_name = "mineral_eq_post_template.pqi"
    else:
        template_name = "mineral_eq_pre_template.pqi"
    template_path = os.path.join(os.path.dirname(__file__), "phreeqc_templates", template_name)
    with open(template_path, "r") as f:
        phreeqc_code = f.read()

    # Unique output file to avoid collisions between concurrent calls
    unique_id = uuid.uuid4().hex[:8]
    output_tsv = os.path.join(temp_files_path, f"mineral_eq_{unique_id}.tsv")
    pqi_file = os.path.join(temp_files_path, f"mineral_eq_{unique_id}.pqi")

    database_name = model if model in ("phreeqc", "pitzer") else "phreeqc"
    phreeqc_code = phreeqc_code.replace("__DATABASE__",      f"/usr/local/share/doc/phreeqc/database/{database_name}.dat")
    phreeqc_code = phreeqc_code.replace("__TEMPERATURE__",   str(temperature_c))
    phreeqc_code = phreeqc_code.replace("__PRESSURE_ATM__",  str(pressure_atm))
    phreeqc_code = phreeqc_code.replace("__NA__",            str(Na))
    phreeqc_code = phreeqc_code.replace("__CL__",            str(Cl))
    phreeqc_code = phreeqc_code.replace("__K__",             str(K))
    phreeqc_code = phreeqc_code.replace("__MG__",            str(Mg))
    phreeqc_code = phreeqc_code.replace("__CA__",            str(Ca))
    phreeqc_code = phreeqc_code.replace("__SO4__",           str(SO4))
    phreeqc_code = phreeqc_code.replace("__HCO3__",          str(HCO3))
    phreeqc_code = phreeqc_code.replace("__WATER_MASS__",    str(water_mass_kg))
    phreeqc_code = phreeqc_code.replace("__MINERAL_PHASES__", mineral_phases_str)
    phreeqc_code = phreeqc_code.replace("__SELECTED_MINERALS__", selected_minerals_str)
    phreeqc_code = phreeqc_code.replace("__OUTPUT_FILE__",   output_tsv)
    if with_co2:
        phreeqc_code = phreeqc_code.replace("__P_CO2__",  str(p_co2))
        phreeqc_code = phreeqc_code.replace("__P_H2O__",  str(p_h2o))

    with open(pqi_file, "w") as f:
        f.write(phreeqc_code)

    subprocess.run(
        ["phreeqc", pqi_file, pqi_file.replace(".pqi", ".pqo")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    if not os.path.exists(output_tsv):
        raise FileNotFoundError(
            f"PHREEQC did not produce output: {output_tsv}. "
            "Check the .pqo log for errors."
        )

    # Parse output with pandas (consistent with supplemental approach)
    df = pd.read_csv(output_tsv, sep="\t")
    df.columns = df.columns.str.strip()
    row = df.iloc[-1]

    # Read post-reaction mineral moles (remaining absolute moles)
    post_moles = {}
    for py_name, phreeqc_name in _MINERAL_PHREEQC_NAMES.items():
        if phreeqc_name in df.columns:
            val = row[phreeqc_name]
            # PHREEQC can write -1.#IND or similar on failure; treat as 0
            try:
                post_moles[py_name] = max(float(val), 0.0)
            except (ValueError, TypeError):
                post_moles[py_name] = initial_moles.get(py_name, 0.0)
        elif py_name in initial_moles:
            # Inert mineral: not in EQUILIBRIUM_PHASES → moles unchanged
            post_moles[py_name] = initial_moles[py_name]

    # Recompute porosity and weight fractions from post-reaction moles
    porosity_post = moles_to_porosity(post_moles, bulk_volume_cm3)
    wt_post = moles_to_wt_fractions(post_moles)

    # Parse solution properties
    try:
        ph_post         = float(row.get("pH", 7.0))
        trapped_co2     = float(row.get("C(4)", 0.0))
        sol_density     = float(row.get("SOL_DENSITY", 0.0))
        salinity_ppm    = float(row.get("Salinity_ppm", 0.0))
    except (ValueError, TypeError):
        ph_post = 7.0; trapped_co2 = 0.0; sol_density = 0.0; salinity_ppm = 0.0

    ion_totals = {}
    for col, key in [("Na", "Na"), ("Cl", "Cl"), ("Mg", "Mg"), ("Ca", "Ca"),
                     ("K", "K"), ("S(6)", "SO4"), ("C(4)", "DIC")]:
        try:
            ion_totals[key] = float(row.get(col, 0.0))
        except (ValueError, TypeError):
            ion_totals[key] = 0.0

    return {
        "mineral_moles_initial":  {k: round(v, 8) for k, v in initial_moles.items()},
        "mineral_moles_post":     {k: round(v, 8) for k, v in post_moles.items()},
        "mineralogy_wt_post":     {k: round(v, 6) for k, v in wt_post.items()},
        "porosity_initial":       round(porosity, 6),
        "porosity_post":          round(porosity_post, 6),
        "porosity_change":        round(porosity_post - porosity, 6),
        "trapped_co2_mol_per_kg": round(trapped_co2, 6),
        "pH_post":                round(ph_post, 4),
        "solution_density_gcc":   round(sol_density, 4),
        "salinity_ppm":           round(salinity_ppm, 2),
        "ion_totals":             {k: round(v, 6) for k, v in ion_totals.items()},
    }
