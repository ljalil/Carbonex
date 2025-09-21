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
      const dissolved_co2 = response.data.data.total_dissolved_co2;
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

export async function runBrineRockSimulation() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      pressure: store.simulationInput.pressure,
      mineralogy: store.simulationInput.minerals,
      model: store.simulationInput.model
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/brine_rock/single_state",
      payload
    );

    if (response.data.status === "success" && response.data.data) {
      const data = response.data.data;
      
      // Update mineralTrapping with all returned values
      store.simulationOutput.mineralTrapping.dissolved_co2 = typeof data.dissolved_co2 === 'string' 
        ? parseFloat(data.dissolved_co2) 
        : Number(data.dissolved_co2);
      store.simulationOutput.mineralTrapping.density = typeof data.density === 'string' 
        ? parseFloat(data.density) 
        : Number(data.density);
      store.simulationOutput.mineralTrapping.ionic_strength = typeof data.ionic_strength === 'string' 
        ? parseFloat(data.ionic_strength) 
        : Number(data.ionic_strength);
      store.simulationOutput.mineralTrapping.pH = typeof data.pH === 'string' 
        ? parseFloat(data.pH) 
        : Number(data.pH);
      store.simulationOutput.mineralTrapping.osmotic_coefficient = typeof data.osmotic_coefficient === 'string' 
        ? parseFloat(data.osmotic_coefficient) 
        : Number(data.osmotic_coefficient);
      store.simulationOutput.mineralTrapping.fugacity_co2 = typeof data.fugacity_co2 === 'string' 
        ? parseFloat(data.fugacity_co2) 
        : Number(data.fugacity_co2);
      store.simulationOutput.mineralTrapping.partial_pressure_co2 = typeof data.partial_pressure_co2 === 'string' 
        ? parseFloat(data.partial_pressure_co2) 
        : Number(data.partial_pressure_co2);
      
      // Handle mineral equilibrium data
      store.simulationOutput.mineralTrapping.mineral_equi = data.mineral_equi || {};

      console.log("Brine-rock simulation completed successfully:", store.simulationOutput.mineralTrapping);
    } else {
      console.error("No valid data in brine-rock simulation response:", response.data);
    }
  } catch (error) {
    console.error("Error during brine-rock simulation:", error);
    // On error, reset to default values
    store.simulationOutput.mineralTrapping = {
      dissolved_co2: 0,
      density: 0,
      ionic_strength: 0,
      pH: 0,
      osmotic_coefficient: 0,
      fugacity_co2: 0,
      partial_pressure_co2: 0,
      mineral_equi: {},
      plotDataPressure: [],
      plotDataTemperature: []
    };
  }
}

export async function runMineralizationWithVaryingPressure() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      mineralogy: store.simulationInput.minerals,
      model: store.simulationInput.model
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/mineralization/var-p",
      payload
    );

    const plotData = response.data.data.plot_data || [];

    // Update the plotDataPressure property
    store.simulationOutput.mineralTrapping.plotDataPressure = plotData;

    console.log("Mineral trapping plot data updated with varying pressure results:", store.simulationOutput.mineralTrapping.plotDataPressure);

  } catch (error) {
    console.error("Error during mineral trapping varying pressure simulation:", error);
    // On error, reset only the pressure plot data
    store.simulationOutput.mineralTrapping.plotDataPressure = [];
  }
}

export async function runMineralizationWithVaryingTemperature() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      pressure: store.simulationInput.pressure,
      mineralogy: store.simulationInput.minerals,
      model: store.simulationInput.model
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/mineralization/var-t",
      payload
    );

    const plotData = response.data.data.plot_data || [];

    // Update the plotDataTemperature property
    store.simulationOutput.mineralTrapping.plotDataTemperature = plotData;

    console.log("Mineral trapping plot data updated with varying temperature results:", store.simulationOutput.mineralTrapping.plotDataTemperature);

  } catch (error) {
    console.error("Error during mineral trapping varying temperature simulation:", error);
    // On error, reset only the temperature plot data
    store.simulationOutput.mineralTrapping.plotDataTemperature = [];
  }
}

export async function runMineralizationFixedState() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      pressure: store.simulationInput.pressure,
      mineralogy: store.simulationInput.minerals,
      model: store.simulationInput.model
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/mineralization/fixed",
      payload
    );

    if (response.data.status === "success" && response.data.data) {
      const data = response.data.data;
      
      // Update mineralTrapping with all returned values
      store.simulationOutput.mineralTrapping.dissolved_co2 = typeof data.dissolved_co2 === 'string' 
        ? parseFloat(data.dissolved_co2) 
        : Number(data.dissolved_co2);
      store.simulationOutput.mineralTrapping.density = typeof data.density === 'string' 
        ? parseFloat(data.density) 
        : Number(data.density);
      store.simulationOutput.mineralTrapping.ionic_strength = typeof data.ionic_strength === 'string' 
        ? parseFloat(data.ionic_strength) 
        : Number(data.ionic_strength);
      store.simulationOutput.mineralTrapping.pH = typeof data.pH === 'string' 
        ? parseFloat(data.pH) 
        : Number(data.pH);
      store.simulationOutput.mineralTrapping.osmotic_coefficient = typeof data.osmotic_coefficient === 'string' 
        ? parseFloat(data.osmotic_coefficient) 
        : Number(data.osmotic_coefficient);
      store.simulationOutput.mineralTrapping.fugacity_co2 = typeof data.fugacity_co2 === 'string' 
        ? parseFloat(data.fugacity_co2) 
        : Number(data.fugacity_co2);
      store.simulationOutput.mineralTrapping.partial_pressure_co2 = typeof data.partial_pressure_co2 === 'string' 
        ? parseFloat(data.partial_pressure_co2) 
        : Number(data.partial_pressure_co2);
      
      // Handle mineral equilibrium data
      store.simulationOutput.mineralTrapping.mineral_equi = data.mineral_equi || {};

      console.log("Mineralization simulation completed successfully:", store.simulationOutput.mineralTrapping);
    } else {
      console.error("No valid data in mineralization response:", response.data);
    }
  } catch (error) {
    console.error("Error during mineralization fixed state simulation:", error);
  }
}