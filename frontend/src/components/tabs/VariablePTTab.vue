<template>
  <div class="tab-content">
    <HeatMap 
      :data="store.simulationOutput.heatmapData"
      x-axis-label="Temperature (K)"
      y-axis-label="Pressure (MPa)"
      title="CO₂ Solubility vs Pressure and Temperature"
    />
  </div>
</template>

<script>
import HeatMap from '../HeatMap.vue';
import { store } from '../../store';

export default {
  name: 'VariablePTTab',
  components: { 
    HeatMap 
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
