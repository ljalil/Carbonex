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
        store.simulationOutput.solubilityTrapping.total_dissolved_co2 = co2Value;
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

    console.log("Full API response:", response.data);

    // Check if the response has the expected structure
    if (response.data.status === "success" && response.data.data) {
      const responseData = response.data.data;

      // CORRECT: Update each property on the existing reactive object
      store.simulationOutput.solubilityTrapping.density = parseFloat(responseData.density || 0);
      store.simulationOutput.solubilityTrapping.ionic_strength = parseFloat(responseData.ionic_strength || 0);
      store.simulationOutput.solubilityTrapping.pH = parseFloat(responseData.pH || 0);
      store.simulationOutput.solubilityTrapping.activity_of_water = parseFloat(responseData.activity_of_water || 0);
      store.simulationOutput.solubilityTrapping.osmotic_coefficient = parseFloat(responseData.osmotic_coefficient || 0);
      store.simulationOutput.solubilityTrapping.fugacity_co2 = parseFloat(responseData.fugacity_co2 || 0);
      store.simulationOutput.solubilityTrapping.partial_pressure_co2 = parseFloat(responseData.partial_pressure_co2 || 0);
      store.simulationOutput.solubilityTrapping.speciesData = responseData.species_data || [];
    } else {
      console.error("API returned error or unexpected structure:", response.data);
      throw new Error(`API Error: ${response.data.message || "Unknown error"}`);
    }
    
    // IMPORTANT: Do NOT touch plotDataPressure or plotDataTemperature here, as this endpoint doesn't provide them.

  } catch (error) {
    console.error("Error during simulation:", error);
    // Reset values on error if needed, but do it property by property
    store.simulationOutput.solubilityTrapping.density = 0;
    store.simulationOutput.solubilityTrapping.ionic_strength = 0;
    store.simulationOutput.solubilityTrapping.pH = 0;
    store.simulationOutput.solubilityTrapping.activity_of_water = 0;
    store.simulationOutput.solubilityTrapping.osmotic_coefficient = 0;
    store.simulationOutput.solubilityTrapping.fugacity_co2 = 0;
    store.simulationOutput.solubilityTrapping.partial_pressure_co2 = 0;
    store.simulationOutput.solubilityTrapping.speciesData = [];
    // Do not reset plotDataPressure, plotDataTemperature or total_dissolved_co2 on this specific error
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

    // CORRECT: Update just the plotDataPressure property
    store.simulationOutput.solubilityTrapping.plotDataPressure = plotData;

    console.log("Plot data updated with varying pressure results:", store.simulationOutput.solubilityTrapping.plotDataPressure);

  } catch (error) {
    console.error("Error during varying pressure simulation:", error);
    // On error, reset only the pressure plot data
    store.simulationOutput.solubilityTrapping.plotDataPressure = [];
  }
}

export async function runSimulationWithVaryingTemperature() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      pressure: store.simulationInput.pressure,
      model: store.simulationInput.model
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/solubility/var-t",
      payload
    );

    const plotData = response.data.data.plot_data || [];

    // CORRECT: Update just the plotDataTemperature property
    store.simulationOutput.solubilityTrapping.plotDataTemperature = plotData;

    console.log("Plot data updated with varying temperature results:", store.simulationOutput.solubilityTrapping.plotDataTemperature);

  } catch (error) {
    console.error("Error during varying temperature simulation:", error);
    // On error, reset only the temperature plot data
    store.simulationOutput.solubilityTrapping.plotDataTemperature = [];
  }
}

export async function runSimulationWithVaryingPressureTemperature() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      model: store.simulationInput.model
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/solubility/var-pt",
      payload
    );

    const responseData = response.data.data;

    // CORRECT: Update the heatmap data
    store.simulationOutput.solubilityTrapping.heatmapData = {
      grid_data: responseData.grid_data || [],
      temperatures: responseData.temperatures || [],
      pressures: responseData.pressures || []
    };

    console.log("Heatmap data updated with varying pressure-temperature results:", store.simulationOutput.solubilityTrapping.heatmapData);

  } catch (error) {
    console.error("Error during varying pressure-temperature simulation:", error);
    // On error, reset the heatmap data
    store.simulationOutput.solubilityTrapping.heatmapData = {
      grid_data: [],
      temperatures: [],
      pressures: []
    };
  }
}