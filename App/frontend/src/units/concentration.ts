export type WaterChemistryUnit = 'mol/kg' | 'mol/L' | 'mg/L';

// Ion data types - using the exact ion names from the store
export interface IonConcentrations {
  "Na+": number;
  "K+": number;
  "Cl-": number;
  "Mg+2": number;
  "Ca+2": number;
  "SO4-2": number;
  "HCO3-": number;
  "CO3-2": number;
}

// Generic interface for internal conversions
export interface GenericIonConcentrations {
  [ion: string]: number;
}

// Typical partial molar volumes at 25 °C in cm^3/mol (literature averages)
const partialMolarVolumes: Record<string, number> = {
  "Na+": 16.6,
  "K+": 25.0,
  "Ca+2": -24.4,
  "Mg+2": -19.6,
  "Cl-": 16.6,
  "SO4-2": -20.1,
  "HCO3-": 28.5,
  "CO3-2": 41.5,
};

// Molar masses in g/mol
const molarMasses: Record<string, number> = {
  "Na+": 22.99,
  "K+": 39.10,
  "Ca+2": 40.08,
  "Mg+2": 24.31,
  "Cl-": 35.45,
  "SO4-2": 96.06,
  "HCO3-": 61.02,
  "CO3-2": 60.01,
};

/**
 * Estimate solution density from ion concentrations in mg/L
 * Returns density in g/cm^3
 */
function solutionDensity(concentrationsMgL: GenericIonConcentrations, tempC: number = 25.0): number {
  const rhoW = 0.99987 + 6.69e-5 * tempC - 8.0e-6 * tempC * tempC;
  const mW = rhoW * 1000.0;
  const nW = mW / 18.015;
  const VW = nW * 18.015;

  let mS = 0.0;
  let VS = 0.0;
  
  for (const [ion, concMgL] of Object.entries(concentrationsMgL)) {
    if (!(ion in molarMasses) || !(ion in partialMolarVolumes)) {
      throw new Error(`Missing data for ion ${ion}`);
    }
    const M = molarMasses[ion];
    const Vm = partialMolarVolumes[ion];
    const nI = (concMgL / 1000.0) / M; // mol/L
    const mI = nI * M;
    const VI = nI * Vm;
    mS += mI;
    VS += VI;
  }

  const mTotal = mW + mS;
  const VTotal = VW + VS;
  return mTotal / VTotal;
}

/**
 * Convert mg/L to mol/L
 */
function mgLToMolarity(concentrationsMgL: GenericIonConcentrations): GenericIonConcentrations {
  const molarities: GenericIonConcentrations = {};
  for (const [ion, concMgL] of Object.entries(concentrationsMgL)) {
    const M = molarMasses[ion];
    molarities[ion] = (concMgL / 1000.0) / M;
  }
  return molarities;
}

/**
 * Convert mol/L to mg/L
 */
function molarityToMgL(concentrationsMolL: GenericIonConcentrations): GenericIonConcentrations {
  const mgL: GenericIonConcentrations = {};
  for (const [ion, concMolL] of Object.entries(concentrationsMolL)) {
    const M = molarMasses[ion];
    mgL[ion] = concMolL * M * 1000.0;
  }
  return mgL;
}

/**
 * Convert mg/L to mol/kg water
 */
function mgLToMolality(concentrationsMgL: GenericIonConcentrations, tempC: number = 25.0): GenericIonConcentrations {
  const rho = solutionDensity(concentrationsMgL, tempC);
  const rhoGL = rho * 1000.0;
  const mSolutes = Object.values(concentrationsMgL).reduce((sum, conc) => sum + (conc / 1000.0), 0);
  const mWater = rhoGL - mSolutes;
  const kgWater = mWater / 1000.0;

  const molalities: GenericIonConcentrations = {};
  for (const [ion, concMgL] of Object.entries(concentrationsMgL)) {
    const M = molarMasses[ion];
    const nI = (concMgL / 1000.0) / M;
    const bI = nI / kgWater;
    molalities[ion] = bI;
  }
  return molalities;
}

/**
 * Convert mol/kg water to mol/L solution
 */
function molalityToMolarity(concentrationsMolkg: GenericIonConcentrations, tempC: number = 25.0): GenericIonConcentrations {
  // Use iterative approach to account for solution density properly
  // Start with an initial approximation: assume density ≈ 1 g/mL
  let previousDensity = 1.0;
  let currentDensity = 1.0;
  let iterations = 0;
  const maxIterations = 10;
  const convergenceThreshold = 0.0001;

  let molarities: GenericIonConcentrations = {};
  
  do {
    previousDensity = currentDensity;
    
    // Calculate molarities based on current density estimate
    molarities = {};
    for (const [ion, molality] of Object.entries(concentrationsMolkg)) {
      if (molality > 0) {
        // Convert molality to molarity using current density estimate
        // M = m * ρ / (1 + Σ(m_i * MW_i / 1000))
        // where ρ is solution density in g/mL
        const totalMass = Object.entries(concentrationsMolkg).reduce((sum, [i, m]) => {
          return sum + (m * molarMasses[i] / 1000.0); // kg solute per kg water
        }, 0);
        
        molarities[ion] = molality * currentDensity / (1 + totalMass);
      } else {
        molarities[ion] = 0;
      }
    }
    
    // Calculate new density estimate from current molarities
    const mgLConcentrations: GenericIonConcentrations = {};
    for (const [ion, molarity] of Object.entries(molarities)) {
      mgLConcentrations[ion] = molarity * molarMasses[ion] * 1000.0;
    }
    
    currentDensity = solutionDensity(mgLConcentrations, tempC);
    iterations++;
    
  } while (Math.abs(currentDensity - previousDensity) > convergenceThreshold && iterations < maxIterations);
  
  return molarities;
}

