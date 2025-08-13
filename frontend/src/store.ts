import { reactive } from "vue";

interface Concentrations {
    "Na+": number;
    "K+": number;
    "Cl-": number;
    "Mg+2": number;
    "Ca+2": number;
    "SO4-2": number;
    "HCO3-": number;
    "CO3-2": number;
}

interface SpeciesData {
  species: string;
  activity: number;
  molar_volume: number;
}

interface SimulationOutput {
  total_dissolved_co2: number;
  density: number;
  ionic_strength: number;
  pH: number;
  activity_of_water: number;
  osmotic_coefficient: number;
  speciesData: SpeciesData[];
  plotData: [number, number][]; // Array of [x, y] pairs for the pressure vs CO2 solubility plot
}

// Define available unit types
export type TemperatureUnit = 'celsius' | 'fahrenheit' | 'kelvin';
export type PressureUnit = 'bar' | 'atm' | 'psi' | 'mpa';
export type ModelType = 'phreeqc_phreeqc' | 'phreeqc_pitzer' | 'duan_sun_2006' | 'carbonex';

interface SimulationInput {
  temperature: number; // Always stored in Kelvin (backend compatible)
  pressure: number; // Always stored in MPa (backend compatible)
  concentrations: Concentrations;
  preset?: string;
  model: ModelType;
}

interface UnitPreferences {
  temperatureUnit: TemperatureUnit;
  pressureUnit: PressureUnit;
}

export const store = reactive<{
  simulationInput: SimulationInput;
  simulationOutput: SimulationOutput;
  unitPreferences: UnitPreferences;
}>({
  simulationInput: {
    temperature: 298.15, // 25°C in Kelvin
    pressure: 0.98, // 9.8 bar in MPa
    concentrations: {
        "Na+": 0,
        "K+": 0,
        "Cl-": 0,
        "Mg+2": 0,
        "Ca+2": 0,
        "SO4-2": 0,
        "HCO3-": 0,
        "CO3-2": 0
    },
    model: 'carbonex' // Default model
  },
  simulationOutput: {
    total_dissolved_co2: 0,
    density: 0,
    ionic_strength: 0,
    pH: 0,
    activity_of_water: 0,
    osmotic_coefficient: 0,
    speciesData: [
      { species: "Na+", activity: 0, molar_volume: 0 },
      { species: "Cl-", activity: 0, molar_volume: 0 },
      { species: "K+", activity: 0, molar_volume: 0 },
      { species: "Mg+2", activity: 0, molar_volume: 0 },
      { species: "Ca+2", activity: 0, molar_volume: 0 },
      { species: "SO4-2", activity: 0, molar_volume: 0 },
      { species: "HCO3-", activity: 0, molar_volume: 0 },
      { species: "CO3-2", activity: 0, molar_volume: 0 },
    ],
    plotData: []
  },
  unitPreferences: {
    temperatureUnit: 'kelvin',
    pressureUnit: 'mpa'
  }
});

// Unit conversion utility functions that can be used throughout the application
export const unitConversion = {
  // Convert from any temperature unit to Kelvin
  toKelvin(value: number, fromUnit: TemperatureUnit): number {
    switch (fromUnit) {
      case 'celsius': 
        return value + 273.15;
      case 'fahrenheit': 
        return (value - 32) * 5/9 + 273.15;
      case 'kelvin':
        return value;
    }
  },
  
  // Convert from Kelvin to any temperature unit
  fromKelvin(value: number, toUnit: TemperatureUnit): number {
    switch (toUnit) {
      case 'celsius': 
        return value - 273.15;
      case 'fahrenheit': 
        return (value - 273.15) * 9/5 + 32;
      case 'kelvin':
        return value;
    }
  },

  // Convert from any pressure unit to MPa
  toMPa(value: number, fromUnit: PressureUnit): number {
    switch (fromUnit) {
      case 'bar': 
        return value * 0.1; // 1 bar = 0.1 MPa
      case 'atm': 
        return value * 0.101325; // 1 atm = 0.101325 MPa
      case 'psi': 
        return value * 0.00689476; // 1 psi = 0.00689476 MPa
      case 'mpa':
        return value;
    }
  },
  
  // Convert from MPa to any pressure unit
  fromMPa(value: number, toUnit: PressureUnit): number {
    switch (toUnit) {
      case 'bar': 
        return value * 10; // 1 MPa = 10 bar
      case 'atm': 
        return value / 0.101325; // 1 MPa = 9.86923 atm
      case 'psi': 
        return value / 0.00689476; // 1 MPa = 145.038 psi
      case 'mpa':
        return value;
    }
  }
};
