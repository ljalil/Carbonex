<template>
  <div class="action-bar">
    <el-button type="primary" @click="handleRunSimulationClicked" :icon="CaretRight">Run</el-button>
  
    <el-button type="default">Export CSV</el-button>
    <el-button type="default">Export Figures</el-button>
    <el-button type="default" @click="dialogVisible = true">Units</el-button>

    <el-dialog
    v-model="dialogVisible"
    title="Units settings"
    width="400"
  >
    <UnitsSettings></UnitsSettings>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogVisible = false">Confirm</el-button>
      </div>
    </template>
  </el-dialog>

  </div>
</template>
  
  <script lang="ts" >
  import { CaretRight } from "@element-plus/icons-vue";
  import { runSimulation, runSimulationWithVaryingPressure, runSimulationWithVaryingTemperature, runSimulationWithVaryingPressureTemperature, runStaticSimulation } from "../actions"; // Added import for heatmap function
  import { ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import UnitsSettings from "./UnitsSettings.vue";

  export default {
    name: "ActionBar",
    components: {
      UnitsSettings
    },
    setup(props, { emit }) {
      const dialogVisible = ref(false);



      const handleRunSimulationClicked = () => {
        runStaticSimulation(); // Call the new function to get dissolved CO2
        runSimulation(); // Call the function to get all other properties
        runSimulationWithVaryingPressure(); // Call this to update the pressure vs. CO2 plot
        runSimulationWithVaryingTemperature(); // Call this to update the temperature vs. CO2 plot
        runSimulationWithVaryingPressureTemperature(); // Call this to update the heatmap
        emit("run-simulation-clicked"); // Emit a custom event if needed
      };

      return {
        dialogVisible,
        handleRunSimulationClicked,
        CaretRight
      }
    }
  };
  </script>
  
  <style scoped>
  .action-bar {
    display: flex;
    align-items: center;
    gap: 5px;
  }

 .el-button, .el-button--primary {
  font-family: 'Roboto' !important;
  margin-left: 0px;
}
  </style>
