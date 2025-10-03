<template>
  <div class="tab-content">
    <el-row :gutter="20" style="height: 100%">
      <el-col :span="12" class="plots-column">
        <!-- Variable pressure plot -->
        <div class="plot-wrapper">
          <Plot
            :data="plotDataPressure"
            :emphasis="[store.simulationInput.pressure, store.simulationOutput.mineralTrapping.dissolved_co2]"
            x-axis-label="Pressure (MPa)"
            y-axis-label="Dissolved CO2 (mol/kg)"
            :tooltip-labels="['Pressure', 'Dissolved CO2']"
          />
        </div>

        <!-- Variable temperature plot -->
        <div class="plot-wrapper">
          <Plot 
            :data="plotDataTemperature"
            :emphasis="[store.simulationInput.temperature, store.simulationOutput.mineralTrapping.dissolved_co2]"
            x-axis-label="Temperature (K)"
            y-axis-label="Dissolved CO2 (mol/kg)"
            :tooltip-labels="['Temperature (K)', 'Dissolved CO2 (mol/kg)']"
          />
        </div>
      </el-col>

      <el-col :span="12" class="scrollable-column">
        <el-scrollbar height="100%">
          <div class="scrollable-content">
            <!-- Dissolved CO2 card -->
             <SingleValueCard 
               title="Dissolved and mineralized CO<sub>2</sub>"
               :value="store.simulationOutput.mineralTrapping.dissolved_co2"
               unit="mol/kg"
             />
             
             <!-- Solution properties -->
             <SolutionProperties :data="simulationOutput.mineralTrapping" />
             
             <!-- Activity coefficients chart -->
             <el-card shadow="never">
                  <template #header>
          <div class="card-header">
            <span>Activity coefficients</span>
          </div>
        </template>
            <div class="activity-chart-container">
              <BarPlot
                :data="activityCoefficientsData"
                x-axis-label="Species"
                y-axis-label="Activity coefficient"
              />
            </div>
    </el-card>

             <!-- Mineral equilibrium chart -->
             <el-card shadow="never">
                  <template #header>
          <div class="card-header">
            <span>Minerals equilibrium</span>
          </div>
        </template>
            <div class="activity-chart-container">
              <BarPlot
                :data="mineralsEquiData"
                x-axis-label="Minerals"
                y-axis-label="Amount (moles)"
              />
            </div>
    </el-card>
          </div>
        </el-scrollbar>
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

// Use actual plot data from store instead of placeholders
const plotDataPressure = computed(() => store.simulationOutput.mineralTrapping.plotDataPressure || []);
const plotDataTemperature = computed(() => store.simulationOutput.mineralTrapping.plotDataTemperature || []);

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

const activityCoefficientsData = computed(() =>
  (simulationOutput.value.mineralTrapping.speciesData || []).map((item: any) => ({
    label: item.species,
    value: item.activity
  }))
);

const mineralsEquiData = computed(() => {
  const mineralEqui = simulationOutput.value.mineralTrapping.mineral_equi || {};
  const initialMinerals = simulationOutput.value.mineralTrapping.initial_minerals || {}; // Use stored snapshot instead of current user input
  
  // Get all unique mineral names from both initial input and final amounts from backend
  const allMinerals = new Set([
    ...Object.keys(initialMinerals),
    ...Object.keys(mineralEqui)
  ]);
  
  // Filter out minerals that have zero values in both initial and final
  const relevantMinerals = Array.from(allMinerals).filter(mineral => {
    const initialAmount = initialMinerals[mineral] || 0;
    const finalAmount = mineralEqui[mineral] || 0; // Backend returns final amounts, not deltas
    return initialAmount > 0 || finalAmount > 0;
  });
  
  // Prepare categories and series data
  const categories = relevantMinerals.map(mineral => 
    mineral.charAt(0).toUpperCase() + mineral.slice(1)
  );
  
  const initialAmounts = relevantMinerals.map(mineral => 
    initialMinerals[mineral] || 0 // Use stored initial minerals snapshot
  );
  
  const finalAmounts = relevantMinerals.map(mineral => 
    mineralEqui[mineral] || 0 // Use backend values directly as final amounts
  );
  
  return {
    categories,
    series: [
      {
        name: 'Initial',
        data: initialAmounts
      },
      {
        name: 'Final',
        data: finalAmounts
      }
    ]
  };
});
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

.scrollable-column {
  height: 100%;
}

.scrollable-column .el-scrollbar {
  height: 100%;
}

.scrollable-content {
  padding-right: 15px;
}
</style>
