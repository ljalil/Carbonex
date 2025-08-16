<template>
  <div class="tab-content">
    <Plot 
      :data="store.simulationOutput.plotDataTemperature"
      x-axis-label="Temperature (K)"
      y-axis-label="Dissolved CO2 (mol/kg)"
      :tooltip-labels="['Temperature (K)', 'Dissolved CO2 (mol/kg)']"
    />
  </div>
</template>

<script>
import Plot from '../Plot.vue';
import { store } from '../../store';

export default {
  name: 'VariableTemperatureTab',
  components: { 
    Plot 
  },
  data() {
    return {
      store
    };
  }
}
</script>

<style scoped>
.tab-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
