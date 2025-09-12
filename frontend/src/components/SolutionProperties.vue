<template>
  <el-card class="solution-properties-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Solution properties</span>
      </div>
    </template>
    <table style="width: 100%">
      <tbody>
        <tr style="height:10px">
          <td style="width:50%"><el-text>Density</el-text></td>
          <td style="width:15%"><el-text type="primary" tag="b">{{ simulationOutput.solubilityTrapping.density?.toFixed(4) || 'N/A' }}</el-text></td>
          <td style="width:25%"><el-text>g/cm</el-text></td>
        </tr>
        <tr>
          <td><el-text>Ionic strength</el-text></td>
          <td><el-text type="primary" tag="b">{{ simulationOutput.solubilityTrapping.ionic_strength?.toFixed(4) || 'N/A' }}</el-text></td>
          <td><el-text>mol/kgw</el-text></td>
        </tr>
        <tr>
          <td><el-text>pH</el-text></td>
          <td><el-text type="primary" tag="b">{{ simulationOutput.solubilityTrapping.pH?.toFixed(4) || 'N/A' }}</el-text></td>
          <td></td>
        </tr>
        <tr>
          <td><el-text>Osmotic coefficient</el-text></td>
          <td><el-text type="primary" tag="b">{{ simulationOutput.solubilityTrapping.osmotic_coefficient?.toFixed(4) || 'N/A' }}</el-text></td>
          <td></td>
        </tr>
        <!-- <tr>
          <td><el-text>CO<sub>2</sub> fugacity coeff. (&phi;)</el-text></td>
          <td><el-text type="primary" tag="b">{{ simulationOutput.solubilityTrapping.fugacity_co2?.toFixed(4) || 'N/A' }}</el-text></td>
          <td></td>
        </tr>
        <tr>
          <td><el-text>CO<sub>2</sub> partial pressure</el-text></td>
          <td><el-text type="primary" tag="b">{{ simulationOutput.solubilityTrapping.partial_pressure_co2?.toFixed(4) || 'N/A' }}</el-text></td>
          <td></td>
        </tr> -->
      </tbody>
    </table>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { store } from '../store';

const simulationOutput = computed(() => store.simulationOutput);
</script>

<style scoped>

</style>
