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

import requests
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

        trapped_co2 = simulate_co2_brine_fixed(
            temperature=temperature,
            pressure=pressure,
            species=concentrations,
            model=model,
        )


        response_data = {
            "trapped_co2": trapped_co2,
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
            "trapped_co2": results["trapped_co2"],
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
def get_AI_insights():
    try:
        data = request.json
        
        # Extract data from payload
        pressure = data.get("pressure", 0)
        temperature = data.get("temperature", 0)
        solubility_trapping = data.get("solubilityTrapping", {})
        mineral_trapping = data.get("mineralTrapping", {})
        
        # Extract solubility trapping data
        sol_trapped_co2 = solubility_trapping.get("trapped_co2", 0)
        sol_density = solubility_trapping.get("density", 0)
        sol_ionic_strength = solubility_trapping.get("ionic_strength", 0)
        sol_pH = solubility_trapping.get("pH", 0)
        sol_species_activities = solubility_trapping.get("speciesActivities", {})
        
        # Extract mineral trapping data
        min_trapped_co2 = mineral_trapping.get("trapped_co2", 0)
        min_density = mineral_trapping.get("density", 0)
        min_ionic_strength = mineral_trapping.get("ionic_strength", 0)
        min_pH = mineral_trapping.get("pH", 0)
        min_species_activities = mineral_trapping.get("speciesActivities", {})
        initial_minerals = mineral_trapping.get("initial_minerals", {})
        final_minerals = mineral_trapping.get("mineral_equi", {})
        
        # Format species activities for prompt
        def format_activities(activities):
            return "\n".join([f"-- {species}: {activity:.4f}" for species, activity in activities.items()])
        
        # Format mineral changes for prompt
        def format_mineral_changes(initial, final):
            changes = []
            all_minerals = set(initial.keys()) | set(final.keys())
            for mineral in all_minerals:
                init_val = initial.get(mineral, 0)
                final_val = final.get(mineral, 0)
                changes.append(f"-- {mineral}: {init_val:.4f} -> {final_val:.4f}")
            return "\n".join(changes)
        
        # Convert temperature from Kelvin to Celsius for more intuitive analysis
        temp_celsius = temperature - 273.15
        
        prompt = f"""I conducted a simulation for CO2 solubility and mineralization under specific pressure and temperature conditions. I will give you the results and you give me a brief description of main findings and your remarks on this simulation results. This is intended to be embedded in a UI for the user as an AI summary, so skip any introductory text and keep it brief and formal. Provide insights into the geochemistry to the end user rather than just providing a commentary on the results.

IMPORTANT: If the provided data contains unrealistic values (such as no dissolved CO2, pH=0, negative densities, or other physically impossible values), simply return a short sentence stating that the simulation data appears to contain invalid or unrealistic values that should be verified.

=== Pressure and Temperature ===
- Pressure: {pressure:.2f} MPa ({pressure * 10:.1f} bar)
- Temperature: {temperature:.2f} K ({temp_celsius:.1f}°C)

=== Solubility Trapping Only ===
- Solution density: {sol_density:.4f} g/cm³
- Ionic strength: {sol_ionic_strength:.4f} mol/kgw
- pH: {sol_pH:.2f}
- Dissolved CO2 due to solubility only: {sol_trapped_co2:.4f} mol/kgw
- Species activities:
{format_activities(sol_species_activities)}

=== Solubility + Mineral Trapping ===
- Solution density: {min_density:.4f} g/cm³
- Ionic strength: {min_ionic_strength:.4f} mol/kgw
- pH: {min_pH:.2f}
- Dissolved CO2 due to solubility and mineralization: {min_trapped_co2:.4f} mol/kgw
- Species activities:
{format_activities(min_species_activities)}
- Formation mineralogy changes (moles):
{format_mineral_changes(initial_minerals, final_minerals)}

=== Additional Analysis Points ===
- CO2 enhancement due to mineralization: {(min_trapped_co2 - sol_trapped_co2):.4f} mol/kgw ({((min_trapped_co2 - sol_trapped_co2) / sol_trapped_co2 * 100) if sol_trapped_co2 > 0 else 0:.1f}% increase)
- pH change due to mineralization: {(min_pH - sol_pH):.2f} units
- Density change: {(min_density - sol_density):.4f} g/cm³
- Ionic strength change: {(min_ionic_strength - sol_ionic_strength):.4f} mol/kgw"""

        # For now, return the prompt as the insight (placeholder for actual AI integration)
        # In a real implementation, you would send this prompt to an AI service

        print(prompt, flush=True)
        
        # Call Google Gemini API
        try:
            gemini_api_key = "AIzaSyD3VruK6S0PlADDWdbc_xXuw9QhkBD71tM"
            gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': gemini_api_key
            }
            
            gemini_payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            # Make request to Gemini API
            gemini_response = requests.post(gemini_url, headers=headers, json=gemini_payload, timeout=30)
            
            if gemini_response.status_code == 200:
                gemini_data = gemini_response.json()
                
                # Extract the AI-generated text from the response
                if (gemini_data.get("candidates") and 
                    len(gemini_data["candidates"]) > 0 and
                    gemini_data["candidates"][0].get("content") and
                    gemini_data["candidates"][0]["content"].get("parts") and
                    len(gemini_data["candidates"][0]["content"]["parts"]) > 0):
                    
                    ai_insights = gemini_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                else:
                    ai_insights = "Unable to generate AI insights - invalid response format."
            else:
                print(f"Gemini API error: {gemini_response.status_code} - {gemini_response.text}")
                ai_insights = f"Simulation Analysis at {pressure:.1f} MPa and {temp_celsius:.0f}°C: The CO2 solubility shows {sol_trapped_co2:.2f} mol/kgw under brine-only conditions with pH {sol_pH:.1f}. Mineral-brine interactions increase CO2 storage to {min_trapped_co2:.2f} mol/kgw (+{((min_trapped_co2 - sol_trapped_co2) / sol_trapped_co2 * 100) if sol_trapped_co2 > 0 else 0:.1f}%) while buffering pH to {min_pH:.1f}. Key geochemical processes include mineral dissolution/precipitation affecting solution chemistry and CO2 speciation."
                
        except requests.exceptions.RequestException as e:
            print(f"Error calling Gemini API: {e}")
            # Fallback response
            ai_insights = f"Simulation Analysis at {pressure:.1f} MPa and {temp_celsius:.0f}°C: The CO2 solubility shows {sol_trapped_co2:.2f} mol/kgw under brine-only conditions with pH {sol_pH:.1f}. Mineral-brine interactions increase CO2 storage to {min_trapped_co2:.2f} mol/kgw (+{((min_trapped_co2 - sol_trapped_co2) / sol_trapped_co2 * 100) if sol_trapped_co2 > 0 else 0:.1f}%) while buffering pH to {min_pH:.1f}. Key geochemical processes include mineral dissolution/precipitation affecting solution chemistry and CO2 speciation."
        
        response_data = {
            "insights": ai_insights
        }
        
        return jsonify({
            "status": "success",
            "message": "AI insights generated successfully",
            "data": response_data
        })
        
    except Exception as e:
        print(f"Error generating AI insights: {e}")
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
