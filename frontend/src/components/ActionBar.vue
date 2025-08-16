<template>
  <div class="action-bar">
    <el-button type="primary" @click="handleRunSimulationClicked">
      <!-- <el-icon :size="20" :color="white"><CaretRight /></el-icon> -->Run
    </el-button>
  
    <el-button type="default"><CaretRight /> Export CSV</el-button>
  </div>
</template>
  
  <script>
  import { CaretRight } from "@element-plus/icons-vue";
  import { runSimulation, runSimulationWithVaryingPressure, runSimulationWithVaryingTemperature, runSimulationWithVaryingPressureTemperature, runStaticSimulation } from "../actions"; // Added import for heatmap function
  
  export default {
    name: "ActionBar",
    methods: {
      handleRunSimulationClicked() {
        runStaticSimulation(); // Call the new function to get dissolved CO2
        runSimulation(); // Call the function to get all other properties
        runSimulationWithVaryingPressure(); // Call this to update the pressure vs. CO2 plot
        runSimulationWithVaryingTemperature(); // Call this to update the temperature vs. CO2 plot
        runSimulationWithVaryingPressureTemperature(); // Call this to update the heatmap
        this.$emit("run-simulation-clicked"); // Emit a custom event if needed
      }
    }
  };
  </script>
  
  <style scoped>
  .action-bar {
    display: flex;
    align-items: center;
  }
  </style>
