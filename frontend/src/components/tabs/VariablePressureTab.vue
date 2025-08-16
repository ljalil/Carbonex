<template>
  <div class="tab-content">
    <Plot 
      :data="store.simulationOutput.plotDataPressure"
      x-axis-label="Pressure (MPa)"
      y-axis-label="Dissolved CO2 (mol/kg)"
      :tooltip-labels="['Pressure (MPa)', 'Dissolved CO2 (mol/kg)']"
    />
  </div>
</template>

<script>
import Plot from '../Plot.vue';
import { store } from '../../store';

export default {
  name: 'VariablePressureTab',
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
