import { reactive } from "vue";
import { 
  type TemperatureUnit, 
  type PressureUnit, 
  type WaterChemistryUnit, 
  type FormationMineralogyUnit,
  temperatureConversion,
  pressureConversion,
  combinedConversions,
  CO2_CRITICAL_POINT,
  waterChemistryConversion
} from './units';

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
  Pyrite: number;
}

interface SpeciesData {
  species: string;
  activity: number;
  molar_volume: number;
}

export interface SolubilityTrapping {
  trapped_co2: number;
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
  trapped_co2: number;
  density: number;
  ionic_strength: number;
  pH: number;
  activity_of_water: number;
  osmotic_coefficient: number;
  fugacity_co2: number;
  partial_pressure_co2: number;
  speciesData: SpeciesData[];
  mineral_equi: Record<string, number>; 
  initial_minerals: Record<string, number>; 
  plotDataPressure: [number, number][];
  plotDataTemperature: [number, number][];
}

interface SimulationOutput {
  solubilityTrapping: SolubilityTrapping;
  mineralTrapping: MineralTrapping;
  aiInsights?: string;
}

// Define available unit types (imported from units module)
export type { TemperatureUnit, PressureUnit, WaterChemistryUnit, FormationMineralogyUnit } from './units';
// Backward compatibility aliases
export type ConcentrationUnit = WaterChemistryUnit;
export type MineralogyUnit = FormationMineralogyUnit;
export type PrimaryModelType = 'phreeqc_phreeqc' | 'phreeqc_pitzer';
export type SolubilityModelType = 'phreeqc_phreeqc' | 'phreeqc_pitzer' | 'duan_sun_2006' | 'carbonex';
export type CorrosionModelType = 'deWaald1991' | 'deWaald1995';

// CO2 critical point constants (imported from units module)
export { CO2_CRITICAL_POINT } from './units';

interface SimulationInput {
  temperature: number; // Always stored in Kelvin (backend compatible)
  pressure: number; // Always stored in MPa (backend compatible)
  concentrations: Concentrations;
  preset?: string;
  primaryModel: PrimaryModelType;
  solubilityModel: SolubilityModelType;
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
  concentrationUnit: WaterChemistryUnit;
  mineralogyUnit: FormationMineralogyUnit;
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
    primaryModel: 'phreeqc_phreeqc', // Default model
    solubilityModel:'duan_sun_2006',
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
    Chlorite: 0,
    Pyrite: 0
  }
  },
  simulationOutput: {
    solubilityTrapping: {
      trapped_co2: 0,
      density: 0,
      ionic_strength: 0,
      pH: 0,
      activity_of_water: 0,
      osmotic_coefficient: 0,
      fugacity_co2: 0,
      partial_pressure_co2: 0,
      speciesData: [],
      plotDataPressure: [],
      plotDataTemperature: [],
      heatmapData: {
        grid_data: [],
        temperatures: [],
        pressures: []
      }
    },
    mineralTrapping: {
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
    },
    aiInsights: '' // Will be populated by backend AI analysis
  },
  unitPreferences: {
  temperatureUnit: 'kelvin',
  pressureUnit: 'mpa',
  concentrationUnit: 'mol/kg',
  mineralogyUnit: 'moles'
  }
});

// Unit conversion utility functions (now imported from dedicated unit modules)
export { temperatureConversion, pressureConversion, combinedConversions, waterChemistryConversion };

// Store methods for unit conversion
export const storeActions = {
  /**
   * Convert water chemistry concentrations when unit preference changes
   */
  convertWaterChemistryUnits(
    fromUnit: WaterChemistryUnit, 
    toUnit: WaterChemistryUnit,
    temperature: number = 298.15 // Default to 25°C in Kelvin
  ) {
    const tempC = temperature - 273.15; // Convert Kelvin to Celsius for conversion calculations
    
    // Convert all concentrations
    store.simulationInput.concentrations = waterChemistryConversion.convert(
      store.simulationInput.concentrations,
      fromUnit,
      toUnit,
      tempC
    );
    
    // Update the unit preference
    store.unitPreferences.concentrationUnit = toUnit;
  },

  /**
   * Get current temperature in Celsius for conversions
   */
  getCurrentTemperatureC(): number {
    return store.simulationInput.temperature - 273.15;
  }
};
