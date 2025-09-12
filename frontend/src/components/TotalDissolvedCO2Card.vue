<template>
  <el-card class="sidebar-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Dissolved CO<sub>2</sub></span>
      </div>
    </template>

    <div class="simulation-properties-card">
      <el-text v-if="displayCO2Value" type="primary" tag="b" size="large" class="total-dissolved-co2">{{ formatCO2Value }} mol/kg</el-text>
      <el-text v-else size="large" class="total-dissolved-co2 no-data">N/A</el-text>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { store } from '../store'

const simulationOutput = computed(() => store.simulationOutput)
const displayCO2Value = computed(() => simulationOutput.value.total_dissolved_co2 != 0)
const formatCO2Value = computed(() => simulationOutput.value.total_dissolved_co2?.toFixed(4) || 'N/A')
</script>

<style scoped>
.sidebar-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
}

.simulation-properties-card p {
  margin: 0;
}

.el-card__body {
  padding-top: 0px;
}

.total-dissolved-co2 {
  display: flex;
  justify-content: center;

}

.no-data {
  color: #999;
}
</style>
