<template>
  <el-card class="sidebar-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Total dissolved CO<sub>2</sub></span>
      </div>
    </template>

    <div class="simulation-properties-card">
      <el-text v-if="displayCO2Value" type="primary" size="large" class="total-dissolved-co2">{{ formatCO2Value }} mol/kg</el-text>
      <el-text v-else size="large" class="total-dissolved-co2 no-data">N/A</el-text>
    </div>
  </el-card>
</template>

<script lang="ts">
import { defineComponent, computed } from "vue";
import { store } from "../store";
import { ElCard } from "element-plus";

export default defineComponent({
  name: "TotalDissolvedCO2Card",
  components: {
    ElCard,
  },
  setup() {
    const simulationOutput = computed(() => store.simulationOutput);
    
    const displayCO2Value = computed(() => simulationOutput.value.total_dissolved_co2 != 0);
    const formatCO2Value = computed(() => simulationOutput.value.total_dissolved_co2?.toFixed(4) || "N/A");

    return {
      displayCO2Value,
      formatCO2Value,
    };
  },
});
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
