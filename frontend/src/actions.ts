import axios from "axios";
import { store } from "./store"; // Adjust the path to your store

export async function runStaticSimulation() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      pressure: store.simulationInput.pressure,
      model: store.simulationInput.model,
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/solubility/fixed",
      payload
    );

    if (response.data.status === "success" && response.data.data) {
      const dissolved_co2 = response.data.data.dissolved_co2;
      const co2Value = typeof dissolved_co2 === 'string' 
        ? parseFloat(dissolved_co2) 
        : Number(dissolved_co2);
      
      if (!isNaN(co2Value)) {
        // CORRECT: Mutate the property directly
        store.simulationOutput.total_dissolved_co2 = co2Value;
      } else {
        console.error("Invalid dissolved CO2 value received:", dissolved_co2);
      }
    } else {
      console.error("No valid dissolved_co2 data in response:", response.data);
    }
  } catch (error) {
    console.error("Error during static simulation:", error);
  }
}

export async function runSimulation() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      pressure: store.simulationInput.pressure,
      model: store.simulationInput.model
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/solution/properties",
      payload
    );

    const responseData = response.data.data;

    // CORRECT: Update each property on the existing reactive object
    store.simulationOutput.density = parseFloat(responseData.density || 0);
    store.simulationOutput.ionic_strength = parseFloat(responseData.ionic_strength || 0);
    store.simulationOutput.pH = parseFloat(responseData.pH || 0);
    store.simulationOutput.activity_of_water = parseFloat(responseData.activity_of_water || 0);
    store.simulationOutput.osmotic_coefficient = parseFloat(responseData.osmotic_coefficient || 0);
    store.simulationOutput.speciesData = responseData.species_data || [];
    
    // IMPORTANT: Do NOT touch plotData here, as this endpoint doesn't provide it.

  } catch (error) {
    console.error("Error during simulation:", error);
    // Reset values on error if needed, but do it property by property
    store.simulationOutput.density = 0;
    store.simulationOutput.ionic_strength = 0;
    store.simulationOutput.pH = 0;
    store.simulationOutput.activity_of_water = 0;
    store.simulationOutput.osmotic_coefficient = 0;
    store.simulationOutput.speciesData = [];
    // Do not reset plotData or total_dissolved_co2 on this specific error
  }
}

export async function runSimulationWithVaryingPressure() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      model: store.simulationInput.model
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/solubility/var-p",
      payload
    );

    const plotData = response.data.data.plot_data || [];

    // CORRECT: Update just the plotData property
    store.simulationOutput.plotData = plotData;

    console.log("Plot data updated with varying pressure results:", store.simulationOutput.plotData);

  } catch (error) {
    console.error("Error during varying pressure simulation:", error);
    // On error, reset only the plot data
    store.simulationOutput.plotData = [];
  }
}