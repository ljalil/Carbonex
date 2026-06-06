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
import { store, CO2_CRITICAL_POINT } from '../store'
import { temperatureConversion, pressureConversion, combinedConversions } from '../units'
import CO2PhaseDiagram from './CO2PhaseDiagram.vue'

// Unit labels
const temperatureUnitLabel = computed(() => {
  return temperatureConversion.getUnitLabel(store.unitPreferences.temperatureUnit)
})
const temperatureMinValue = computed(() => {
  return temperatureConversion.getMinValue(store.unitPreferences.temperatureUnit)
})
const pressureUnitLabel = computed(() => {
  return pressureConversion.getUnitLabel(store.unitPreferences.pressureUnit)
})

// Check if CO2 is in supercritical conditions
const isSupercritical = computed(() => {
  return combinedConversions.isCO2Supercritical(store.simulationInput.temperature, store.simulationInput.pressure)
})

// Displayed values
const displayedTemperature = ref(temperatureConversion.fromKelvin(store.simulationInput.temperature, store.unitPreferences.temperatureUnit))
const displayedPressure = ref(pressureConversion.fromMPa(store.simulationInput.pressure, store.unitPreferences.pressureUnit))

// Update handlers
const handleTemperatureChange = (current: number | undefined) => {
  store.simulationInput.temperature = temperatureConversion.toKelvin(current ?? 0, store.unitPreferences.temperatureUnit)
}
const handlePressureChange = (current: number | undefined) => {
  store.simulationInput.pressure = pressureConversion.toMPa(current ?? 0, store.unitPreferences.pressureUnit)
}

// Watch for changes
watch(() => store.simulationInput.temperature, val => {
  displayedTemperature.value = temperatureConversion.fromKelvin(val, store.unitPreferences.temperatureUnit)
})
watch(() => store.simulationInput.pressure, val => {
  displayedPressure.value = pressureConversion.fromMPa(val, store.unitPreferences.pressureUnit)
})
watch(() => store.unitPreferences.temperatureUnit, () => {
  displayedTemperature.value = temperatureConversion.fromKelvin(store.simulationInput.temperature, store.unitPreferences.temperatureUnit)
})
watch(() => store.unitPreferences.pressureUnit, () => {
  displayedPressure.value = pressureConversion.fromMPa(store.simulationInput.pressure, store.unitPreferences.pressureUnit)
})

// Initialize on mount
onMounted(() => {
  displayedTemperature.value = temperatureConversion.fromKelvin(store.simulationInput.temperature, store.unitPreferences.temperatureUnit)
  displayedPressure.value = pressureConversion.fromMPa(store.simulationInput.pressure, store.unitPreferences.pressureUnit)
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