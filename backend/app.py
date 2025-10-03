from flask import Flask, request, jsonify
from flask_cors import CORS

from co2_brine_simulation import (
    simulate_co2_brine_solution_properties,
    simulate_co2_brine_fixed,
    simulate_co2_brine_var_p,
    simulate_co2_brine_var_t,
)

from co2_brine_rock_simulation import (
    simulate_co2_brine_rock_solution_properties,
    simulate_co2_brine_rock_fixed,
    simulate_co2_brine_rock_var_p,
    simulate_co2_brine_rock_var_t,
)


import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/simulate/co2-brine/solution-properties", methods=["POST"])
def simulate_co2_brine_solution_properties_endpoint():
    try:
        data = request.json

        temperature_unit = data.get("temperatureUnit")
        pressure_unit = data.get("pressureUnit")
        water_preset = data.get("waterPreset")
        concentrations = data.get("concentrations")
        temperature = data.get("temperature")
        pressure = data.get("pressure")

        (
            species_data,
            density,
            ionic_strength,
            pH,
            osmotic_coefficient,
            partial_pressure_co2,
            fugacity_co2,
        ) = simulate_co2_brine_solution_properties(
            temperature=temperature, pressure=pressure, species=concentrations
        )

        response_data = {
            "density": density,
            "ionic_strength": ionic_strength,
            "pH": pH,
            "activity_of_water": 0.0,  # Set default value since it's not returned by the function
            "osmotic_coefficient": osmotic_coefficient,
            "species_data": species_data,
            "partial_pressure_co2": partial_pressure_co2,
            "fugacity_co2": fugacity_co2,
        }

        return jsonify(
            {
                "status": "success",
                "message": "Simulation completed successfully",
                "data": response_data,
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/simulate/co2-brine/var-p", methods=["POST"])
def simulate_co2_brine_var_p_endpoint():
    try:
        data = request.json

        temperature = data.get("temperature")
        concentrations = data.get("concentrations")
        model = data.get("model")

        result = simulate_co2_brine_var_p(
            temperature=temperature, ion_moles=concentrations, model=model
        )
        # print('returned results', result,flush=True)

        # Convert the result to the expected format for plotting
        plot_data = []
        for i in range(len(result["Pressure (MPa)"])):
            plot_data.append(
                [result["Pressure (MPa)"][i], result["Dissolved CO2 (mol/kg)"][i]]
            )

        response_data = {"plot_data": plot_data}

        # print(type(response_data['plot_data']['Pressure(MPa)']), flush=True)
        # print(type(response_data['plot_data']['Pressure(MPa)'][0]), flush=True)

        return jsonify(
            {
                "status": "success",
                "message": "Simulation with varying pressure completed successfully",
                "data": response_data,
            }
        )

    except Exception as e:
        print(f"Error from varying pressure: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/simulate/co2-brine/var-t", methods=["POST"])
def simulate_co2_brine_var_t_endpoint():
    try:
        data = request.json

        pressure = data.get("pressure")
        concentrations = data.get("concentrations")
        model = data.get("model")

        result = simulate_co2_brine_var_t(
            pressure=pressure, ion_moles=concentrations, model=model
        )

        # Convert the result to the expected format for plotting
        plot_data = []
        for i in range(len(result["Temperature (K)"])):
            plot_data.append(
                [result["Temperature (K)"][i], result["Dissolved CO2 (mol/kg)"][i]]
            )

        response_data = {"plot_data": plot_data}

        return jsonify(
            {
                "status": "success",
                "message": "Simulation with varying temperature completed successfully",
                "data": response_data,
            }
        )

    except Exception as e:
        print(f"Error from varying temperature: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/simulate/co2-brine/fixed", methods=["POST"])
def simulate_co2_brine_fixed_endpoint():
    try:
        data = request.json

        temperature = data.get("temperature")
        pressure = data.get("pressure")
        concentrations = data.get("concentrations")
        model = data.get("model")

        dissolved_co2 = simulate_co2_brine_fixed(
            temperature=temperature,
            pressure=pressure,
            species=concentrations,
            model=model,
        )


        response_data = {
            "total_dissolved_co2": dissolved_co2,
        }

        return jsonify(
            {
                "status": "success",
                "message": "State simulation completed successfully",
                "data": response_data,
            }
        )

    except Exception as e:
        print(f" from state simulation: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/simulate/co2-brine-rock/solution-properties", methods=["POST"])
def simulate_co2_brine_rock_solution_properties_endpoint():
    try:
        data = request.json

        temperature = data.get("temperature")
        pressure = data.get("pressure")
        concentrations = data.get("concentrations")
        mineralogy = data.get("mineralogy", {})

        (
            species_data,
            density,
            ionic_strength,
            pH,
            osmotic_coefficient,
            partial_pressure_co2,
            fugacity_co2,
        ) = simulate_co2_brine_rock_solution_properties(
            temperature=temperature, 
            pressure=pressure, 
            species=concentrations,
            minerals=mineralogy
        )

        response_data = {
            "density": density,
            "ionic_strength": ionic_strength,
            "pH": pH,
            "activity_of_water": 0.0,  # Placeholder for water activity
            "osmotic_coefficient": osmotic_coefficient,
            "species_data": species_data,
            "partial_pressure_co2": partial_pressure_co2,
            "fugacity_co2": fugacity_co2,
        }

        return jsonify(
            {
                "status": "success",
                "message": "Brine-rock solution properties simulation completed successfully",
                "data": response_data,
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/simulate/co2-brine-rock/fixed", methods=["POST"])
def simulate_co2_rock_brine_single_state_endpoint():
    try:
        data = request.json

        temperature = data.get("temperature")
        pressure = data.get("pressure")
        concentrations = data.get("concentrations")
        mineralogy = data.get(
            "mineralogy", {}
        )  # Dictionary of mineral names and initial moles
        model = data.get("model", "phreeqc")  # Default to phreeqc database

        results = simulate_co2_brine_rock_fixed(
            temperature=temperature,
            pressure=pressure,
            species=concentrations,
            mineralogy=mineralogy,
            model=model,
        )

        response_data = {
            "dissolved_co2": results["dissolved_co2"],
            "mineral_equi": results["mineral_equi"],
        }

        return jsonify(
            {
                "status": "success",
                "message": "Brine-rock simulation completed successfully",
                "data": response_data,
            }
        )

    except Exception as e:
        print(f"Error from brine-rock simulation: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/simulate/co2-brine-rock/var-p", methods=["POST"])
def simulate_co2_brine_rock_var_p_endpoint():
    try:
        data = request.json

        temperature = data.get("temperature")
        concentrations = data.get("concentrations")
        mineralogy = data.get("mineralogy", {})
        model = data.get("model", "phreeqc")

        result = simulate_co2_brine_rock_var_p(
            temperature=temperature,
            ion_moles=concentrations,
            mineralogy=mineralogy,
            model=model,
        )

        # Convert the result to the expected format for plotting
        plot_data = []
        for i in range(len(result["Pressure (MPa)"])):
            plot_data.append(
                [result["Pressure (MPa)"][i], result["Dissolved CO2 (mol/kg)"][i]]
            )

        response_data = {"plot_data": plot_data}

        return jsonify(
            {
                "status": "success",
                "message": "Mineralization simulation with varying pressure completed successfully",
                "data": response_data,
            }
        )

    except Exception as e:
        print(f"Error from mineralization varying pressure: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/simulate/co2-brine-rock/var-t", methods=["POST"])
def simulate_co2_brine_rock_var_t_endpoint():
    try:
        data = request.json

        pressure = data.get("pressure")
        concentrations = data.get("concentrations")
        mineralogy = data.get("mineralogy", {})
        model = data.get("model", "phreeqc")

        result = simulate_co2_brine_rock_var_t(
            pressure=pressure,
            ion_moles=concentrations,
            mineralogy=mineralogy,
            model=model,
        )

        # Convert the result to the expected format for plotting
        plot_data = []
        for i in range(len(result["Temperature (K)"])):
            plot_data.append(
                [result["Temperature (K)"][i], result["Dissolved CO2 (mol/kg)"][i]]
            )

        response_data = {"plot_data": plot_data}

        return jsonify(
            {
                "status": "success",
                "message": "Mineralization simulation with varying temperature completed successfully",
                "data": response_data,
            }
        )

    except Exception as e:
        print(f"Error from mineralization varying temperature: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/utilities/AI-insights", methods=["POST"])
def get_AI_insights(pressure, temperature, concentrations):
    prompt = f"I conducted a simulation for CO2 solubility and mineralization under a certain pressure and temperature conditions. I will give you the results and you give me a brief description of main findings and your remarks on this simulation results. This is intended to be embedded in a UI for the user as an AI summary, so skip any introductory text and keep it brief and formal. Provide insights into the geochemistry to the end user rather than just providing a commentary on the results. === Pressure and temperature === - Pressure: {pressure} MPa - temperature: {temperature} K === solubility === - Initial brine composition (mol/kgw): -- Na+: 0.4690 -- K+: 0.0102 -- Cl-: 0.5460 -- Mg+2: 0.0528 -- Ca+2: 0.0103 -- SO4-2: 0.0282 - Solution density: 1.0346 g/cm - Ionic strength: 0.6927 mol/kgw - pH: 3.1205 - Activity coefficients: -- Na+: 0.6717 -- Cl-: 0.6269 -- K+: 0.1189 -- Mg+2: 0.1820 -- Ca+2: 0.0864 -- SO4-2: 0.0789 -- HCO3-:0.0448 -- CO3-2: 0 - Dissolved CO2 due to solubility only: 1.1640 mol/kgw === solubility + mineralization === - Solution density: 1.0539 g/cm - Ionic strength: 0.8929 mol/kgw - pH: 5.4812 - Formation mineralogy change (moles): -- Quartz: 0.25 -> 0.9099 -- Albite: 0.1 -> 0 -- K-feldspar: 0.05 -> 0 -- Illite: 0.3 -> 0 -- Kaolinite: 0.1 -> 0.52 -- Calcite: 0.05 -> 0 -- Dolomite: 0.05 -> 0.10952 - Dissolved CO2 due to solubility and mineralization: 1.5133 mol/kgw"


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
