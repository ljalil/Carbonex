export type PressureUnit = 'bar' | 'atm' | 'psi' | 'mpa';

// CO2 critical pressure (stored in MPa as internal format)
export const CO2_CRITICAL_PRESSURE = 7.38; // MPa

/**
 * Pressure conversion utilities
 */
export const pressureConversion = {
  /**
   * Convert from any pressure unit to MPa (internal storage format)
   */
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
  
  /**
   * Convert from MPa to any pressure unit (for display)
   */
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
  },

  /**
   * Get unit label for display
   */
  getUnitLabel(unit: PressureUnit): string {
    switch (unit) {
      case 'bar': return 'bar';
      case 'atm': return 'atm';
      case 'psi': return 'psi';
      case 'mpa': return 'MPa';
    }
  }
};