<template>
  <div class="action-bar">
    <el-button type="primary" @click="handleRunSimulationClicked">
      <!-- <el-icon :size="20" :color="white"><CaretRight /></el-icon> -->Run
    </el-button>
  
    <el-button type="default"><CaretRight /> Export CSV</el-button>
    <el-button type="default"><CaretRight /> Export Figures</el-button>
    <el-button type="default" @click="dialogVisible = true"><CaretRight /> Units</el-button>

    <el-dialog
    v-model="dialogVisible"
    title="Units settings"
    width="500"
    :before-close="handleClose"
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


const handleClose = (done: () => void) => {
  ElMessageBox.confirm('Are you sure to close this dialog?')
    .then(() => {
      done()
    })
    .catch(() => {
      // catch error
    })
}

  export default {
    name: "ActionBar",
    data() {
      return {
        dialogVisible: false
      };
    },
    methods: {
      handleRunSimulationClicked() {
        runStaticSimulation(); // Call the new function to get dissolved CO2
        runSimulation(); // Call the function to get all other properties
        runSimulationWithVaryingPressure(); // Call this to update the pressure vs. CO2 plot
        runSimulationWithVaryingTemperature(); // Call this to update the temperature vs. CO2 plot
        runSimulationWithVaryingPressureTemperature(); // Call this to update the heatmap
        this.$emit("run-simulation-clicked"); // Emit a custom event if needed
      },
      handleClose() {
      this.dialogVisible = false;
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
