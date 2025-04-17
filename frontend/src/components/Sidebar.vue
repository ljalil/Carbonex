<template>
  <el-card class="sidebar-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Simulation model</span>
      </div>
    </template>

    <el-form label-position="left" label-width="90px">
      <el-form-item label="Model">
        <el-select
          size="small"
          v-model="store.simulationInput.model"
          placeholder="Select model"
        >
          <el-option
            v-for="option in modelOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          ></el-option>
        </el-select>
      </el-form-item>
    </el-form>
  </el-card>

  <el-card class="sidebar-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Units settings</span>
      </div>
    </template>

    <el-form label-position="left" label-width="90px">
      <el-form-item label="Temperature">
        <el-select
          size="small"
          v-model="store.unitPreferences.temperatureUnit"
          placeholder="Select option"
          @change="updateTemperatureUnit"
        >
          <el-option
            v-for="option in temperatureUnits"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Pressure">
        <el-select
          size="small"
          v-model="store.unitPreferences.pressureUnit"
          placeholder="Select option"
          @change="updatePressureUnit"
        >
          <el-option
            v-for="option in pressureUnits"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          ></el-option>
        </el-select>
      </el-form-item>
    </el-form>
  </el-card>

  <el-card class="concentration-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Aqueous species</span>
      </div>
    </template>

    <el-form label-position="left">
      <el-form-item label="Preset">
        <el-select
          size="small"
          v-model="store.simulationInput.preset"
          placeholder="Select option"
          @change="updateWaterPreset"
        >
          <el-option
            v-for="option in ['Seawater', 'Freshwater', 'Brackish water']"
            :key="option"
            :label="option"
            :value="option"
          ></el-option>
        </el-select>
      </el-form-item>

      <el-form-item v-for="ion in ions" :key="ion">
        <span v-html="formatIonName(ion)" class="ion-label"></span>
        <el-input-number
          v-model="store.simulationInput.concentrations[ion]"
          size="small"
          :min="0"
          :precision="4"
          :step="0.1"
        />
        <span class="unit-label">mol/kg</span>
      </el-form-item>
    </el-form>
  </el-card>

  <el-card class="operational-card" shadow="neverhover">
    <template #header>
      <div class="card-header">
        <span>Operational variables</span>
      </div>
    </template>
    <el-form label-position="left" label-width="90px">
      <el-form-item label="Temperature">
        <el-input-number
          v-model="displayedTemperature"
          size="small"
          :min="temperatureMinValue"
          :precision="1"
          :step="1"
          @change="handleTemperatureChange"
        />
        <span class="unit-label">{{ temperatureUnitLabel }}</span>
      </el-form-item>

      <el-form-item label="Pressure">
        <el-input-number
          v-model="displayedPressure"
          size="small"
          :min="0"
          :precision="2"
          :step="1"
          @change="handlePressureChange"
        />
        <span class="unit-label">{{ pressureUnitLabel }}</span>
      </el-form-item>
    </el-form>
  </el-card>
</template>


<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from "vue";
import { store, unitConversion, type TemperatureUnit, type PressureUnit } from "../store"; // Import types and conversion utilities
import {
  ElCard,
  ElForm,
  ElFormItem,
  ElSelect,
  ElOption,
  ElInputNumber,
} from "element-plus";

