import os
import math
import pandas as pd
import subprocess
import csv
import sys

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
    temp_files_path = "."
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

    template_path = os.path.join("phreeqc_programs", "co2_brine_rock_template.pqi")
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
    temp_files_path = "."
    temperature_c = temperature - 273.15

    # Load the PHREEQC template
    template_path = os.path.join(
        "phreeqc_programs", "co2_brine_rock_var_pressure_template.pqi"
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

                    dissolved_co2 = float(row.get("C(4)", 0))

                    result["Pressure (MPa)"].append(pressure_mpa)
                    result["Dissolved CO2 (mol/kg)"].append(dissolved_co2)

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
    temp_files_path = "."
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

    # Define the output file path consistently
    brine_rock_out_file = os.path.join(temp_files_path, "co2_brine_rock.tsv")

    # Load the PHREEQC template
    template_path = os.path.join("phreeqc_programs", "co2_brine_rock_template.pqi")
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
        dissolved_co2 = float(results.get("C(4)", 0))
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
        dissolved_co2 = 0
        density = 0
        ionic_strength = 0
        pH = 7.0
        osmotic_coefficient = 0
        partial_pressure_co2 = 0
        fugacity_co2 = 0
        mineral_equi = {k: 0 for k in mineral_names.keys()}

    return {
        "dissolved_co2": dissolved_co2,
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
    dissolved_co2_values = []

    for temperature in temperatures:
        try:
            result = simulate_co2_brine_rock_fixed(
                temperature=temperature,
                pressure=pressure,
                species=ion_moles,
                mineralogy=mineralogy,
                model=model,
            )
            dissolved_co2_values.append(result["dissolved_co2"])
        except Exception as e:
            print(f"Error at temperature {temperature} K: {e}")
            dissolved_co2_values.append(0)

    return {
        "Temperature (K)": temperatures,
        "Dissolved CO2 (mol/kg)": dissolved_co2_values,
    }
