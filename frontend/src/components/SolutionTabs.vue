<template>
  <el-tabs type="border-card">
    <el-tab-pane label="Solution">
      <table style="width: 100%">
        <tr style="height:10px">
          <td style="width:50%"><span class="property-text">Density</span></td>
          <td style="width:15%"><span class="property-value">{{ simulationOutput.density.toFixed(4) }}</span></td>
          <td style="width:25%"><span class="property-unit">g/cm</span></td>
        </tr>
        
        <tr>
          <td><span class="property-text">Ionic strength</span></td>
          <td><span class="property-value">{{ simulationOutput.ionic_strength.toFixed(4) }}</span></td>
          <td><span class="property-unit">mol/kgw</span></td>
        </tr>

        <tr>
          <td><span class="property-text">pH</span></td>
          <td><span class="property-value">{{ simulationOutput.pH.toFixed(4) }}</span></td>
          <td><span class="property-unit"></span></td>
        </tr>

        <!-- <tr>
          <td><span class="property-text">Activity of water</span></td>
          <td><span class="property-value">{{ simulationOutput.activity_of_water }}</span></td>
          <td><span class="property-unit"></span></td>
        </tr> -->

        <tr>
          <td><span class="property-text">Osmotic coefficient</span></td>
          <td><span class="property-value">{{ simulationOutput.osmotic_coefficient.toFixed(4) }}</span></td>
          <td><span class="property-unit"></span></td>
        </tr>
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

<script lang="ts">
import { defineComponent, computed } from "vue";
import { store } from "../store";
import { 
  ElTabs, 
  ElTabPane, 
  ElAlert, 
  ElTable, 
  ElTableColumn 
} from "element-plus";
import BarPlot from "./BarPlot.vue";

export default defineComponent({
  name: "SolutionTabs",
  components: {
    ElTabs,
    ElTabPane,
    ElAlert,
    ElTable,
    ElTableColumn,
    BarPlot,
  },
  setup() {
    const simulationOutput = computed(() => store.simulationOutput);
    
    // Direct mapping of ion names to their HTML representation
    const ionNameMapping: Record<string, string> = {
      "Na+": "Na<sup>+</sup>",
      "K+": "K<sup>+</sup>",
      "Cl-": "Cl<sup>-</sup>",
      "Mg+2": "Mg<sup>+2</sup>",
      "Ca+2": "Ca<sup>+2</sup>",
      "SO4-2": "SO<sub>4</sub><sup>-2</sup>",
      "HCO3-": "HCO<sub>3</sub><sup>-</sup>",
      "CO3-2": "CO<sub>3</sub><sup>-2</sup>"
    };
    
    // Simple function to look up the formatted ion name
    const formatIonName = (ion: string) => {
      return ionNameMapping[ion] || ion; // Return mapped value or original if not found
    };

    // Compute data for activity bar plot
    const activityData = computed(() => {
      return (simulationOutput.value.speciesData || []).map((item: any) => ({
        label: item.species,
        value: item.activity,
      }));
    });

    return {
      simulationOutput,
      formatIonName,
      activityData,
    };
  },
});
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
