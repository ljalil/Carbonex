import axios from "axios";
import { store } from "./store"; // Adjust the path to your store

export async function runSimulationCO2BrineFixed() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      pressure: store.simulationInput.pressure,
      model: store.simulationInput.solubilityModel,
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/co2-brine/fixed",
      payload
    );

    if (response.data.status === "success" && response.data.data) {
      const trapped_co2 = response.data.data.trapped_co2;
      const co2Value = typeof trapped_co2 === 'string' 
        ? parseFloat(trapped_co2) 
        : Number(trapped_co2);
      
      if (!isNaN(co2Value)) {
        // CORRECT: Mutate the property directly
        store.simulationOutput.solubilityTrapping.trapped_co2 = co2Value;
      } else {
        console.error("Invalid dissolved CO2 value received:", trapped_co2);
      }
    } else {
      console.error("No valid trapped_co2 data in response:", response.data);
    }
  } catch (error) {
    console.error("Error during static simulation:", error);
  }
}

export async function runSimulationCO2BrineSolutionProperties() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      pressure: store.simulationInput.pressure,
      model: store.simulationInput.solubilityModel
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/co2-brine/solution-properties",
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
  }
}

export async function runSimulationCO2BrineVarP() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      model: store.simulationInput.solubilityModel
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/co2-brine/var-p",
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

export async function runSimulationCO2BrineVarT() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      pressure: store.simulationInput.pressure,
      model: store.simulationInput.solubilityModel
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/co2-brine/var-t",
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

export async function runSimulationCO2BrineRockSolutionProperties() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      pressure: store.simulationInput.pressure,
      mineralogy: store.simulationInput.minerals
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/co2-brine-rock/solution-properties",
      payload
    );

    console.log("Full API response for brine-rock solution properties:", response.data);

    // Check if the response has the expected structure
    if (response.data.status === "success" && response.data.data) {
      const responseData = response.data.data;

      // Update mineral trapping solution properties
      store.simulationOutput.mineralTrapping.density = parseFloat(responseData.density || 0);
      store.simulationOutput.mineralTrapping.ionic_strength = parseFloat(responseData.ionic_strength || 0);
      store.simulationOutput.mineralTrapping.pH = parseFloat(responseData.pH || 0);
      store.simulationOutput.mineralTrapping.activity_of_water = parseFloat(responseData.activity_of_water || 0);
      store.simulationOutput.mineralTrapping.osmotic_coefficient = parseFloat(responseData.osmotic_coefficient || 0);
      store.simulationOutput.mineralTrapping.fugacity_co2 = parseFloat(responseData.fugacity_co2 || 0);
      store.simulationOutput.mineralTrapping.partial_pressure_co2 = parseFloat(responseData.partial_pressure_co2 || 0);
      store.simulationOutput.mineralTrapping.speciesData = responseData.species_data || [];
      
      console.log("Mineral trapping solution properties updated successfully");
    } else {
      console.error("API returned error or unexpected structure:", response.data);
      throw new Error(`API Error: ${response.data.message || "Unknown error"}`);
    }

  } catch (error) {
    console.error("Error during brine-rock solution properties simulation:", error);
    // Reset values on error
    store.simulationOutput.mineralTrapping.density = 0;
    store.simulationOutput.mineralTrapping.ionic_strength = 0;
    store.simulationOutput.mineralTrapping.pH = 0;
    store.simulationOutput.mineralTrapping.activity_of_water = 0;
    store.simulationOutput.mineralTrapping.osmotic_coefficient = 0;
    store.simulationOutput.mineralTrapping.fugacity_co2 = 0;
    store.simulationOutput.mineralTrapping.partial_pressure_co2 = 0;
    store.simulationOutput.mineralTrapping.speciesData = [];
  }
}

export async function runSimulationCO2BrineRockFixed() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      pressure: store.simulationInput.pressure,
      mineralogy: store.simulationInput.minerals,
      model: store.simulationInput.primaryModel
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/co2-brine-rock/fixed",
      payload
    );

    if (response.data.status === "success" && response.data.data) {
      const data = response.data.data;
      
      // Store a snapshot of the initial minerals from when the simulation was run
      store.simulationOutput.mineralTrapping.initial_minerals = { ...store.simulationInput.minerals };
      
      store.simulationOutput.mineralTrapping.trapped_co2 = typeof data.trapped_co2 === 'string' 
        ? parseFloat(data.trapped_co2) 
        : Number(data.trapped_co2);
      
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
      trapped_co2: 0,
      density: 0,
      ionic_strength: 0,
      pH: 0,
      activity_of_water: 0,
      osmotic_coefficient: 0,
      fugacity_co2: 0,
      partial_pressure_co2: 0,
      speciesData: [],
      mineral_equi: {},
      initial_minerals: {},
      plotDataPressure: [],
      plotDataTemperature: []
    };
  }
}

export async function runSimulationCO2BrineRockVarP() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      temperature: store.simulationInput.temperature,
      mineralogy: store.simulationInput.minerals,
      model: store.simulationInput.primaryModel
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/co2-brine-rock/var-p",
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

export async function runSimulationCO2BrineRockVarT() {
  try {
    const payload = {
      concentrations: store.simulationInput.concentrations,
      pressure: store.simulationInput.pressure,
      mineralogy: store.simulationInput.minerals,
      model: store.simulationInput.primaryModel
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/simulate/co2-brine-rock/var-t",
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

export async function requestAIInsights() {
  try {
    // Extract species activities from speciesData
    const extractSpeciesActivities = (speciesData: Array<{species: string, activity: number, molar_volume: number}>) => {
      const activities: Record<string, number> = {};
      speciesData.forEach(species => {
        activities[species.species] = species.activity;
      });
      return activities;
    };

    // Prepare the payload with simulation data
    const payload = {
      pressure: store.simulationInput.pressure,
      temperature: store.simulationInput.temperature,
      solubilityTrapping: {
        trapped_co2: store.simulationOutput.solubilityTrapping.trapped_co2,
        density: store.simulationOutput.solubilityTrapping.density,
        ionic_strength: store.simulationOutput.solubilityTrapping.ionic_strength,
        pH: store.simulationOutput.solubilityTrapping.pH,
        speciesActivities: extractSpeciesActivities(store.simulationOutput.solubilityTrapping.speciesData)
      },
      mineralTrapping: {
        trapped_co2: store.simulationOutput.mineralTrapping.trapped_co2,
        density: store.simulationOutput.mineralTrapping.density,
        ionic_strength: store.simulationOutput.mineralTrapping.ionic_strength,
        pH: store.simulationOutput.mineralTrapping.pH,
        speciesActivities: extractSpeciesActivities(store.simulationOutput.mineralTrapping.speciesData),
        initial_minerals: store.simulationOutput.mineralTrapping.initial_minerals,
        mineral_equi: store.simulationOutput.mineralTrapping.mineral_equi
      }
    };

    const response = await axios.post(
      "http://127.0.0.1:5000/utilities/AI-insights",
      payload
    );

    if (response.data.status === "success" && response.data.data) {
      // Store the AI insights in the simulation output
      store.simulationOutput.aiInsights = response.data.data.insights || response.data.data;
      console.log("AI insights retrieved successfully:", store.simulationOutput.aiInsights);
    } else {
      console.error("AI insights request failed:", response.data);
      throw new Error(`AI Insights Error: ${response.data.message || "Unknown error"}`);
    }

  } catch (error) {
    console.error("Error during AI insights request:", error);
    // Reset AI insights on error
    store.simulationOutput.aiInsights = "";
  }
}