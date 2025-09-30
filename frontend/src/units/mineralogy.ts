export type FormationMineralogyUnit = 'moles' | 'w/w';

// Mineral molar masses (g/mol) - from Python backend
export const MINERAL_MOLAR_MASSES: Record<string, number> = {
  'Quartz': 60.083,
  'Albite': 262.14,
  'K-feldspar': 278.33,
  'Illite': 389.34,
  'Kaolinite': 258.16,
  'Calcite': 100.0869,
  'Dolomite': 184.40,
  'Siderite': 115.85,
  'Chlorite': 555.797,
  'Pyrite': 119.98,
  'Smectite': 367.86 // Average molar mass for smectite clay minerals
};

// Default total sample weight in grams (1 kg)
const TOTAL_SAMPLE_WEIGHT = 1000;

/**
 * Convert weight fractions to number of moles for each mineral
 * @param weightFractions - Weight fraction of each mineral (must sum to 1.0)
 * @param molarMasses - Molar mass of each mineral (g/mol)
 * @param totalWeight - Total weight of the sample (g), defaults to 1000g
 * @returns Number of moles for each mineral
 */
export function wtFracToMoles(
  weightFractions: Record<string, number>, 
  molarMasses: Record<string, number> = MINERAL_MOLAR_MASSES,
  totalWeight: number = TOTAL_SAMPLE_WEIGHT
): Record<string, number> {
  const moles: Record<string, number> = {};
  
  for (const [mineral, weightFrac] of Object.entries(weightFractions)) {
    if (mineral in molarMasses && molarMasses[mineral] > 0) {
      const mineralWeight = weightFrac * totalWeight;
      moles[mineral] = mineralWeight / molarMasses[mineral];
    } else {
      moles[mineral] = 0.0;
    }
  }
  
  return moles;
}

/**
 * Convert number of moles to weight fractions for each mineral
 * @param moles - Number of moles for each mineral
 * @param molarMasses - Molar mass of each mineral (g/mol)
 * @returns Weight fractions for each mineral (will sum to 1.0)
 */
export function molesToWtFrac(
  moles: Record<string, number>,
  molarMasses: Record<string, number> = MINERAL_MOLAR_MASSES
): Record<string, number> {
  // Calculate weight of each mineral
  const weights: Record<string, number> = {};
  let totalWeight = 0;
  
  for (const [mineral, nMoles] of Object.entries(moles)) {
    if (mineral in molarMasses) {
      const weight = nMoles * molarMasses[mineral];
      weights[mineral] = weight;
      totalWeight += weight;
    } else {
      weights[mineral] = 0.0;
    }
  }
  
  // Convert to weight fractions
  const weightFractions: Record<string, number> = {};
  if (totalWeight > 0) {
    for (const [mineral, weight] of Object.entries(weights)) {
      weightFractions[mineral] = weight / totalWeight;
    }
  } else {
    for (const mineral of Object.keys(moles)) {
      weightFractions[mineral] = 0.0;
    }
  }
  
  return weightFractions;
}

/**
 * Normalize weight fractions to sum to 1.0
 * @param weightFractions - Weight fractions to normalize
 * @returns Normalized weight fractions
 */
export function normalizeWeightFractions(weightFractions: Record<string, number>): Record<string, number> {
  const total = Object.values(weightFractions).reduce((sum, frac) => sum + frac, 0);
  
  if (total > 0) {
    const normalized: Record<string, number> = {};
    for (const [mineral, frac] of Object.entries(weightFractions)) {
      normalized[mineral] = frac / total;
    }
    return normalized;
  } else {
    return { ...weightFractions };
  }
}

/**
 * Formation mineralogy amounts conversion utilities
 */
export const formationMineralogyConversion = {
  /**
   * Get unit label for display
   */
  getUnitLabel(unit: FormationMineralogyUnit): string {
    switch (unit) {
      case 'moles': return 'moles';
      case 'w/w': return 'w/w';
    }
  },

  /**
   * Convert mineral values to moles unit
   * @param values - Current mineral values
   * @param fromUnit - Current unit
   * @returns Values converted to moles
   */
  toMoles(values: Record<string, number>, fromUnit: FormationMineralogyUnit): Record<string, number> {
    if (fromUnit === 'moles') {
      return { ...values }; // Already in moles, return copy
    } else if (fromUnit === 'w/w') {
      // Convert from weight fractions to moles
      return wtFracToMoles(values);
    }
    return values;
  },

  /**
   * Convert mineral values from moles to target unit
   * @param values - Values in moles
   * @param toUnit - Target unit
   * @returns Values converted to target unit
   */
  fromMoles(values: Record<string, number>, toUnit: FormationMineralogyUnit): Record<string, number> {
    if (toUnit === 'moles') {
      return { ...values }; // Already in moles, return copy
    } else if (toUnit === 'w/w') {
      // Convert from moles to weight fractions
      return molesToWtFrac(values);
    }
    return values;
  },

  /**
   * Convert mineral values between any two units
   * @param values - Current values
   * @param fromUnit - Current unit
   * @param toUnit - Target unit
   * @returns Values converted to target unit
   */
  convert(values: Record<string, number>, fromUnit: FormationMineralogyUnit, toUnit: FormationMineralogyUnit): Record<string, number> {
    if (fromUnit === toUnit) {
      return { ...values }; // Same unit, return copy
    }
    
    // Convert to moles first, then to target unit
    const molesValues = this.toMoles(values, fromUnit);
    return this.fromMoles(molesValues, toUnit);
  }
};