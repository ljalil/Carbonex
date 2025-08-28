<template>
  <el-card class="concentration-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Water chemistry</span>
        <el-button  size="small" :icon="Plus" circle />
      </div>
    </template>

    <el-form label-position="left" label-width="auto" >

      <el-form-item label="Preset">
        <el-select
          size="small"
          v-model="store.simulationInput.preset"
          placeholder="Select option"
          @change="updateWaterPreset"
          style="width: 100%"
        >
          <el-option
            v-for="option in presetOptions"
            :key="option"
            :label="option"
            :value="option"
          ></el-option>
        </el-select>
      </el-form-item>

      <el-form-item v-for="ion in ions" :key="ion" :label="ion">
        <!-- The v-html version can be used for better formatting -->
        <!-- <span v-html="formatIonName(ion)" class="ion-label"></span> -->

          <el-input-number
            v-model="store.simulationInput.concentrations[ion]"
            size="small"
            :min="0"
            :precision="4"
            :step="0.1"
            style="flex: 1"
            @change="calculateChargeBalance">
            <template #suffix>
        <span>{{ concentrationUnitLabel }}</span>
      </template>
          
          </el-input-number>

      </el-form-item>
    </el-form>


        <template #footer>
    <el-alert
      :title="alertInfo.title"
      :type="alertInfo.type"
      center
      show-icon
      :closable="false"
      class="cbe-alert"
    >
    </el-alert>
    </template>
  
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { store } from "../store";
import { Plus } from '@element-plus/icons-vue';

// Define a type for ion names to match the keys in concentrations
type IonName = "Na+" | "K+" | "Cl-" | "Mg+2" | "Ca+2" | "SO4-2" | "HCO3-" | "CO3-2";

const ions: IonName[] = ["Na+", "K+", "Cl-", "Mg+2", "Ca+2", "SO4-2"];

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

const concentrationUnitLabel = computed(() => {
  switch (store.unitPreferences.concentrationUnit) {
    case 'mol/kg': return 'mol/kg';
    case 'mol/L': return 'mol/L';
    case 'ppm': return 'ppm';
    default: return 'mol/kg';
  }
});

const presetOptions = ['Pure water', 'Seawater'];

// --- State for Charge Balance Error ---
const cbe = ref(0); // Charge Balance Error in %
const ACCEPTABLE_ERROR = 5; // % for success
const WARNING_THRESHOLD = 10; // % for warning vs. error

/**
 * Calculates the Charge Balance Error (%CBE).
 * %CBE = (Sum(cation equivalents) - Sum(anion equivalents)) / (Sum(cation equivalents) + Sum(anion equivalents)) * 100
 */
const calculateChargeBalance = () => {
  let sumCations = 0; // Sum of cation equivalents (mol/kg * charge)
  let sumAnions = 0; // Sum of anion equivalents (mol/kg * |charge|)

  for (const ion of ions) {
    const concentration = store.simulationInput.concentrations[ion];
    const charge = ionCharges[ion];
    if (charge > 0) {
      sumCations += concentration * charge;
    } else {
      sumAnions += concentration * Math.abs(charge);
    }
  }

  const totalEquivalents = sumCations + sumAnions;

  // Avoid division by zero for pure water
  if (totalEquivalents === 0) {
    cbe.value = 0;
  } else {
    cbe.value = ((sumCations - sumAnions) / totalEquivalents) * 100;
  }
};

// Call on mount for initial calculation
onMounted(calculateChargeBalance);

// Computed property to determine alert type and title based on CBE
const alertInfo = computed(() => {
  const absCbe = Math.abs(cbe.value);
  const title = `Charge balance error: ${cbe.value.toFixed(2)}%`;

  if (absCbe <= ACCEPTABLE_ERROR) {
    return { type: 'success', title };
  }
  if (absCbe <= WARNING_THRESHOLD) {
    return { type: 'warning', title };
  }
  return { type: 'error', title };
});

const updateWaterPreset = (preset: string) => {
  if (preset === "Seawater") {
    store.simulationInput.concentrations["Cl-"] = 0.546;
    store.simulationInput.concentrations["Na+"] = 0.469;
    store.simulationInput.concentrations["Mg+2"] = 0.0528;
    store.simulationInput.concentrations["SO4-2"] = 0.0282;
    store.simulationInput.concentrations["Ca+2"] = 0.0103;
    store.simulationInput.concentrations["K+"] = 0.0102;
  } else if (preset === "Pure water") {
    store.simulationInput.concentrations["Cl-"] = 0;
    store.simulationInput.concentrations["Na+"] = 0;
    store.simulationInput.concentrations["Mg+2"] = 0;
    store.simulationInput.concentrations["SO4-2"] = 0;
    store.simulationInput.concentrations["Ca+2"] = 0;
    store.simulationInput.concentrations["K+"] = 0;
  }
  // Recalculate CBE after preset is applied
  calculateChargeBalance();
};
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



.cbe-alert {
  margin-top: 10px;
}

.el-select-dropdown__item {
  font-family: 'Roboto' !important;
}
</style>