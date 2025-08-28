<template>
  <el-tabs type="border-card">
    <el-tab-pane label="Solution">
      <table style="width: 100%">
        <tbody>
          <tr style="height:10px">
            <td style="width:50%"><el-text>Density</el-text></td>
            <td style="width:15%"><el-text type="primary" tag="b">{{ simulationOutput.density?.toFixed(4) || 'N/A' }}</el-text></td>
            <td style="width:25%"><el-text>g/cm</el-text></td>
          </tr>
          
          <tr>
            <td><el-text>Ionic strength</el-text></td>
            <td><el-text type="primary" tag="b">{{ simulationOutput.ionic_strength?.toFixed(4) || 'N/A' }}</el-text></td>
            <td><el-text>mol/kgw</el-text></td>
          </tr>

          <tr>
            <td><el-text>pH</el-text></td>
            <td><el-text type="primary" tag="b">{{ simulationOutput.pH?.toFixed(4) || 'N/A' }}</el-text></td>
            <td></td>
          </tr>

          <tr>
            <td><el-text>Osmotic coefficient</el-text></td>
            <td><el-text type="primary" tag="b">{{ simulationOutput.osmotic_coefficient?.toFixed(4) || 'N/A' }}</el-text></td>
            <td></td>
          </tr>
          <tr>
            <td><el-text>CO<sub>2</sub> fugacity coeff. (&phi;)</el-text></td>
            <td><el-text type="primary" tag="b">{{ simulationOutput.fugacity_co2?.toFixed(4) || 'N/A' }}</el-text></td>
            <td></td>
          </tr>
          <tr>
            <td><el-text>CO<sub>2</sub> partial pressure</el-text></td>
            <td><el-text type="primary" tag="b">{{ simulationOutput.partial_pressure_co2?.toFixed(4) || 'N/A' }}</el-text></td>
            <td></td>
          </tr>
        </tbody>
      </table>
      <el-alert title="Solution properties are determined using PHREEQC." type="info" :closable="false" show-icon/>
    </el-tab-pane>
    
    <el-tab-pane label="Activities">
      <div class="activity-chart-container">
        <BarPlot 
          :data="activityData" 
          xAxisLabel="Activity" 
        />
      </div>
      <el-alert title="Activities are determined using PHREEQC." type="info" :closable="false" show-icon/>
    </el-tab-pane>
    
    <el-tab-pane label="Molar volumes">
      <el-table
        :data="simulationOutput.speciesData"
        border
        stripe
        style="width: 100%;">
        <el-table-column
          prop="species"
          label="Species"
          width="80">
          <template #default="scope">
            <span v-html="formatIonName(scope.row.species)"></span>
          </template>
        </el-table-column>

        <el-table-column
          prop="molar_volume"
          label="Molar volume"
          align="center">
        </el-table-column>
      </el-table>
      <el-alert title="Molar volumes are determined using PHREEQC." type="info" :closable="false" show-icon/>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { store } from '../store'
import BarPlot from './BarPlot.vue'

const simulationOutput = computed(() => store.simulationOutput)

const ionNameMapping: Record<string, string> = {
  'Na+': 'Na<sup>+</sup>',
  'K+': 'K<sup>+</sup>',
  'Cl-': 'Cl<sup>-</sup>',
  'Mg+2': 'Mg<sup>+2</sup>',
  'Ca+2': 'Ca<sup>+2</sup>',
  'SO4-2': 'SO<sub>4</sub><sup>-2</sup>',
  'HCO3-': 'HCO<sub>3</sub><sup>-</sup>',
  'CO3-2': 'CO<sub>3</sub><sup>-2</sup>'
}
const formatIonName = (ion: string) => ionNameMapping[ion] || ion

const activityData = computed(() =>
  (simulationOutput.value.speciesData || []).map((item: any) => ({
    label: item.species,
    value: item.activity
  }))
)
</script>

<style scoped>
.property-text {
  font-size: .8em;
  width: 50%;
}

.property-unit {
  font-size: 0.8em;
  padding-left: 5px;
}

.property-value {
  font-size: 0.8em;
  color: #409EFF;
}
</style>
