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

<script lang="ts">
import { defineComponent } from 'vue';
import HeatMap from '../HeatMap.vue';
import type { HeatmapData } from '../HeatMap.vue';
import { store } from '../../store';

export default defineComponent({
  name: 'VariablePTTab',
  components: {
    HeatMap,
  },
  setup() {
    // simulationOutput.heatmapData is of type HeatmapData
    return {
      store,
    };
  }
});
</script>

<style scoped>
.tab-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
