<template>
  <el-card class="sidebar-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span v-html="title"></span>
      </div>
    </template>

    <div class="simulation-properties-card">
      <el-text v-if="displayValue" type="primary" tag="b" size="large" class="single-value">{{ formattedValue }} {{ unit }}</el-text>
      <el-text v-else size="large" class="single-value no-data">N/A</el-text>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface SingleValueCardProps {
  title: string
  value: number | null | undefined
  unit?: string
  decimals?: number
}

const props = withDefaults(defineProps<SingleValueCardProps>(), {
  unit: '',
  decimals: 4
})

const displayValue = computed(() => props.value != null && props.value !== 0)
const formattedValue = computed(() => 
  props.value != null ? props.value.toFixed(props.decimals) : 'N/A'
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

.simulation-properties-card p {
  margin: 0;
}

.el-card__body {
  padding-top: 0px;
}

.single-value {
  display: flex;
  justify-content: center;
}

.no-data {
  color: #999;
}
</style>
