<template>
  
  <TotalDissolvedCO2Card />
  <SolutionTabs />
  <OperationalRisk />
</template>
  
<script lang="ts">
import { defineComponent } from "vue";
import TotalDissolvedCO2Card from "./TotalDissolvedCO2Card.vue";
import SolutionTabs from "./SolutionTabs.vue";
import OperationalRisk from "./OperationalRisk.vue"

export default defineComponent({
  name: "SimulationInfo",
  components: {
    TotalDissolvedCO2Card,
    SolutionTabs,
    OperationalRisk
  },
});
</script>
  
<style scoped>
/* SimulationInfo specific styles can be added here if needed */
</style>
