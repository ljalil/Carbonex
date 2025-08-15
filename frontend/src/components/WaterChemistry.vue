<template>
  <el-card class="concentration-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Aqueous species</span>
      </div>
    </template>

    <el-form label-position="left">
      <el-form-item label="Preset">
        <el-select
          size="small"
          v-model="store.simulationInput.preset"
          placeholder="Select option"
          @change="updateWaterPreset"
        >
          <el-option
            v-for="option in presetOptions"
            :key="option"
            :label="option"
            :value="option"
          ></el-option>
        </el-select>
      </el-form-item>

      <el-form-item v-for="ion in ions" :key="ion">
        <span v-html="formatIonName(ion)" class="ion-label"></span>
        <el-input-number
          v-model="store.simulationInput.concentrations[ion]"
          size="small"
          :min="0"
          :precision="4"
          :step="0.1"
          @change="calculateChargeBalance"
        />
        <span class="unit-label">mol/kg</span>
      </el-form-item>
    </el-form>
    <el-alert 
      v-if="!isChargeBalanced" 
      :title="`Charge imbalanced: ${chargeSum.toFixed(4)}m`" 
      center 
      show-icon 
      type="error" 
      :closable="false" 
    />
    <el-alert 
      v-else 
      :title="`Charge balanced: ${chargeSum.toFixed(4)}m`" 
      center 
      show-icon 
      type="success" 
      :closable="false" 
    />
  </el-card>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import { store } from "../store";
import {
  ElCard,
  ElForm,
  ElFormItem,
  ElSelect,
  ElOption,
  ElInputNumber,
  ElAlert,
} from "element-plus";

export default defineComponent({
  name: "WaterChemistry",
  components: {
    ElCard,
    ElForm,
    ElFormItem,
    ElSelect,
    ElOption,
    ElInputNumber,
    ElAlert,
  },
  setup() {
    // Define a type for ion names to match the keys in concentrations
    type IonName = "Na+" | "K+" | "Cl-" | "Mg+2" | "Ca+2" | "SO4-2" | "HCO3-" | "CO3-2";
    
    const ions: IonName[] = [
      "Na+",
      "K+",
      "Cl-",
      "Mg+2",
      "Ca+2",
      "SO4-2",
    ];

    const ionCharges: Record<IonName, number> = {
      "Na+": 1,
      "K+": 1,
      "Cl-": -1,
      "Mg+2": 2,
      "Ca+2": 2,
      "SO4-2": -2,
      "HCO3-": -1,
      "CO3-2": -2,
    };

    const presetOptions = ['Seawater'];

    const isChargeBalanced = ref(true);
    const chargeSum = ref(0);

    const calculateChargeBalance = () => {
      let totalCharge = 0;
      for (const ion of ions) {
        totalCharge += store.simulationInput.concentrations[ion] * ionCharges[ion];
      }
      chargeSum.value = totalCharge;
      // You might want to define a tolerance for what you consider "balanced"
      isChargeBalanced.value = Math.abs(totalCharge) < 0.0001;
    };
    
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
    
    // Water preset handling
    const updateWaterPreset = (preset: string) => {
      console.log("Updating water preset to:", preset);
      
      if (preset === "Seawater") {
        // Update concentrations with seawater values
        store.simulationInput.concentrations["Cl-"] = 0.546;
        store.simulationInput.concentrations["Na+"] = 0.469;
        store.simulationInput.concentrations["Mg+2"] = 0.0528;
        store.simulationInput.concentrations["SO4-2"] = 0.0282;
        store.simulationInput.concentrations["Ca+2"] = 0.0103;
        store.simulationInput.concentrations["K+"] = 0.0102;
      }
      calculateChargeBalance();
    };

    return {
      store,
      ions,
      presetOptions,
      formatIonName,
      calculateChargeBalance,
      isChargeBalanced,
      chargeSum,
      updateWaterPreset,
    };
  },
});
</script>

<style scoped>
.concentration-card {
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

.ion-label {
  display: inline-block;
  width: 65px;
  margin-right: 5px;
  text-align: left;
}
</style>