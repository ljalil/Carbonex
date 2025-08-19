<template>
  <el-card class="sidebar-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Simulation model</span>
      </div>
    </template>

    <el-form label-position="left" label-width="90px">
      <el-form-item label="Model">
        <el-select
          size="small"
          v-model="store.simulationInput.model"
          placeholder="Select model"

        >
          <el-option
            v-for="option in modelOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          ></el-option>
        </el-select>
      </el-form-item>
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
  name: "ModelSelection",
  components: {
    ElCard,
    ElForm,
    ElFormItem,
    ElSelect,
    ElOption,
  },
  setup() {
    const modelOptions = [
      { label: 'Carbonex', value: 'carbonex' },
      { label: 'PHREEQC (phreeqc.dat)', value: 'phreeqc_phreeqc' },
      { label: 'PHREEQC (pitzer.dat)', value: 'phreeqc_pitzer' },
      { label: 'Duan and Sun (2006)', value: 'duan_sun_2006' }
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

.el-select-dropdown__item {
  font-family: 'Roboto' !important;
}
</style>
