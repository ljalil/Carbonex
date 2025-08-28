<template>


    <el-form label-position="left" label-width="90px">
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
      <el-form-item label="Concentration">
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
    </el-form>

</template>

<script setup lang="ts">
import { store, type TemperatureUnit, type PressureUnit, type ConcentrationUnit } from "../store";
import { ElForm, ElFormItem, ElSelect, ElOption } from "element-plus";

const emit = defineEmits([
  'temperature-unit-changed',
  'pressure-unit-changed',
  'concentration-unit-changed'
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

const concentrationUnits: { label: string; value: ConcentrationUnit }[] = [
  { label: 'mol/kg', value: 'mol/kg' },
  { label: 'mol/L', value: 'mol/L' },
  { label: 'ppm', value: 'ppm' }
];

function updateTemperatureUnit() {
  emit('temperature-unit-changed');
}

function updatePressureUnit() {
  emit('pressure-unit-changed');
}

function updateConcentrationUnit() {
  emit('concentration-unit-changed');
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
