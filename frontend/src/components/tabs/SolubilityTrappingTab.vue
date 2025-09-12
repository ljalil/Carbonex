<template>
  <div class="tab-content">
    <el-row :gutter="20" style="height: 100%">
      <el-col :span="14" class="plots-column">
        <!-- Solution properties card -->
        

        <!-- Solubility plot -->
        <div class="plot-wrapper">
          <Plot
            :data="simulationOutput.solubilityTrapping.plotDataPressure"
            :emphasis="[store.simulationInput.pressure, store.simulationOutput.solubilityTrapping.total_dissolved_co2]"
            x-axis-label="Pressure (MPa)"
            y-axis-label="Dissolved CO2 (mol/kg)"
            :tooltip-labels="['Pressure', 'Dissolved CO2']"
          />
        </div>

        <div class="plot-wrapper">
          <Plot 
            :data="store.simulationOutput.solubilityTrapping.plotDataTemperature"
            :emphasis="[store.simulationInput.temperature, store.simulationOutput.solubilityTrapping.total_dissolved_co2]"
            x-axis-label="Temperature (K)"
            y-axis-label="Dissolved CO2 (mol/kg)"
            :tooltip-labels="['Temperature (K)', 'Dissolved CO2 (mol/kg)']"
          />
        </div>
      </el-col>

      <el-col :span="10">
        <!-- Activities plot -->
         <SingleValueCard 
           title="Dissolved CO<sub>2</sub>"
           :value="store.simulationOutput.solubilityTrapping.total_dissolved_co2"
           unit="mol/kg"
         />
         <SolutionProperties />
         <el-card  shadow="never">
              <template #header>
      <div class="card-header">
        <span>Activity coefficients</span>
      </div>
    </template>
        <div class="activity-chart-container">
          <BarPlot
            :data="activityData"
            x-axis-label="Species"
            y-axis-label="Activity coefficient"
          />
        </div>
</el-card>

        <!-- Molar volumes table -->
        <!-- <el-table
          :data="simulationOutput.speciesData"
          border
          stripe
          style="width: 100%; margin-top: 16px;"
        >
          <el-table-column
            prop="species"
            label="Species"
            width="80"
          >
            <template #default="scope">
              <span v-html="formatIonName(scope.row.species)"></span>
            </template>
          </el-table-column>

          <el-table-column
            prop="molar_volume"
            label="Molar volume"
            align="center"
          />
        </el-table> -->

      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Plot from '../Plot.vue';
import BarPlot from '../BarPlot.vue';
import SolutionProperties from '../SolutionProperties.vue';
import SingleValueCard from '../SingleValueCard.vue'
import { store } from '../../store';

const simulationOutput = computed(() => store.simulationOutput);

const ionNameMapping: Record<string, string> = {
  'Na+': 'Na<sup>+</sup>',
  'K+': 'K<sup>+</sup>',
  'Cl-': 'Cl<sup>-</sup>',
  'Mg+2': 'Mg<sup>+2</sup>',
  'Ca+2': 'Ca<sup>+2</sup>',
  'SO4-2': 'SO<sub>4</sub><sup>-2</sup>',
  'HCO3-': 'HCO<sub>3</sub><sup>-</sup>',
  'CO3-2': 'CO<sub>3</sub><sup>-2</sup>'
};
const formatIonName = (ion: string) => ionNameMapping[ion] || ion;

const activityData = computed(() =>
  (simulationOutput.value.solubilityTrapping.speciesData || []).map((item: any) => ({
    label: item.species,
    value: item.activity
  }))
);
</script>

<style scoped>
.tab-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.plots-column {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.plot-wrapper {
  flex: 1;
  min-height: 0;
  margin-bottom: 16px;
  width: 100%;
  overflow: hidden;
}

.plot-wrapper:last-child {
  margin-bottom: 0;
}
</style>
