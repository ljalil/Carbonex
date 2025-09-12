<template>
  <SingleValueCard 
    title="Dissolved CO<sub>2</sub>"
    :value="store.simulationOutput.solubilityTrapping.total_dissolved_co2"
    unit="mol/kg"
  />

  <SingleValueCard 
    title="Total trapped CO<sub>2</sub>"
    :value="store.simulationOutput.solubilityTrapping.total_dissolved_co2"
    unit="mol/kg"
  />
  <!-- <OperationalRisk /> -->
</template>
  
<script lang="ts">
import { defineComponent } from "vue";
import SingleValueCard from "./SingleValueCard.vue";
import SolutionTabs from "./SolutionTabs.vue";
import OperationalRisk from "./OperationalRisk.vue";
import { store } from '../store';

export default defineComponent({
  name: "SimulationInfo",
  components: {
    SingleValueCard,
    SolutionTabs,
    OperationalRisk
  },
  setup() {
    return {
      store
    }
  }
});
</script>
  
<style scoped>
/* SimulationInfo specific styles can be added here if needed */
</style>
