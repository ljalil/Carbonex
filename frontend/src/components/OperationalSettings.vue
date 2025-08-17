<template>
  <el-card class="operational-card">
    <template #header>
      <div class="card-header">
        <span>Pressure and Temperature</span>
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
        <span class="el-form-item__label unit-label">{{ temperatureUnitLabel }}</span>
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
        <span class="el-form-item__label unit-label">{{ pressureUnitLabel }}</span>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from "vue";
import { store, unitConversion } from "../store";
import {
  ElCard,
  ElForm,
  ElFormItem,
  ElInputNumber,
} from "element-plus";

export default defineComponent({
  name: "OperationalSettings",
  components: {
    ElCard,
    ElForm,
    ElFormItem,
    ElInputNumber,
  },
  setup() {
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
    
    const pressureUnitLabel = computed(() => {
      switch (store.unitPreferences.pressureUnit) {
        case 'bar': return 'bar';
        case 'atm': return 'atm';
        case 'psi': return 'psi';
        case 'mpa': return 'MPa';
        default: return 'bar';
      }
    });
    
    // Display temperature in the selected unit
    const displayedTemperature = ref(
      unitConversion.fromKelvin(store.simulationInput.temperature, store.unitPreferences.temperatureUnit)
    );
    
    // Display pressure in the selected unit
    const displayedPressure = ref(
      unitConversion.fromMPa(store.simulationInput.pressure, store.unitPreferences.pressureUnit)
    );
    
    const handleTemperatureChange = (
      current: number | undefined,
      previous: number | undefined
    ) => {
      // Convert from the displayed unit to Kelvin for storage, default to 0 if undefined
      const value = current ?? 0;
      store.simulationInput.temperature = unitConversion.toKelvin(
        value,
        store.unitPreferences.temperatureUnit
      );
    };

    const handlePressureChange = (new_value: number | undefined, old_value: number | undefined) => {
      // Convert from the displayed unit to MPa for storage
      store.simulationInput.pressure = unitConversion.toMPa(
        new_value ?? 0,
        store.unitPreferences.pressureUnit
      );
    };

    const updateTemperatureUnit = () => {
      // When unit changes, update displayed temperature
      displayedTemperature.value = unitConversion.fromKelvin(
        store.simulationInput.temperature,
        store.unitPreferences.temperatureUnit
      );
    };

    const updatePressureUnit = () => {
      // When unit changes, update displayed pressure
      displayedPressure.value = unitConversion.fromMPa(
        store.simulationInput.pressure,
        store.unitPreferences.pressureUnit
      );
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
      temperatureUnitLabel,
      temperatureMinValue,
      pressureUnitLabel,
      displayedTemperature,
      displayedPressure,
      handleTemperatureChange,
      handlePressureChange,
    };
  },
});
</script>

<style scoped>
.operational-card {
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
</style>