<template>
    <el-button type="primary" @click="handleRunSimulationClicked">
      <!-- <el-icon :size="20" :color="white"><CaretRight /></el-icon> -->Run
    </el-button>
  
    <el-button type="default"><CaretRight /> Export CSV</el-button>
  </template>
  
  <script>
  import { CaretRight } from "@element-plus/icons-vue";
  import { runSimulation, runSimulationWithVaryingPressure, runStaticSimulation } from "../actions"; // Added import for runStaticSimulation
  
  export default {
    name: "ActionBar",
    methods: {
      handleRunSimulationClicked() {
        runStaticSimulation(); // Call the new function to get dissolved CO2
        runSimulation(); // Call the function to get all other properties
        runSimulationWithVaryingPressure(); // Call this to update the pressure vs. CO2 plot
        this.$emit("run-simulation-clicked"); // Emit a custom event if needed
      }
    }
  };
  </script>
  
  <style scoped>
  /* Add any styles here */
  </style>
