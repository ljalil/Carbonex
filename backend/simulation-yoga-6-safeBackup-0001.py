import os
import pandas as pd
import subprocess
import csv

def get_solution_properties(temperature, pressure, species):
    temp_files_path = '.'
    Na = species.get('Na+', 0)
    Cl = species.get('Cl-', 0)
    Mg = species.get('Mg+2', 0)
    Ca = species.get('Ca+2', 0)
    K = species.get('K+', 0)
    SO4 = species.get('SO4-2', 0)
    HCO3 = species.get('HCO3-', 0)
    CO3 = species.get('CO3-2', 0)

    pressure_atm = pressure * 9.86923
    temperature_c = temperature -  273.15
    p_co2 = pressure_atm * 0.95
    p_h2o = pressure_atm * 0.05

    # Define the output file path consistently
    state_out_file = os.path.join(temp_files_path, "solution_properties.tsv")

    phreeqc_code = f'DATABASE /usr/local/share/doc/phreeqc/database/pitzer.dat\n'
    phreeqc_code += f'SOLUTION 1\n\ttemp\t{temperature_c}\n\tpH\t7.0\n\t'
    phreeqc_code += f'units\tmol/kgw\n\tNa\t{Na}\n\tCl\t{Cl}\n\tCa\t{Ca}\n\tMg\t{Mg}\n\tK\t{K}\n\tS(6)\t{SO4}\n\tC {HCO3} as HCO3\n'
    phreeqc_code += f'GAS_PHASE 1\n\t-fixed_pressure\n\t-pressure {pressure_atm}\n'
    phreeqc_code += f'\t-volume 1.0\n\t CO2(g) {p_co2}\n\tH2O(g) {p_h2o}\n'
    phreeqc_code +=  f'''
USER_PUNCH
    -headings VM_Na+ VM_Cl- VM_K+ VM_Ca+2 VM_Mg+2 VM_SO4-2 VM_HCO3- VM_CO3-2 SOL_DENSITY OSMOTIC
    -start
    10 PUNCH VM("Na+")
    20 PUNCH VM("Cl-")
    30 PUNCH VM("K+")
    40 PUNCH VM("Ca+2")
    50 PUNCH VM("Mg+2")
    60 PUNCH VM("SO4-2")
    70 PUNCH VM("HCO3-")
    80 PUNCH VM("CO3-2")
    90 PUNCH RHO
    100 PUNCH OSMOTIC
    -end

SELECTED_OUTPUT
    -file {state_out_file}
    -totals C(4)
    -solution True
    -gases CO2(g)
    -saturation_indices CO2(g)
    -activities   Na+ K+ Cl- SO4+2 Ca+2 Mg+2 HCO3- CO3-2
    -ionic_strength True
    -calculate_values
END'''

    filename = os.path.join(temp_files_path, 'solution_properties.pqi')

    pqi = open(filename, 'w')
    pqi.write(phreeqc_code)
    pqi.close()

    # Run phreeqc with full paths
    subprocess.run(['phreeqc', filename, filename.replace('.pqi', '.pqo')], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # Make sure the file exists before trying to read it
    if not os.path.exists(state_out_file):
        raise FileNotFoundError(f"Output file not found: {state_out_file}")

    # Read the output file using the same path as specified in SELECTED_OUTPUT
    results = {}
    try:
        with open(state_out_file, mode='r') as file:
            reader = csv.DictReader(file, delimiter='\t')
            # Clean column names by stripping spaces
            if reader.fieldnames:
                fieldnames = [field.strip() for field in reader.fieldnames]
                reader = csv.DictReader(file, fieldnames=fieldnames, delimiter='\t')
                next(reader)  # Skip header row since we're providing our own fieldnames
                
                # Get the last row (final simulation state)
                for row in reader:
                    results = row  # Will keep the last row
    except Exception as e:
        print(f"Error reading {state_out_file}: {str(e)}")
        raise

    species_data = []

    for ion in ['Na+', 'Cl-', 'K+', 'Mg+2', 'Ca+2', 'SO4-2', 'HCO3-', 'CO3-2']:
        activity_key = f'la_{ion}'
        molar_volume_key = f'VM_{ion}'
        
        # Handle potential missing keys safely
        try:
            activity_value = float(results.get(activity_key, 0))
            molar_volume_value = float(results.get(molar_volume_key, 0))
        except (ValueError, TypeError):
            activity_value = 0
            molar_volume_value = 0
            
        threshold = -500  # even if the species is non-existent, it will have an activity of -1000, this is to avoid including non-existing species
        species_data.append({
            'species': ion,
            'activity': round(activity_value if activity_value >= threshold else 0, 4),
            'molar_volume': round(molar_volume_value if molar_volume_value >= threshold else 0, 4)
        })



    # Handle potential missing keys safely
    try:
    
        density = float(results.get('SOL_DENSITY', 0))
        ionic_strength = float(results.get('mu', 0))
        ph = float(results.get('pH', 7.0))
        osmotic_coefficient = float(results.get('OSMOTIC', 0))
    except (ValueError, TypeError):
        density = 0
        ionic_strength = 0
        ph = 7.0
        osmotic_coefficient = 0
        
    activity_of_water = 3.5  # Fixed value as in original code
    
    return species_data, density, ionic_strength, ph, activity_of_water, osmotic_coefficient

def simulate_varying_pressure(temperature, ion_moles, database="pitzer", print_code=False):
    database_path = f'/usr/local/share/doc/phreeqc/database/{database}.dat'
    temp_files_path = "."

    temperature_c = temperature - 273.15

    phreeqc_code = f"DATABASE {database_path}\n\n"

    phreeqc_code += "SOLUTION 1\n"
    phreeqc_code += f"\ttemperature\t{temperature_c}\n"
    phreeqc_code += "\tunits\tmol/kgw\n"
    phreeqc_code += f'\tNa\t{ion_moles.get("Na+", 0)}\n'
    phreeqc_code += f'\tCl\t{ion_moles.get("Cl-", 0)}\n'
    phreeqc_code += f'\tCa\t{ion_moles.get("Ca+2", 0)}\n'
    phreeqc_code += f'\tMg\t{ion_moles.get("Mg+2", 0)}\n'
    phreeqc_code += f'\tK\t{ion_moles.get("K+", 0)}\n'
    phreeqc_code += f'\tS(6)\t{ion_moles.get("SO4-2", 0)}\n'
    
    phreeqc_code  += f'GAS_PHASE 1\n\t-fixed_volume\n\tCO2(g)\t0\n\tH2O(g)\t0\n'
    phreeqc_code  += f'REACTION 1\n\tCO2 1;\t  0 100*0.5\n'
    phreeqc_code  += 'INCREMENTAL_REACTIONS true\n'
    temperature_str = str(temperature).replace('.', '_')
    phreeqc_code += f'SELECTED_OUTPUT\n\t-file {os.path.join(temp_files_path, "varying_pressure.tsv")}\n\t-totals\tC(4)\n\t-solution True\n\t-gases\tCO2(g)\n\t-saturation_indices CO2(g)\nEND\n'

    filename = 'varying_pressure.pqi'
    if print_code:
        print(phreeqc_code)
    pqi = open(os.path.join(temp_files_path, filename), 'w')
    pqi.write(phreeqc_code)

    pqi.close()

    subprocess.run(['phreeqc', f"{os.path.join(temp_files_path, filename)}", f"{os.path.join(temp_files_path, filename).replace('.pqi', '.pqo')}"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # Read data using standard csv module instead of pandas
    result = {'Pressure (MPa)': [], 'Dissolved CO2 (mol/kg)': []}
    
    with open(os.path.join(temp_files_path, "varying_pressure.tsv"), mode='r') as file:
        reader = csv.DictReader(file, delimiter='\t')
        # Clean column names by stripping spaces
        if reader.fieldnames:
            fieldnames = [field.strip() for field in reader.fieldnames]
            reader = csv.DictReader(file, fieldnames=fieldnames, delimiter='\t')
            next(reader)  # Skip header row since we're providing our own fieldnames
        
        for row in reader:
            # Convert pressure from atm to MPa
            pressure = float(row.get('pressure', 0)) * 0.101325
            dissolved_co2 = float(row.get('C(4)', 2))
            
            result['Pressure (MPa)'].append(pressure)
            result['Dissolved CO2 (mol/kg)'].append(dissolved_co2)

    if os.path.exists("error.inp"):
        os.remove("error.inp")
        
    if os.path.exists("phreeqc.log"):
        os.remove("phreeqc.log")

    return result

def run_state_simulation(temperature, pressure, species):
    temp_files_path = '.'
    Na = species.get('Na+', 0)
    Cl = species.get('Cl-', 0)
    Mg = species.get('Mg+2', 0)
    Ca = species.get('Ca+2', 0)
    K = species.get('K+', 0)
    SO4 = species.get('SO4-2', 0)
    HCO3 = species.get('HCO3-', 0)
    CO3 = species.get('CO3-2', 0)

    pressure_atm = pressure * 9.86923
    temperature_c = temperature - 273.15
    p_co2 = pressure_atm * 0.95
    p_h2o = pressure_atm * 0.05

    # Define the output file path consistently
    state_out_file = os.path.join(temp_files_path, "state_out.tsv")

    phreeqc_code = f'DATABASE /usr/local/share/doc/phreeqc/database/pitzer.dat\n'
    phreeqc_code += f'SOLUTION 1\n\ttemp\t{temperature_c}\n\tpH\t7.0\n\t'
    phreeqc_code += f'units\tmol/kgw\n\tNa\t{Na}\n\tCl\t{Cl}\n\tCa\t{Ca}\n\tMg\t{Mg}\n\tK\t{K}\n\tS(6)\t{SO4}\n\tC {HCO3} as HCO3\n'
    phreeqc_code += f'GAS_PHASE 1\n\t-fixed_pressure\n\t-pressure {pressure_atm}\n'
    phreeqc_code += f'\t-volume 1.0\n\t CO2(g) {p_co2}\n\tH2O(g) {p_h2o}\n'
    phreeqc_code += f'''
USER_PUNCH
    -headings VM_Na+ VM_Cl- VM_K+ VM_Ca+2 VM_Mg+2 VM_SO4-2 VM_HCO3- VM_CO3-2 SOL_DENSITY OSMOTIC
    -start
    10 PUNCH VM("Na+")
    20 PUNCH VM("Cl-")
    30 PUNCH VM("K+")
    40 PUNCH VM("Ca+2")
    50 PUNCH VM("Mg+2")
    60 PUNCH VM("SO4-2")
    70 PUNCH VM("HCO3-")
    80 PUNCH VM("CO3-2")
    90 PUNCH RHO
    100 PUNCH OSMOTIC
    -end

SELECTED_OUTPUT
    -file {state_out_file}
    -totals C(4)
    -solution True
    -gases CO2(g)
    -saturation_indices CO2(g)
    -activities   Na+ K+ Cl- SO4+2 Ca+2 Mg+2 HCO3- CO3-2
    -ionic_strength True
    -calculate_values
END'''

    filename = os.path.join(temp_files_path, 'state_out.pqi')

    pqi = open(filename, 'w')
    pqi.write(phreeqc_code)
    pqi.close()

    # Run phreeqc with full paths
    subprocess.run(['phreeqc', filename, filename.replace('.pqi', '.pqo')], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # Make sure the file exists before trying to read it
    if not os.path.exists(state_out_file):
        raise FileNotFoundError(f"Output file not found: {state_out_file}")

    # Initialize results with a default empty dictionary
    results = {}
    
    # Read the output file to get the CO2 concentration
    try:
        with open(state_out_file, mode='r') as file:
            reader = csv.DictReader(file, delimiter='\t')
            # Clean column names by stripping spaces
            if reader.fieldnames:
                fieldnames = [field.strip() for field in reader.fieldnames]
                reader = csv.DictReader(file, fieldnames=fieldnames, delimiter='\t')
                next(reader)  # Skip header row
                
                # Get the last row (final simulation state)
                for row in reader:
                    results = row  # Will keep the last row
                    print(results)
            
    except Exception as e:
        print(f"Error reading {state_out_file}: {str(e)}")
        raise

    # Extract the C(4) value (dissolved CO2)
    try:
        dissolved_co2 = float(results.get('C(4)', 0))
    except (ValueError, TypeError):
        dissolved_co2 = 0

    print('Dissolved CO2 concentration:', dissolved_co2)
    
    return dissolved_co2

if __name__ == '__main__':
    # Testing code for the new function
    dissolved_co2 = run_state_simulation(temperature=298, pressure=1, species={'Na+': 0.1, 'Cl-': 0.1, 'Mg+2': 0, 'Ca+2': 0, 'K+': 0, 'SO4-2': 0, 'HCO3-': 0, 'CO3-2': 0})
    print(f'Dissolved CO2: {dissolved_co2} mol/kg')

