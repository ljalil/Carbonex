from flask import Flask, request, jsonify
from flask_cors import CORS

from simulation import get_solution_properties, simulate_varying_pressure, run_state_simulation


import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/solution_properties', methods=['POST'])
def solution_properties():
    try:
        data = request.json

        temperature_unit = data.get('temperatureUnit')
        pressure_unit = data.get('pressureUnit')
        water_preset = data.get('waterPreset')
        concentrations = data.get('concentrations')
        temperature = data.get('temperature')
        pressure = data.get('pressure')

        

        species_data, density, ionic_strength, ph, activity_of_water, osmotic_coefficient = get_solution_properties(temperature=temperature, pressure=pressure, species=concentrations)

        response_data = {
            "density": density,
            "ionic_strength": ionic_strength,
            "pH": ph,
            "activity_of_water": activity_of_water,
            "osmotic_coefficient": osmotic_coefficient,
            "species_data": species_data,
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


@app.route('/run_simulation_with_varying_pressure', methods=['POST'])
def run_simulation_with_varying_pressure():
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


@app.route('/run_state_simulation', methods=['POST'])
def run_state_simulation_endpoint():
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

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
