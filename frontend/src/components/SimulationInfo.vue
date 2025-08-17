<template>
    <el-card class="sidebar-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>Total dissolved CO<sub>2</sub></span>
        </div>
      </template>
  
      <div class="simulation-properties-card">
        <p v-if="displayCO2Value" class="total-dissolved-co2">{{ formatCO2Value }} mol/kg</p>
        <p v-else class="total-dissolved-co2 no-data">N/A</p>
      </div>
    </el-card>

    <el-tabs type="border-card">
    <el-tab-pane label="Solution">
      <table style="width: 100%">
          <tr style="height:10px">
            <td style="width:50%"><span class="property-text">Density</span></td>
            <td style="width:15%"><span class="property-value">{{ simulationOutput.density }}</span></td>
            <td style="width:25%"><span class="property-unit">g/cm</span></td>
          </tr>
          
          <tr>
            <td><span class="property-text">Ionic strength</span></td>
            <td><span class="property-value">{{ simulationOutput.ionic_strength }}</span></td>
            <td><span class="property-unit">mol/kgw</span></td>
          </tr>

          <tr>
            <td><span class="property-text">pH</span></td>
            <td><span class="property-value">{{ simulationOutput.pH }}</span></td>
            <td><span class="property-unit"></span></td>
          </tr>

          <tr>
            <td><span class="property-text">Activity of water</span></td>
            <td><span class="property-value">{{ simulationOutput.activity_of_water }}</span></td>
            <td><span class="property-unit"></span></td>
          </tr>

          <tr>
            <td><span class="property-text">Osmotic coefficient</span></td>
            <td><span class="property-value">{{ simulationOutput.osmotic_coefficient }}</span></td>
            <td><span class="property-unit"></span></td>
          </tr>

        </table>
    </el-tab-pane>
    <el-tab-pane label="Activities">
      <div class="activity-chart-container">
        <BarPlot 
          :data="activityData" 
          xAxisLabel="Activity" 
        />
      </div>
    </el-tab-pane>
    <el-tab-pane label="Molar">

          <el-table
    :data="simulationOutput.speciesData"
    border
    stripe
    style="width: 100%; ">
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
    </el-tab-pane>

  </el-tabs>

    
  


  

  </template>
  
  <script lang="ts">
  import { defineComponent, ref, reactive } from "vue";
  import { computed } from "vue";

  import { store } from "../store"; // Adjust the import path based on your project structure
  import {
    ElCard,
    ElForm,
    ElFormItem,
    ElSelect,
    ElOption,
    ElCol,
  } from "element-plus";
  import {
    CaretRight,
    Delete,
    Edit,
    Eleme,
    PartlyCloudy,
    Search,
    Share,
    Upload,
  } from "@element-plus/icons-vue";
  import BarPlot from "./BarPlot.vue";

  interface UnitOption {
    label: string;
    value: string;
  }
  
  export default defineComponent({
    name: "Sidebar",
    components: {
      ElCard,
      ElForm,
      ElFormItem,
      ElSelect,
      ElOption,
      ElCol,
      BarPlot,
    },

    setup() {
      const ions = [
        "Sodium",
        "Potassium",
        "Chloride",
        "Magnesium",
        "Calcium",
        "Sulfide",
        "Bicarbonate",
        "Carbonate",
      ];

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
      
      const concentrations = reactive<Record<string, number>>(
        Object.fromEntries(ions.map((ion) => [ion, 0]))
      );
  
      const updateConcentration = (ion: string) => {
        console.log(`${ion} concentration updated:`, concentrations[ion]);
        // You can add additional logic here, such as emitting an event to a parent component
      };
  
      const temperatureUnits: UnitOption[] = [
        { label: "Celsius", value: "celsius" },
        { label: "Fahrenheit", value: "fahrenheit" },
        { label: "Kelvin", value: "kelvin" },
      ];
  
      const waterPresets: UnitOption[] = [
        { label: "Seawater", value: "seawater" },
        { label: "Freshwater", value: "freshwater" },
        { label: "Brackish water", value: "brackish" },
      ];
  
      const pressureUnits: UnitOption[] = [
        { label: "Pascal", value: "pascal" },
        { label: "Bar", value: "bar" },
        { label: "PSI", value: "psi" },
      ];
  
      const concentrationUnits: UnitOption[] = [
        { label: "molality", value: "pascal" },
        { label: "Bar", value: "bar" },
        { label: "PSI", value: "psi" },
      ];
  
      const selectedTemperatureUnit = ref("");
      const selectedPressureUnit = ref("");
      const currentTemperatureUnit = ref("");
      const currentPressureUnit = ref("");
      const selectedWaterPreset = ref("");
      const simTemperature = ref(273);
      const simPressure = ref(4000);
  
      const updateTemperatureUnit = (value: string) => {
        currentTemperatureUnit.value = value;
        console.log("Temperature unit updated:", value);
      };
  
      const updatePressureUnit = (value: string) => {
        currentPressureUnit.value = value;
        console.log("Pressure unit updated:", value);
      };
  
      const updateWaterPreset = (value: string) => {
        selectedWaterPreset.value = value;
        console.log("Water preset updated:", value);
      };

      // Compute data for activity bar plot
      const activityData = computed(() => {
        return (simulationOutput.value.speciesData || []).map((item: any) => ({
          label: item.species,
          value: item.activity,
        }));
      });

      const displayCO2Value = computed(() => simulationOutput.value.total_dissolved_co2 != null);
      const formatCO2Value = computed(() => simulationOutput.value.total_dissolved_co2?.toFixed(4) || "N/A");
  
      return {
        temperatureUnits,
        pressureUnits,
        waterPresets,
        selectedTemperatureUnit,
        selectedWaterPreset,
        selectedPressureUnit,
        currentTemperatureUnit,
        currentPressureUnit,
        updateTemperatureUnit,
        updatePressureUnit,
        updateWaterPreset,
        ions,
        concentrations,
        updateConcentration,
        simTemperature,
        simPressure,


        simulationOutput,
        formatIonName,
        displayCO2Value,
        formatCO2Value,
        activityData,
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
  
  .unit-label {
    margin-left: 10px;
  }
  
  .el-select,
  .el-select-dropdown__item {
    font-family: "Roboto", sans-serif;
  }
  
  h1 {
    font-weight: 100;
    margin: 10px 0px;
  }

  .simulation-properties-card p {
    margin: 0;
  }

  p {
    display:flex;
    justify-content: start;
  }

  .property-text{
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

.el-card__body {
    padding-top: 0px;
  }

  .total-dissolved-co2{
    display: flex;
    justify-content: center;
    font-size: 1.5em;
    color: #409EFF;
  }

  .no-data {
    color: #999;
  }
  </style>
