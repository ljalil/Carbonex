<template>


    <el-form label-position="left" label-width="150px">
      <el-form-item label="Temperature">
        <el-select
          size="small"
          v-model="store.unitPreferences.temperatureUnit"
          placeholder="Select option"
          @change="updateTemperatureUnit"
        >
          <el-option
            v-for="option in temperatureUnits"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Pressure">
        <el-select
          size="small"
          v-model="store.unitPreferences.pressureUnit"
          placeholder="Select option"
          @change="updatePressureUnit"
        >
          <el-option
            v-for="option in pressureUnits"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Water chemistry">
        <el-select
          size="small"
          v-model="store.unitPreferences.concentrationUnit"
          placeholder="Select option"
          @change="updateConcentrationUnit"
        >
          <el-option
            v-for="option in concentrationUnits"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Formation mineralogy">
        <el-select
          size="small"
          v-model="store.unitPreferences.mineralogyUnit"
          placeholder="Select option"
          @change="updateMineralogyUnit"
        >
          <el-option
            v-for="option in mineralogyUnits"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          ></el-option>
        </el-select>
      </el-form-item>
    </el-form>

</template>

<script setup lang="ts">
import { store } from "../store";
import { 
  type TemperatureUnit, 
  type PressureUnit, 
  type WaterChemistryUnit, 
  type FormationMineralogyUnit 
} from "../units";
import { ElForm, ElFormItem, ElSelect, ElOption } from "element-plus";

const emit = defineEmits([
  'temperature-unit-changed',
  'pressure-unit-changed',
  'water-chemistry-unit-changed',
  'formation-mineralogy-unit-changed'
] as const);

const temperatureUnits = [
  { label: 'Kelvin (K)', value: 'kelvin' as TemperatureUnit },
  { label: 'Celsius (°C)', value: 'celsius' as TemperatureUnit },
  { label: 'Fahrenheit (°F)', value: 'fahrenheit' as TemperatureUnit }
];

const pressureUnits = [
  { label: 'Megapascal (MPa)', value: 'mpa' as PressureUnit },
  { label: 'Bar', value: 'bar' as PressureUnit },
  { label: 'Atmosphere (atm)', value: 'atm' as PressureUnit },
  { label: 'PSI', value: 'psi' as PressureUnit }
];

const concentrationUnits: { label: string; value: WaterChemistryUnit }[] = [
  { label: 'mol/kg', value: 'mol/kg' },
  { label: 'mol/L', value: 'mol/L' },
  { label: 'mg/L', value: 'mg/L' }
];

const mineralogyUnits: { label: string; value: FormationMineralogyUnit }[] = [
  { label: 'moles', value: 'moles' },
  { label: 'w/w', value: 'w/w' }
];

function updateTemperatureUnit() {
  emit('temperature-unit-changed');
}

function updatePressureUnit() {
  emit('pressure-unit-changed');
}

function updateConcentrationUnit() {
  emit('water-chemistry-unit-changed');
}

function updateMineralogyUnit() {
  emit('formation-mineralogy-unit-changed');
}
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

.el-select-dropdown__item {
  font-family: 'Roboto' !important;
}
</style>
