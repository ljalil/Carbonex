<template>
  <div class="action-bar">
    <el-button type="primary" @click="handleRunSimulationClicked" :icon="CaretRight">Run</el-button>
  
    <el-button type="default">Export CSV</el-button>
    <el-button type="default">Export Figures</el-button>
    <el-button type="default" @click="dialogVisible = true">Units Settings</el-button>

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
  
  <script setup lang="ts" >
  import { CaretRight } from "@element-plus/icons-vue";
  import { runSimulation, runSimulationWithVaryingPressure, runSimulationWithVaryingTemperature, runSimulationWithVaryingPressureTemperature, runStaticSimulation } from "../actions"; // Added import for heatmap function
  import { ref, defineEmits } from 'vue'
import { ElMessageBox } from 'element-plus'
import UnitsSettings from "./UnitsSettings.vue";

  const emit = defineEmits<{
    (e: 'run-simulation-clicked'): void
  }>()
  
  const dialogVisible = ref(false)
  
  const handleRunSimulationClicked = () => {
    runStaticSimulation()
    runSimulation()
    runSimulationWithVaryingPressure()
    runSimulationWithVaryingTemperature()
    emit('run-simulation-clicked')
  }
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
