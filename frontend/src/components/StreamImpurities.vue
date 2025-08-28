<template>
  <el-card class="stream-impurities-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Gas components</span>
        <el-switch
          v-model="store.simulationInput.considerImpurities"
          @change="handleConsiderImpuritiesChange"
          size="small"
        />
      </div>
    </template>

    <el-form label-position="left" label-width="auto">
      <el-form-item v-for="gas in gases" :key="gas" :label="gas">
        <div class="input-with-unit">
          <el-input-number
            v-model="store.simulationInput.streamImpurities[gas]"
            size="small"
            :min="0"
            :max="1"
            :precision="4"
            :step="0.1"
            :disabled="!store.simulationInput.considerImpurities"
            @change="calculateSum"
            style="flex: 1"
          />
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-alert
        :title="alertInfo.title"
        :type="alertInfo.type as 'error' | 'success' | 'warning' | 'info'"
        center
        show-icon
        :closable="false"
        class="sum-alert"
      />
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { store } from '../store'
// Gas mole fraction logic
const gases = ['CO2', 'O2', 'H2S', 'Hydrogen'] as const

const handleConsiderImpuritiesChange = () => { if (!store.simulationInput.considerImpurities) calculateSum() }
const sumFractions = computed(() => gases.reduce((sum, gas) => sum + store.simulationInput.streamImpurities[gas], 0))
const calculateSum = () => { void sumFractions.value }
onMounted(calculateSum)

const alertInfo = computed(() => {
  const sum = sumFractions.value
  const title = `Mole fractions sum: ${sum.toFixed(2)}`
  return Math.abs(sum - 1) < 1e-6
    ? { type: 'success', title }
    : { type: 'error', title: title + ' (should be 1)' }
})
</script>

<style scoped>
.stream-impurities-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
}

.unit-label {
  margin-left: 10px;
  white-space: nowrap;
}

.input-with-unit {
  display: flex;
  align-items: center;
  width: 100%;
}
.sum-alert {
  margin-top: 10px;
}
</style>
