export type TemperatureUnit = 'celsius' | 'fahrenheit' | 'kelvin';

// Temperature critical points and constants
export const TEMPERATURE_CONSTANTS = {
  ABSOLUTE_ZERO_CELSIUS: -273.15,
  ABSOLUTE_ZERO_FAHRENHEIT: -459.67,
  ABSOLUTE_ZERO_KELVIN: 0
} as const;

/**
 * Temperature conversion utilities
 */
export const temperatureConversion = {
  /**
   * Convert from any temperature unit to Kelvin (internal storage format)
   */
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
  
  /**
   * Convert from Kelvin to any temperature unit (for display)
   */
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

  /**
   * Get minimum allowed value for temperature input based on unit
   */
  getMinValue(unit: TemperatureUnit): number {
    switch (unit) {
      case 'celsius': return TEMPERATURE_CONSTANTS.ABSOLUTE_ZERO_CELSIUS;
      case 'fahrenheit': return TEMPERATURE_CONSTANTS.ABSOLUTE_ZERO_FAHRENHEIT;
      case 'kelvin': return TEMPERATURE_CONSTANTS.ABSOLUTE_ZERO_KELVIN;
    }
  },

  /**
   * Get unit label for display
   */
  getUnitLabel(unit: TemperatureUnit): string {
    switch (unit) {
      case 'celsius': return '°C';
      case 'fahrenheit': return '°F';
      case 'kelvin': return 'K';
    }
  }
};