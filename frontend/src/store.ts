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

interface StreamImpurities {
    "CO2": number;
    "O2": number;
    "H2S": number;
    "Hydrogen": number;
    "Nitrogen": number;
}
// Formation mineralogy inputs
interface Minerals {
  Quartz: number;
  Albite: number;
  "K-feldspar": number;
  Illite: number;
  Kaolinite: number;
  Calcite: number;
  Dolomite: number;
  Siderite: number;
  Chlorite: number;
}

interface SpeciesData {
  species: string;
  activity: number;
  molar_volume: number;
}

export interface SolubilityTrapping {
  total_dissolved_co2: number;
  density: number;
  ionic_strength: number;
  pH: number;
  activity_of_water: number;
  osmotic_coefficient: number;
  fugacity_co2: number;
  partial_pressure_co2: number;
  speciesData: SpeciesData[];
  plotDataPressure: [number, number][]; // Array of [pressure, CO2] pairs for variable pressure plot
  plotDataTemperature: [number, number][]; // Array of [temperature, CO2] pairs for variable temperature plot
  heatmapData: {
    grid_data: [number, number, number][]; // Array of [temp_index, pressure_index, CO2] for heatmap
    temperatures: number[]; // Temperature values in Kelvin
    pressures: number[]; // Pressure values in MPa
  };
}

export interface MineralTrapping {
  dissolved_co2: number;
  density: number;
  ionic_strength: number;
  pH: number;
  osmotic_coefficient: number;
  fugacity_co2: number;
  partial_pressure_co2: number;
  mineral_equi: Record<string, number>; // Dictionary of mineral deltas
  plotDataPressure: [number, number][]; // Array of [pressure, dissolved_co2] pairs
  plotDataTemperature: [number, number][]; // Array of [temperature, dissolved_co2] pairs
}

interface SimulationOutput {
  solubilityTrapping: SolubilityTrapping;
  mineralTrapping: MineralTrapping;
}

// Define available unit types
export type TemperatureUnit = 'celsius' | 'fahrenheit' | 'kelvin';
export type PressureUnit = 'bar' | 'atm' | 'psi' | 'mpa';
// Available concentration units for input/output
export type ConcentrationUnit = 'mol/kg' | 'mol/L' | 'ppm';
export type ModelType = 'phreeqc_phreeqc' | 'phreeqc_pitzer' | 'duan_sun_2006' | 'carbonex';
export type CorrosionModelType = 'deWaald1991' | 'deWaald1995';

interface SimulationInput {
  temperature: number; // Always stored in Kelvin (backend compatible)
  pressure: number; // Always stored in MPa (backend compatible)
  concentrations: Concentrations;
  preset?: string;
  model: ModelType;
  corrosionModel: CorrosionModelType;
  considerImpurities: boolean;
  streamImpurities: StreamImpurities;
  minerals: Minerals;
  /** Selected mineralogy preset */
  mineralogyPreset?: string;
}

interface UnitPreferences {
  temperatureUnit: TemperatureUnit;
  pressureUnit: PressureUnit;
  concentrationUnit: ConcentrationUnit;
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
    model: 'duan_sun_2006', // Default model
    corrosionModel: 'deWaald1991',
  considerImpurities: false,
  streamImpurities: {
        "CO2": 1,
        "O2": 0,
        "H2S": 0,
        "Hydrogen": 0,
        "Nitrogen": 0,
  },
  minerals: {
    Quartz: 0,
    Albite: 0,
    "K-feldspar": 0,
    Illite: 0,
    Kaolinite: 0,
    Calcite: 0,
    Dolomite: 0,
    Siderite: 0,
    Chlorite: 0
  }
  },
  simulationOutput: {
    solubilityTrapping: {
      total_dissolved_co2: 0,
      density: 0,
      ionic_strength: 0,
      pH: 0,
      activity_of_water: 0,
      osmotic_coefficient: 0,
      fugacity_co2: 0,
      partial_pressure_co2: 0,
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
      plotDataPressure: [],
      plotDataTemperature: [],
      heatmapData: {
        grid_data: [],
        temperatures: [],
        pressures: []
      }
    },
    mineralTrapping: {
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
    }
  },
  unitPreferences: {
  temperatureUnit: 'kelvin',
  pressureUnit: 'mpa',
  concentrationUnit: 'mol/kg'
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
