from flask import Flask, request, jsonify
#from flask_cors import CORS
import numpy as np

app = Flask(__name__)
#CORS(app)


@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    try:
        data = request.json

        temperature_unit = data.get('temperatureUnit')
        pressure_unit = data.get('pressureUnit')
        water_preset = data.get('waterPreset')
        concentrations = data.get('concentrations')
        temperature = data.get('temperature')
        pressure = data.get('pressure')



        



        # Dummy calculation for dissolved CO2 values
        # Change these values after training the model

        total_dissolved_co2 = 1.23
        density = 3.0
        ionic_strength = 1.940e+00
        ph = 3.5
        activity_of_water = 3.5
        osmotic_coefficient = 3.5
        species_data = {
            "Na+": {"Activity": 0.78, "Molar volume": 11},
            "Cl-": {"Activity": 0.89, "Molar volume": 10},
            "K+": {"Activity": 0.89, "Molar volume": 10},
            "Mg2+": {"Activity": 5, "Molar volume": 10},
            "Ca2+": {"Activity": 1, "Molar volume": 10},
            "SO4-2": {"Activity": 1, "Molar volume": 10},
            "HCO3-": {"Activity": 1, "Molar volume": 10},
            "CO3-2": {"Activity": 1, "Molar volume": 10}
        }

        if pressure is None or pressure <= 0:
            pressure = 1  # Default to 1 to avoid issues

        try:
            # Generate pressures and dissolved CO2 values
            pressures = np.linspace(0, pressure, 10)
            dissolved_co2_values = [np.sin(p / pressure) * 100 for p in pressures]

            plot_data = {
                'x': pressures.tolist(),
                'y': dissolved_co2_values
            }
        except Exception as e:
            print(f"Error calculating plot data: {e}")
            plot_data = {'x': [], 'y': []}


        response_data = {

            "Total dissolved CO2": f"{total_dissolved_co2} mol/kg",
            "Density": f"{density} g/cm3",
            "Ionic strength": f"{ionic_strength} mol/kgw",
            "pH": ph,
            "Activity of water": activity_of_water,
            "Osmotic coefficient": osmotic_coefficient,
            "Species": species_data,
            "PlotData": plot_data
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

if __name__ == '__main__':
    app.run(debug=True)
