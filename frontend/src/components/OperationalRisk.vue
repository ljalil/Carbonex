<template>
    <el-card class="sidebar-card" shadow="never">
      <template #header>
        Corrosion Assessment
      </template>
  
      <el-form label-position="left" label-width="120px">
      <el-form-item label="Corrosion model">
        <el-select
          size="small"
          v-model="store.simulationInput.corrosionModel"
          placeholder="Select corrosion model"
        >
          <el-option
            v-for="option in modelOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          ></el-option>
        </el-select>
      </el-form-item>

      <el-text>Corrosion rate: </el-text>
      <el-text type="primary" tag="b">0.3 mm/year</el-text>

      
    </el-form>
    </el-card>

  

  </template>
  
  <script lang="ts">
  import { defineComponent } from "vue";
  import { store } from "../store";
  import {
    ElCard,
    ElForm,
    ElFormItem,
    ElSelect,
    ElOption,
  } from "element-plus";
  
  export default defineComponent({
    name: "OperationalRisk",
    components: {
      ElCard,
      ElForm,
      ElFormItem,
      ElSelect,
      ElOption,
    },
    setup() {
      const modelOptions = [
        { label: 'de Waard (1991)', value: 'deWaald1991' },
        { label: 'de Waard (1995)', value: 'deWaald1995' }
      ];

      return {
        store,
        modelOptions,
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
