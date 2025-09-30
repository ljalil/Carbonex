<template>
  <el-card class="operational-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Pressure and Temperature</span>
      </div>
    </template>
    <el-form label-position="left" label-width="auto">
      <el-form-item label="Temperature">

          <el-input-number
            v-model="displayedTemperature"
            size="small"
            :min="temperatureMinValue"
            :precision="1"
            :step="1"
            @change="handleTemperatureChange"
            style="flex: 1">
                    <template #suffix>
        <span>{{ temperatureUnitLabel }}</span>
      </template>
          </el-input-number>

      </el-form-item>

      <el-form-item label="Pressure">
          <el-input-number
            v-model="displayedPressure"
            size="small"
            :min="0"
            :precision="2"
            :step="1"
            @change="handlePressureChange"
            style="flex: 1">
          <template #suffix>
        <span>{{ pressureUnitLabel }}</span>
      </template>
          </el-input-number>

      </el-form-item>
    </el-form>

    <!--<CO2PhaseDiagram></CO2PhaseDiagram>-->

       <template #footer>
      <el-alert 
        :title="isSupercritical ? 'Supercritical state' : 'Subcritical state'"
        center
        :type="isSupercritical ? 'success' : 'warning'"
        show-icon 
        :closable="false" 
      />
    </template>
  </el-card>
  
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { store, unitConversion, CO2_CRITICAL_POINT } from '../store'
import CO2PhaseDiagram from './CO2PhaseDiagram.vue'

// Unit labels
const temperatureUnitLabel = computed(() => {
  switch (store.unitPreferences.temperatureUnit) {
    case 'celsius': return '°C'
    case 'fahrenheit': return '°F'
    case 'kelvin': return 'K'
    default: return '°C'
  }
})
const temperatureMinValue = computed(() => {
  switch (store.unitPreferences.temperatureUnit) {
    case 'celsius': return -273.15
    case 'fahrenheit': return -459.67
    case 'kelvin': return 0
    default: return -273.15
  }
})
const pressureUnitLabel = computed(() => {
  switch (store.unitPreferences.pressureUnit) {
    case 'bar': return 'bar'
    case 'atm': return 'atm'
    case 'psi': return 'psi'
    case 'mpa': return 'MPa'
    default: return 'bar'
  }
})

// Check if CO2 is in supercritical conditions
const isSupercritical = computed(() => {
  return unitConversion.isCO2Supercritical(store.simulationInput.temperature, store.simulationInput.pressure)
})

// Displayed values
const displayedTemperature = ref(unitConversion.fromKelvin(store.simulationInput.temperature, store.unitPreferences.temperatureUnit))
const displayedPressure = ref(unitConversion.fromMPa(store.simulationInput.pressure, store.unitPreferences.pressureUnit))

// Update handlers
const handleTemperatureChange = (current: number | undefined) => {
  store.simulationInput.temperature = unitConversion.toKelvin(current ?? 0, store.unitPreferences.temperatureUnit)
}
const handlePressureChange = (current: number | undefined) => {
  store.simulationInput.pressure = unitConversion.toMPa(current ?? 0, store.unitPreferences.pressureUnit)
}

// Watch for changes
watch(() => store.simulationInput.temperature, val => {
  displayedTemperature.value = unitConversion.fromKelvin(val, store.unitPreferences.temperatureUnit)
})
watch(() => store.simulationInput.pressure, val => {
  displayedPressure.value = unitConversion.fromMPa(val, store.unitPreferences.pressureUnit)
})
watch(() => store.unitPreferences.temperatureUnit, () => {
  displayedTemperature.value = unitConversion.fromKelvin(store.simulationInput.temperature, store.unitPreferences.temperatureUnit)
})
watch(() => store.unitPreferences.pressureUnit, () => {
  displayedPressure.value = unitConversion.fromMPa(store.simulationInput.pressure, store.unitPreferences.pressureUnit)
})

// Initialize on mount
onMounted(() => {
  displayedTemperature.value = unitConversion.fromKelvin(store.simulationInput.temperature, store.unitPreferences.temperatureUnit)
  displayedPressure.value = unitConversion.fromMPa(store.simulationInput.pressure, store.unitPreferences.pressureUnit)
})
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



</style>