export default defineComponent({
  name: "Sidebar",
  components: {
    ElCard,
    ElForm,
    ElFormItem,
    ElSelect,
    ElOption,
    ElInputNumber,
  },
  setup() {
const ions = [
      "Na+",
      "K+",
      "Cl-",
      "Mg+2",
      "Ca+2",
      "SO4-2",
    ];
    
    // Direct mapping of ion names to their HTML representation
    const ionNameMapping: Record<string, string> = {
      "Na+": "Na<sup>+</sup>",
      "K+": "K<sup>+</sup>",
      "Cl-": "Cl<sup>-</sup>",
      "Mg+2": "Mg<sup>+2</sup>",
      "Ca+2": "Ca<sup>+2</sup>",
      "SO4-2": "SO<sub>4</sub><sup>-2</sup>",
      "HCO3-": "HCO<sub>3</sub><sup>-</sup>",
      "CO3-2": "CO<sub>3</sub><sup>-2</sup>"
    };
    
    // Simple function to look up the formatted ion name
    const formatIonName = (ion: string) => {
      return ionNameMapping[ion] || ion; // Return mapped value or original if not found
    };
    
    // Model options
    const modelOptions = [
      { label: 'Carbonex', value: 'carbonex' },
      { label: 'PHREEQC (phreeqc.dat)', value: 'phreeqc_phreeqc' },
      { label: 'PHREEQC (pitzer.dat)', value: 'phreeqc_pitzer' },
      { label: 'Duan and Sun (2006)', value: 'duan_sun' }
    ];

    // Temperature unit handling
    const temperatureUnits = [
      { label: 'Kelvin (K)', value: 'kelvin' as TemperatureUnit },
      { label: 'Celsius (°C)', value: 'celsius' as TemperatureUnit },
      { label: 'Fahrenheit (°F)', value: 'fahrenheit' as TemperatureUnit }
    ];
    
    const temperatureUnitLabel = computed(() => {
      switch (store.unitPreferences.temperatureUnit) {
        case 'celsius': return '°C';
        case 'fahrenheit': return '°F';
        case 'kelvin': return 'K';
        default: return '°C';
      }
    });
    
    const temperatureMinValue = computed(() => {
      switch (store.unitPreferences.temperatureUnit) {
        case 'celsius': return -273.15;
        case 'fahrenheit': return -459.67;
        case 'kelvin': return 0;
        default: return -273.15;
      }
    });
    
    // Display temperature in the selected unit
    const displayedTemperature = ref(
      unitConversion.fromKelvin(store.simulationInput.temperature, store.unitPreferences.temperatureUnit)
    );
    
    const handleTemperatureChange = (value: number) => {
      // Convert from the displayed unit to Kelvin for storage
      store.simulationInput.temperature = unitConversion.toKelvin(
        value,
        store.unitPreferences.temperatureUnit
      );
    };

    const updateTemperatureUnit = () => {
      // When unit changes, update displayed temperature
      displayedTemperature.value = unitConversion.fromKelvin(
        store.simulationInput.temperature,
        store.unitPreferences.temperatureUnit
      );
    };

    // Pressure unit handling
    const pressureUnits = [
      { label: 'Megapascal (MPa)', value: 'mpa' as PressureUnit },
      { label: 'Bar', value: 'bar' as PressureUnit },
      { label: 'Atmosphere (atm)', value: 'atm' as PressureUnit },
      { label: 'PSI', value: 'psi' as PressureUnit }
    ];
    
    const pressureUnitLabel = computed(() => {
      switch (store.unitPreferences.pressureUnit) {
        case 'bar': return 'bar';
        case 'atm': return 'atm';
        case 'psi': return 'psi';
        case 'mpa': return 'MPa';
        default: return 'bar';
      }
    });
    
    // Display pressure in the selected unit
    const displayedPressure = ref(
      unitConversion.fromMPa(store.simulationInput.pressure, store.unitPreferences.pressureUnit)
    );
    
    const handlePressureChange = (value: number) => {
      // Convert from the displayed unit to MPa for storage
      store.simulationInput.pressure = unitConversion.toMPa(
        value,
        store.unitPreferences.pressureUnit
      );
    };

    const updatePressureUnit = () => {
      // When unit changes, update displayed pressure
      displayedPressure.value = unitConversion.fromMPa(
        store.simulationInput.pressure,
        store.unitPreferences.pressureUnit
      );
    };
    
    // Water preset handling
    const updateWaterPreset = (preset: string) => {
      console.log("Updating water preset to:", preset);
      
      if (preset === "Seawater") {
        // Update concentrations with seawater values
        store.simulationInput.concentrations["Na+"] = 0.4791;
        store.simulationInput.concentrations["K+"] = 0.009796;
        store.simulationInput.concentrations["Ca+2"] = 0.011478;
        store.simulationInput.concentrations["Mg+2"] = 0.026167;
        store.simulationInput.concentrations["Cl-"] = 0.5134;
        store.simulationInput.concentrations["SO4-2"] = 0.02021;
      }
      // We only have seawater preset for now, can add others later
    };
    
    // Watch for changes to the store's values or units
    watch(() => store.simulationInput.temperature, (newTemperature) => {
      displayedTemperature.value = unitConversion.fromKelvin(
        newTemperature, 
        store.unitPreferences.temperatureUnit
      );
    });
    
    watch(() => store.simulationInput.pressure, (newPressure) => {
      displayedPressure.value = unitConversion.fromMPa(
        newPressure, 
        store.unitPreferences.pressureUnit
      );
    });

    watch(() => store.unitPreferences.temperatureUnit, () => {
      updateTemperatureUnit();
    });

    watch(() => store.unitPreferences.pressureUnit, () => {
      updatePressureUnit();
    });
    
    // Initialize displayed values on mount
    onMounted(() => {
      displayedTemperature.value = unitConversion.fromKelvin(
        store.simulationInput.temperature, 
        store.unitPreferences.temperatureUnit
      );
      
      displayedPressure.value = unitConversion.fromMPa(
        store.simulationInput.pressure, 
        store.unitPreferences.pressureUnit
      );
    });

    return {
      store,
ions,
      formatIonName,
      modelOptions,
      temperatureUnits,
      temperatureUnitLabel,
      temperatureMinValue,
      displayedTemperature,
      handleTemperatureChange,
      updateTemperatureUnit,
      pressureUnits,
      pressureUnitLabel,
      displayedPressure,
      handlePressureChange,
      updatePressureUnit,
      updateWaterPreset,
    };
  },
});
</script>

<style scoped>
.sidebar-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
}

.unit-label {
  margin-left: 10px;
}

.ion-label {
  display: inline-block;
  width: 65px;
  margin-right: 5px;

  text-align: left;
}

.el-select,
.el-select-dropdown__item {
  font-family: "Roboto", sans-serif;
}



h1 {
  font-weight: 100;
  margin: 10px 0px;
}
</style>
