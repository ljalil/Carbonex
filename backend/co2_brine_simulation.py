import os
import math
import pandas as pd
import subprocess
import csv
import DuanSun2006
import sys


def simulate_co2_brine_solution_properties(temperature, pressure, species):
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

    state_out_file = os.path.join(temp_files_path, "solution_properties.tsv")

    template_path = os.path.join("phreeqc_programs", "co2_brine_template.pqi")
    with open(template_path, "r") as template_file:
        phreeqc_code = template_file.read()

    phreeqc_code = phreeqc_code.replace(
        "__DATABASE__", "/usr/local/share/doc/phreeqc/database/pitzer.dat"
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
    phreeqc_code = phreeqc_code.replace("__OUTPUT_FILE__", state_out_file)

    filename = os.path.join(temp_files_path, "solution_properties.pqi")

    pqi = open(filename, "w")
    pqi.write(phreeqc_code)
    pqi.close()

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

    return (
        species_data,
        density,
        ionic_strength,
        pH,
        osmotic_coefficient,
        partial_pressure_co2,
        fugacity_co2,
    )


def _simulate_varying_pressure_PHREEQC(temperature, ion_moles, database):
    temp_files_path = "."
    temperature_c = temperature - 273.15

    template_path = os.path.join(
        "phreeqc_programs", "co2_brine_var_pressure_template.pqi"
    )
    with open(template_path, "r") as template_file:
        phreeqc_code = template_file.read()

    database_path = f"/usr/local/share/doc/phreeqc/database/{database}.dat"
    output_file = os.path.join(temp_files_path, "varying_pressure.tsv")

    phreeqc_code = phreeqc_code.replace("__DATABASE__", database_path)
    phreeqc_code = phreeqc_code.replace("__TEMPERATURE__", str(temperature_c))
    phreeqc_code = phreeqc_code.replace("__NA__", str(ion_moles.get("Na+", 0)))
    phreeqc_code = phreeqc_code.replace("__CL__", str(ion_moles.get("Cl-", 0)))
    phreeqc_code = phreeqc_code.replace("__CA__", str(ion_moles.get("Ca+2", 0)))
    phreeqc_code = phreeqc_code.replace("__MG__", str(ion_moles.get("Mg+2", 0)))
    phreeqc_code = phreeqc_code.replace("__K__", str(ion_moles.get("K+", 0)))
    phreeqc_code = phreeqc_code.replace("__SO4__", str(ion_moles.get("SO4-2", 0)))
    phreeqc_code = phreeqc_code.replace("__OUTPUT_FILE__", output_file)

    filename = "varying_pressure.pqi"

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

    with open(os.path.join(temp_files_path, "varying_pressure.tsv"), mode="r") as file:
        reader = csv.DictReader(file, delimiter="\t")
        # Clean column names by stripping spaces
        if reader.fieldnames:
            fieldnames = [field.strip() for field in reader.fieldnames]
            reader = csv.DictReader(file, fieldnames=fieldnames, delimiter="\t")
            next(reader)  # Skip header row since we're providing our own fieldnames

        for row in reader:
            # Convert pressure from atm to MPa
            pressure = float(row.get("pressure", 0)) * 0.101325
            pressure = round(pressure, 2)
            trapped_co2 = float(row.get("C(4)", 2))

            result["Pressure (MPa)"].append(pressure)
            result["Dissolved CO2 (mol/kg)"].append(trapped_co2)

    if os.path.exists("error.inp"):
        os.remove("error.inp")

    if os.path.exists("phreeqc.log"):
        os.remove("phreeqc.log")

    return result


def _simulate_varying_pressure_Carbonex(temperature, ion_moles):
    return {"Pressure (MPa)": [], "Dissolved CO2 (mol/kg)": []}


def _simulate_varying_pressure_DuanSun(temperature, ion_moles):
    """
    Use Duan and Sun (2006) model to calculate CO2 solubility over a pressure range.
    Returns dict with lists for 'Pressure (MPa)' and 'Dissolved CO2 (mol/kg)'.
    """

    model = DuanSun2006.DuanSun2006()
    P_start = 0.1
    P_end = 50.0
    P_step = 1
    result = model.calculate_varying_pressure(
        P_start, P_end, P_step, temperature, ion_moles, model="DuanSun"
    )
    return result


def _simulate_varying_temperature_PHREEQC(pressure, ion_moles, database):
    """
    Use PHREEQC to calculate CO2 solubility over a temperature range.
    Since PHREEQC cannot vary temperature the same way as pressure, we call
    _run_PHREEQC_state_simulation multiple times with different temperatures.
    Returns dict with lists for 'Temperature (K)' and 'Dissolved CO2 (mol/kg)'.
    """
    T_start = 273.15  # 0°C
    T_end = 573.15  # 100°C
    T_step = 5.0  # 5K steps

    result = {"Temperature (K)": [], "Dissolved CO2 (mol/kg)": []}

    temperatures = []
    temp = T_start
    while temp <= T_end:
        temperatures.append(temp)
        temp += T_step

    for temperature in temperatures:
        try:
            trapped_co2 = _run_PHREEQC_state_simulation(
                temperature, pressure, ion_moles, database
            )
            result["Temperature (K)"].append(temperature)
            result["Dissolved CO2 (mol/kg)"].append(trapped_co2)
        except Exception as e:
            print(f"Error at temperature {temperature}: {e}", flush=True)
            continue

    return result


def _simulate_varying_temperature_Carbonex(pressure, ion_moles):
    """
    Placeholder for Carbonex model varying temperature calculation.
    """
    return {"Temperature (K)": [], "Dissolved CO2 (mol/kg)": []}


def _simulate_varying_temperature_DuanSun(pressure, ion_moles):
    """
    Use Duan and Sun (2006) model to calculate CO2 solubility over a temperature range.
    Returns dict with lists for 'Temperature (K)' and 'Dissolved CO2 (mol/kg)'.
    """

    model = DuanSun2006.DuanSun2006()

    T_start = 273.15  # 0°C
    T_end = 573.15  # 100°C
    T_step = 5.0  # 5K steps

    result = model.calculate_varying_temperature(
        T_start, T_end, T_step, pressure, ion_moles, model="DuanSun"
    )

    return result


def simulate_co2_brine_var_p(temperature, ion_moles, model):
    if model == "phreeqc_phreeqc":
        result = _simulate_varying_pressure_PHREEQC(
            temperature, ion_moles, database="phreeqc"
        )
    elif model == "phreeqc_pitzer":
        result = _simulate_varying_pressure_PHREEQC(
            temperature, ion_moles, database="pitzer"
        )
    elif model == "duan_sun_2006":
        print("using duan sun model", flush=True)
        result = _simulate_varying_pressure_DuanSun(temperature, ion_moles)

    elif model == "carbonex":
        results = _simulate_varying_pressure_Carbonex(temperature, ion_moles)
    else:
        result = {"Pressure (MPa)": [], "Dissolved CO2 (mol/kg)": []}

    return result


def simulate_co2_brine_var_t(pressure, ion_moles, model):
    """
    Simulate CO2 solubility over a range of temperatures at fixed pressure.

    Parameters:
        pressure: Fixed pressure in MPa
        ion_moles: Dictionary of ion molalities
        model: Model to use ('phreeqc_phreeqc', 'phreeqc_pitzer', 'duan_sun_2006', 'carbonex')

    Returns:
        dict: Contains 'Temperature (K)' and 'Dissolved CO2 (mol/kg)' lists
    """
    if model == "phreeqc_phreeqc":
        result = _simulate_varying_temperature_PHREEQC(
            pressure, ion_moles, database="phreeqc"
        )
    elif model == "phreeqc_pitzer":
        result = _simulate_varying_temperature_PHREEQC(
            pressure, ion_moles, database="pitzer"
        )
    elif model == "duan_sun_2006":
        result = _simulate_varying_temperature_DuanSun(pressure, ion_moles)
    elif model == "carbonex":
        result = _simulate_varying_temperature_Carbonex(pressure, ion_moles)
    else:
        # Default to empty result for unknown models
        result = {"Temperature (K)": [], "Dissolved CO2 (mol/kg)": []}

    return result


def _run_PHREEQC_state_simulation(temperature, pressure, species, database):
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
    state_out_file = os.path.join(temp_files_path, "state_out.tsv")

    # Load the PHREEQC template
    template_path = os.path.join("phreeqc_programs", "co2_brine_template.pqi")
    with open(template_path, "r") as template_file:
        phreeqc_code = template_file.read()

    # Replace template placeholders with actual values
    phreeqc_code = phreeqc_code.replace(
        "__DATABASE__", f"/usr/local/share/doc/phreeqc/database/{database}.dat"
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
    phreeqc_code = phreeqc_code.replace("__OUTPUT_FILE__", state_out_file)

    filename = os.path.join(temp_files_path, "state_out.pqi")

    pqi = open(filename, "w")
    pqi.write(phreeqc_code)
    pqi.close()

    # Run phreeqc with full paths
    subprocess.run(
        ["phreeqc", filename, filename.replace(".pqi", ".pqo")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    # Make sure the file exists before trying to read it
    if not os.path.exists(state_out_file):
        raise FileNotFoundError(f"Output file not found: {state_out_file}")

    # Initialize results with a default empty dictionary
    results = {}

    # Read the output file to get the CO2 concentration
    try:
        with open(state_out_file, mode="r") as file:
            reader = csv.DictReader(file, delimiter="\t")
            # Clean column names by stripping spaces
            if reader.fieldnames:
                fieldnames = [field.strip() for field in reader.fieldnames]
                reader = csv.DictReader(file, fieldnames=fieldnames, delimiter="\t")
                next(reader)  # Skip header row

                # Get the last row (final simulation state)
                for row in reader:
                    results = row  # Will keep the last row
                    # print(results)

    except Exception as e:
        print(f"Error reading {state_out_file}: {str(e)}", flush=True)
        raise

    # Extract the C(4) value (dissolved CO2)
    try:
        trapped_co2 = float(results.get("C(4)", 0))
    except (ValueError, TypeError):
        trapped_co2 = 0

    return trapped_co2


def _run_Duan_Sun_state_simulation(temperature, pressure, species):
    # Use Duan and Sun (2006) model to calculate dissolved CO2
    model = DuanSun2006.DuanSun2006()
    try:
        # calculate_CO2_solubility expects P in MPa, T in Kelvin, ion molalities dict
        trapped_co2 = model.calculate_CO2_solubility(
            pressure, temperature, species, model="DuanSun"
        )
    except Exception:
        trapped_co2 = 0
    return trapped_co2


def simulate_co2_brine_fixed(temperature, pressure, species, model):
    """
    Run simulation for fixed conditions and return only dissolved CO2.
    """
    trapped_co2 = 0  # Default value
    
    if model == "phreeqc_phreeqc":
        trapped_co2 = _run_PHREEQC_state_simulation(
            temperature, pressure, species, database="phreeqc"
        )
    elif model == "phreeqc_pitzer":
        trapped_co2 = _run_PHREEQC_state_simulation(
            temperature, pressure, species, database="pitzer"
        )
    elif model == "duan_sun_2006":
        trapped_co2 = _run_Duan_Sun_state_simulation(temperature, pressure, species)
    elif model == "carbonex":
        trapped_co2 = 3
    else:
        # Default to phreeqc if model is not recognized
        trapped_co2 = _run_PHREEQC_state_simulation(
            temperature, pressure, species, database="phreeqc"
        )

    return trapped_co2
