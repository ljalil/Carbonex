<template>
  <el-card class="sidebar-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>AI Insights</span>
      </div>
    </template>

    <div class="ai-insights-content">
      <el-text v-if="hasInsights" size="default" class="insight-text">
        {{ store.simulationOutput.aiInsights }}
      </el-text>
      <el-text v-else size="default" class="insight-text no-insights">
        No AI insights available. Run a simulation to generate intelligent analysis of your results.
      </el-text>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { store } from '../store'

const hasInsights = computed(() => 
  store.simulationOutput.aiInsights && 
  store.simulationOutput.aiInsights.trim().length > 0
)
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

.ai-insights-content {
  padding: 8px 0;
}

.insight-text {
  line-height: 1.6;
  color: #606266;
  display: block;
  text-align: left;
}

.no-insights {
  color: #909399;
  font-style: italic;
}

.el-card__body {
  padding-top: 0px;
}
</style>