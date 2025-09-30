// Re-export all unit types and conversions for easy importing
export * from './temperature';
export * from './pressure';
export * from './concentration';
export * from './mineralogy';

// CO2 critical point constants (combining temperature and pressure)
export const CO2_CRITICAL_POINT = {
  temperature: 304.18, // Kelvin
  pressure: 7.38 // MPa
} as const;

import { temperatureConversion } from './temperature';
import { pressureConversion } from './pressure';
import { CO2_CRITICAL_PRESSURE } from './pressure';

/**
 * Utility functions that combine multiple unit types
 */
export const combinedConversions = {
  /**
   * Check if CO2 is in supercritical conditions
   */
  isCO2Supercritical(temperatureK: number, pressureMPa: number): boolean {
    return temperatureK > CO2_CRITICAL_POINT.temperature && pressureMPa > CO2_CRITICAL_POINT.pressure;
  }
};