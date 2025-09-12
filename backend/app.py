from flask import Flask, request, jsonify
from flask_cors import CORS

from simulation import get_solution_properties, simulate_varying_pressure, simulate_varying_temperature, simulate_varying_pressure_temperature, run_state_simulation, _run_PHREEQC_brine_rock_single_state


import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/simulate/solution/properties', methods=['POST'])
def simulate_solution_properties():
    try:
        data = request.json

        temperature_unit = data.get('temperatureUnit')
        pressure_unit = data.get('pressureUnit')
        water_preset = data.get('waterPreset')
        concentrations = data.get('concentrations')
        temperature = data.get('temperature')
        pressure = data.get('pressure')

        

        species_data, density, ionic_strength, ph, osmotic_coefficient, partial_pressure_co2, fugacity_co2 = get_solution_properties(temperature=temperature, pressure=pressure, species=concentrations)

        response_data = {
            "density": density,
            "ionic_strength": ionic_strength,
            "pH": ph,
            "activity_of_water": 0.0,  # Set default value since it's not returned by the function
            "osmotic_coefficient": osmotic_coefficient,
            "species_data": species_data,
            "partial_pressure_co2": partial_pressure_co2,
            "fugacity_co2": fugacity_co2
        }

        return jsonify({
            "status": "success",
            "message": "Simulation completed successfully",
            "data": response_data
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@app.route('/simulate/solubility/var-p', methods=['POST'])
def simulate_solubility_var_p_endpoint():
    try:
        data = request.json

        temperature = data.get('temperature')
        concentrations = data.get('concentrations')
        model = data.get('model')
        print('running simulation with varying pressure, model', model,flush=True)
        
        # Call the simulate_varying_pressure function
        result = simulate_varying_pressure(temperature=temperature, ion_moles=concentrations, model=model)
        #print('returned results', result,flush=True)
        
        # Convert the result to the expected format for plotting
        plot_data = []
        for i in range(len(result['Pressure (MPa)'])):
            plot_data.append([result['Pressure (MPa)'][i], result['Dissolved CO2 (mol/kg)'][i]])
        
        response_data = {
            "plot_data": plot_data
        }

        print('this is the response data for plotting:')
        print(type(response_data['plot_data']), flush=True)
        print(type(response_data['plot_data'][0]), flush=True)
        print(type(response_data['plot_data'][0][0]), flush=True)
        #print(type(response_data['plot_data']['Pressure(MPa)']), flush=True)
        #print(type(response_data['plot_data']['Pressure(MPa)'][0]), flush=True)

        return jsonify({
            "status": "success",
            "message": "Simulation with varying pressure completed successfully",
            "data": response_data
        })

    except Exception as e:
        print(f"Error from varying pressure: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@app.route('/simulate/solubility/var-t', methods=['POST'])
def simulate_solubility_var_t_endpoint():
    try:
        data = request.json

        pressure = data.get('pressure')
        concentrations = data.get('concentrations')
        model = data.get('model')
        print('running simulation with varying temperature, model', model, flush=True)
        
        # Call the simulate_varying_temperature function
        result = simulate_varying_temperature(pressure=pressure, ion_moles=concentrations, model=model)
        
        # Convert the result to the expected format for plotting
        plot_data = []
        for i in range(len(result['Temperature (K)'])):
            plot_data.append([result['Temperature (K)'][i], result['Dissolved CO2 (mol/kg)'][i]])
        
        response_data = {
            "plot_data": plot_data
        }

        print('this is the response data for varying temperature plotting:')
        print(type(response_data['plot_data']), flush=True)
        print(type(response_data['plot_data'][0]), flush=True)
        print(type(response_data['plot_data'][0][0]), flush=True)

        return jsonify({
            "status": "success",
            "message": "Simulation with varying temperature completed successfully",
            "data": response_data
        })

    except Exception as e:
        print(f"Error from varying temperature: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@app.route('/simulate/solubility/var-pt', methods=['POST'])
def simulate_solubility_var_pt_endpoint():
    try:
        data = request.json

        concentrations = data.get('concentrations')
        model = data.get('model')
        print('running simulation with varying pressure and temperature, model', model, flush=True)
        
        # Call the simulate_varying_pressure_temperature function
        result = simulate_varying_pressure_temperature(ion_moles=concentrations, model=model)
        
        response_data = {
            "grid_data": result['grid_data'],
            "temperatures": result['temperatures'],
            "pressures": result['pressures']
        }

        print('this is the response data for pressure-temperature heatmap:')
        print(f'Grid data length: {len(response_data["grid_data"])}', flush=True)
        print(f'Temperature range: {len(response_data["temperatures"])} points', flush=True)
        print(f'Pressure range: {len(response_data["pressures"])} points', flush=True)

        return jsonify({
            "status": "success",
            "message": "Simulation with varying pressure and temperature completed successfully",
            "data": response_data
        })

    except Exception as e:
        print(f"Error from varying pressure-temperature: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@app.route('/simulate/solubility/fixed', methods=['POST'])
def simulate_solubility_fixed_endpoint():
    try:
        data = request.json

        temperature = data.get('temperature')
        pressure = data.get('pressure')
        concentrations = data.get('concentrations')
        model = data.get('model')
        
        # Call the run_state_simulation function to get only the dissolved CO2 value
        dissolved_co2 = run_state_simulation(
            temperature=temperature,
            pressure=pressure, 
            species=concentrations,
            model = model
        )
        
        response_data = {
            "dissolved_co2": dissolved_co2
        }

        return jsonify({
            "status": "success",
            "message": "State simulation completed successfully",
            "data": response_data
        })

    except Exception as e:
        print(f" from state simulation: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@app.route('/simulate/brine_rock/single_state', methods=['POST'])
def simulate_rock_brine_single_state_endpoint():
    try:
        data = request.json

        temperature = data.get('temperature')
        pressure = data.get('pressure')
        concentrations = data.get('concentrations')
        mineralogy = data.get('mineralogy', {})  # Dictionary of mineral names and initial moles
        model = data.get('model', 'phreeqc')  # Default to phreeqc database
        
        # Call the _run_PHREEQC_brine_rock_single_state function
        results = _run_PHREEQC_brine_rock_single_state(
            temperature=temperature,
            pressure=pressure,
            species=concentrations,
            mineralogy=mineralogy,
            model=model
        )
        
        response_data = {
            "dissolved_co2": results['dissolved_co2'],
            "density": results['density'],
            "ionic_strength": results['ionic_strength'],
            "ph": results['ph'],
            "osmotic_coefficient": results['osmotic_coefficient'],
            "partial_pressure_co2": results['partial_pressure_co2'],
            "fugacity_co2": results['fugacity_co2'],
            "mineral_deltas": results['mineral_deltas']
        }

        return jsonify({
            "status": "success",
            "message": "Brine-rock simulation completed successfully",
            "data": response_data
        })

    except Exception as e:
        print(f"Error from brine-rock simulation: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