/**
 * Convert mol/L to mol/kg water
 */
function molarityToMolality(concentrationsMolL: GenericIonConcentrations, tempC: number = 25.0): GenericIonConcentrations {
  // Convert mol/L to mg/L first
  const concentrationsMgL = molarityToMgL(concentrationsMolL);
  return mgLToMolality(concentrationsMgL, tempC);
}

/**
 * Convert mol/kg to ppm (mg/L)
 */
function molalityToPpm(concentrationsMolkg: GenericIonConcentrations, tempC: number = 25.0): GenericIonConcentrations {
  // First convert to mg/L via molarity
  const molarities = molalityToMolarity(concentrationsMolkg, tempC);
  return molarityToMgL(molarities);
}

/**
 * Convert ppm (mg/L) to mol/kg
 */
function ppmToMolality(concentrationsPpm: GenericIonConcentrations, tempC: number = 25.0): GenericIonConcentrations {
  return mgLToMolality(concentrationsPpm, tempC);
}

/**
 * Convert mol/L to ppm (mg/L)
 */
function molarityToPpm(concentrationsMolL: GenericIonConcentrations): GenericIonConcentrations {
  return molarityToMgL(concentrationsMolL);
}

/**
 * Convert ppm (mg/L) to mol/L
 */
function ppmToMolarity(concentrationsPpm: GenericIonConcentrations): GenericIonConcentrations {
  return mgLToMolarity(concentrationsPpm);
}

/**
 * Convert between the specific IonConcentrations interface and generic
 */
function toGeneric(concentrations: IonConcentrations): GenericIonConcentrations {
  return { ...concentrations };
}

function fromGeneric(concentrations: GenericIonConcentrations): IonConcentrations {
  return {
    "Na+": concentrations["Na+"] || 0,
    "K+": concentrations["K+"] || 0,
    "Cl-": concentrations["Cl-"] || 0,
    "Mg+2": concentrations["Mg+2"] || 0,
    "Ca+2": concentrations["Ca+2"] || 0,
    "SO4-2": concentrations["SO4-2"] || 0,
    "HCO3-": concentrations["HCO3-"] || 0,
    "CO3-2": concentrations["CO3-2"] || 0,
  };
}

/**
 * Water chemistry concentration conversion utilities
 */
export const waterChemistryConversion = {
  /**
   * Get unit label for display
   */
  getUnitLabel(unit: WaterChemistryUnit): string {
    switch (unit) {
      case 'mol/kg': return 'mol/kg';
      case 'mol/L': return 'mol/L';
      case 'mg/L': return 'mg/L';
    }
  },

  /**
   * Convert concentrations from one unit to another
   */
  convert(
    concentrations: IonConcentrations,
    fromUnit: WaterChemistryUnit,
    toUnit: WaterChemistryUnit,
    tempC: number = 25.0
  ): IonConcentrations {
    if (fromUnit === toUnit) {
      return { ...concentrations };
    }

    const genericConcentrations = toGeneric(concentrations);

    // Convert from source unit to mol/kg (our base unit)
    let molalityConcentrations: GenericIonConcentrations;
    switch (fromUnit) {
      case 'mol/kg':
        molalityConcentrations = { ...genericConcentrations };
        break;
      case 'mol/L':
        molalityConcentrations = molarityToMolality(genericConcentrations, tempC);
        break;
      case 'mg/L':
        molalityConcentrations = ppmToMolality(genericConcentrations, tempC);
        break;
    }

    // Convert from mol/kg to target unit
    let result: GenericIonConcentrations;
    switch (toUnit) {
      case 'mol/kg':
        result = molalityConcentrations;
        break;
      case 'mol/L':
        result = molalityToMolarity(molalityConcentrations, tempC);
        break;
      case 'mg/L':
        result = molalityToPpm(molalityConcentrations, tempC);
        break;
    }

    return fromGeneric(result);
  },

  /**
   * Convert a single concentration value between units
   */
  convertSingle(
    value: number,
    ion: keyof IonConcentrations,
    fromUnit: WaterChemistryUnit,
    toUnit: WaterChemistryUnit,
    tempC: number = 25.0
  ): number {
    if (fromUnit === toUnit) {
      return value;
    }

    const singleConcentration: IonConcentrations = {
      "Na+": ion === "Na+" ? value : 0,
      "K+": ion === "K+" ? value : 0,
      "Cl-": ion === "Cl-" ? value : 0,
      "Mg+2": ion === "Mg+2" ? value : 0,
      "Ca+2": ion === "Ca+2" ? value : 0,
      "SO4-2": ion === "SO4-2" ? value : 0,
      "HCO3-": ion === "HCO3-" ? value : 0,
      "CO3-2": ion === "CO3-2" ? value : 0,
    };
    
    const converted = this.convert(singleConcentration, fromUnit, toUnit, tempC);
    return converted[ion];
  }
};