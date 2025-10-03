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
    <UnitsSettings
      @water-chemistry-unit-changed="handleWaterChemistryUnitChanged"
    ></UnitsSettings>
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
  import { runSimulationCO2BrineSolutionProperties, runSimulationCO2BrineVarP, runSimulationCO2BrineVarT, runSimulationCO2BrineFixed, runSimulationCO2BrineRockFixed, runSimulationCO2BrineRockVarP, runSimulationCO2BrineRockVarT, runSimulationCO2BrineRockSolutionProperties} from "../actions";
  import { ref, defineEmits } from 'vue'
import { ElMessageBox } from 'element-plus'
import UnitsSettings from "./UnitsSettings.vue";
import { store } from '../store'

  const emit = defineEmits<{
    (e: 'run-simulation-clicked'): void
  }>()
  
  const dialogVisible = ref(false)
  
    const handleRunSimulationClicked = () => {
    // Reset AI insights when starting new simulation
    store.simulationOutput.aiInsights = ''
    
    runSimulationCO2BrineFixed()
    runSimulationCO2BrineSolutionProperties()
    runSimulationCO2BrineVarP()
    runSimulationCO2BrineVarT()
    runSimulationCO2BrineRockFixed()
    runSimulationCO2BrineRockSolutionProperties()
    runSimulationCO2BrineRockVarP()
    runSimulationCO2BrineRockVarT()
    emit('run-simulation-clicked')
  }

  const handleWaterChemistryUnitChanged = () => {
    // The conversion is handled automatically by the watcher in WaterChemistry.vue
    // This handler can be used for additional actions if needed
    console.log('Water chemistry unit changed')
  }
  </script>
  
  <style scoped>
  .action-bar {
    display: flex;
    align-items: center;
    gap: 5px;
    flex-shrink: 0; /* Prevent the action bar from shrinking */
    height: auto; /* Let it size naturally but don't grow */
  }

 .el-button, .el-button--primary {
  font-family: 'Roboto' !important;
  margin-left: 0px;
}
  </style>
