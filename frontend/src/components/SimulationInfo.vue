<template>
  <SingleValueCard 
    title="Dissolved CO<sub>2</sub>"
    :value="store.simulationOutput.solubilityTrapping.total_dissolved_co2"
    unit="mol/kg"
  />

  <SingleValueCard 
    title="Dissolved and mineralized CO<sub>2</sub>"
    :value="store.simulationOutput.mineralTrapping.dissolved_co2"
    unit="mol/kg"
  />
  <!-- <OperationalRisk /> -->
  <ArtificialIntelligenceInsights />
</template>
  
<script lang="ts">
import { defineComponent } from "vue";
import SingleValueCard from "./SingleValueCard.vue";
import SolutionTabs from "./SolutionTabs.vue";
import OperationalRisk from "./OperationalRisk.vue";
import ArtificialIntelligenceInsights from "./ArtificialIntelligenceInsights.vue";
import { store } from '../store';

export default defineComponent({
  name: "SimulationInfo",
  components: {
    SingleValueCard,
    SolutionTabs,
    OperationalRisk,
    ArtificialIntelligenceInsights
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
