<template>
  <div class="sidebar-content">
    <ModelSelection />
    <!-- <UnitsSettings 
    @temperature-unit-changed="updateTemperatureUnit"
    @pressure-unit-changed="updatePressureUnit"
    /> -->
    <OperationalSettings />
  <WaterChemistry />
  <FormationMineralogy />
  <!-- <StreamImpurities /> -->
  </div>
</template>

<script setup lang="ts">
import ModelSelection from './ModelSelection.vue'
import UnitsSettings from './UnitsSettings.vue'
import WaterChemistry from './WaterChemistry.vue'
import FormationMineralogy from './FormationMineralogy.vue'
import OperationalSettings from './OperationalSettings.vue'
import StreamImpurities from './StreamImpurities.vue'

// Handle unit change events
const updateTemperatureUnit = () => {
  console.log('Temperature unit updated')
}

const updatePressureUnit = () => {
  console.log('Pressure unit updated')
}
</script>

<style scoped>
.sidebar-content {
  display: flex;
  flex-direction: column;

}
</style>
