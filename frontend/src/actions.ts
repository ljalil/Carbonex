import axios from "axios";
import { store } from "./store"; // Adjust the path to your store

export async function runStaticSimulation() {
  try {
    // Values are already stored in Kelvin and MPa in the store, which are compatible with the backend
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature, // Already in Kelvin
      pressure: store.simulationInput.pressure, // Already in MPa
    };

    console.log("Sending static simulation request with:", {
      temperature: payload.temperature + "K",
      pressure: payload.pressure + "MPa",
      concentrations: payload.concentrations
    });

    const response = await axios.post(
      "http://127.0.0.1:5000/run_state_simulation",
      payload
    );

    console.log("Static simulation response:", response.data);

    // Update only the dissolved CO2 value in the store
    if (response.data.status === "success" && response.data.data) {
      const dissolved_co2 = response.data.data.dissolved_co2;
      console.log("Raw dissolved CO2 value:", dissolved_co2);
      
      // Ensure we have a valid number
      const co2Value = typeof dissolved_co2 === 'string' 
        ? parseFloat(dissolved_co2) 
        : Number(dissolved_co2);
      
      if (!isNaN(co2Value)) {
        store.simulationOutput.total_dissolved_co2 = co2Value;
        console.log("Total dissolved CO2 updated:", store.simulationOutput.total_dissolved_co2);
      } else {
        console.error("Invalid dissolved CO2 value received:", dissolved_co2);
      }
    } else {
      console.error("No valid dissolved_co2 data in response:", response.data);
    }
  } catch (error) {
    console.error("Error during static simulation:", error);
    // Don't update the store on error - keep existing values
  }
}

export async function runSimulation() {
  try {
    // Values are already stored in Kelvin and MPa in the store, which are compatible with the backend
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature, // Already in Kelvin
      pressure: store.simulationInput.pressure, // Already in MPa
      model: store.simulationInput.model // Include the selected model
    };

    console.log("Sending simulation request with:", {
      temperature: payload.temperature + "K",
      pressure: payload.pressure + "MPa",
      model: payload.model,
      concentrations: payload.concentrations
    });

    const response = await axios.post(
      "http://127.0.0.1:5000/solution_properties",
      payload
    );

    console.log("Simulation response:", response.data);

    // Process species data from response
    const formattedSpeciesData = response.data.data.species_data || [];

    // Use the plot data directly from the response with the correct key
    const plotData = response.data.data.plot_co2_solubility_pressure || [];

    // Update store with simulation results BUT preserve total_dissolved_co2 
    // which is handled by runStaticSimulation
    store.simulationOutput = {
      ...store.simulationOutput, // Keep existing total_dissolved_co2 value
      density: parseFloat(response.data.data.density || 0),
      ionic_strength: parseFloat(response.data.data.ionic_strength || 0),
      pH: parseFloat(response.data.data.pH || 0),
      activity_of_water: parseFloat(response.data.data.activity_of_water || 0),
      osmotic_coefficient: parseFloat(response.data.data.osmotic_coefficient || 0),
      speciesData: formattedSpeciesData,
      plotData: plotData
    };

    console.log("Simulation result updated:", store.simulationOutput);
  } catch (error) {
    console.error("Error during simulation:", error);
    // Don't reset total_dissolved_co2 on error
    const currentCO2 = store.simulationOutput.total_dissolved_co2;
    store.simulationOutput = { 
      total_dissolved_co2: currentCO2, // Preserve the existing value
      density: 0,
      ionic_strength: 0,
      pH: 0,
      activity_of_water: 0,
      osmotic_coefficient: 0,
      speciesData: [],
      plotData: []
    };
    console.error("Failed to run simulation");
  }
}

export async function runSimulationWithVaryingPressure() {
  try {
    // Values are already stored in Kelvin and MPa in the store
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature, // Already in Kelvin
      model: store.simulationInput.model // Include the selected model
    };

    console.log("Sending varying pressure simulation request with:", {
      temperature: payload.temperature + "K",
      model: payload.model,
      concentrations: payload.concentrations
    });

    const response = await axios.post(
      "http://127.0.0.1:5000/run_simulation_with_varying_pressure",
      payload
    );

    console.log("Varying pressure simulation response:", response.data);

    // Extract the plot data directly from the response
    const plotData = response.data.data.plot_data || [];

    // Update just the plotData in the store (keep other values unchanged)
    store.simulationOutput = {
      ...store.simulationOutput,
      plotData: plotData
    };

    console.log("Plot data updated with varying pressure results:", store.simulationOutput.plotData);
  } catch (error) {
    console.error("Error during varying pressure simulation:", error);
    store.simulationOutput = {
      ...store.simulationOutput,
      plotData: []
    };
    console.error("Failed to run varying pressure simulation");
  }
}
