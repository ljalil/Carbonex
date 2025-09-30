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
import { ref, computed, onMounted, watch } from "vue";
import { store, storeActions } from "../store";
import { waterChemistryConversion } from "../units";
import { Plus } from '@element-plus/icons-vue';
import waterPresets from '@/presets/waterChemistryPresets.json';

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
  return waterChemistryConversion.getUnitLabel(store.unitPreferences.concentrationUnit);
});

// Cast imported JSON to a generic presets map for TypeScript indexing via double assertion
const presets = (waterPresets as unknown) as Record<string, Partial<Record<IonName, number>>>;
const presetOptions = Object.keys(presets);

// --- State for Charge Balance Error ---
const cbe = ref(0); // Charge Balance Error in %
const ACCEPTABLE_ERROR = 5; // % for success
const WARNING_THRESHOLD = 10; // % for warning vs. error

/**
 * Calculates the Charge Balance Error (%CBE).
 * %CBE = (Sum(cation equivalents) - Sum(anion equivalents)) / (Sum(cation equivalents) + Sum(anion equivalents)) * 100
 * Always converts to molality (mol/kg) for proper charge balance calculation regardless of current unit.
 */
const calculateChargeBalance = () => {
  // Get current concentrations and convert to molality for charge balance calculation
  const currentUnit = store.unitPreferences.concentrationUnit;
  const tempC = storeActions.getCurrentTemperatureC();
  
  // Convert current concentrations to molality (mol/kg) for accurate charge balance calculation
  let concentrationsInMolality;
  if (currentUnit === 'mol/kg') {
    // Already in molality, use directly
    concentrationsInMolality = store.simulationInput.concentrations;
  } else {
    // Convert from current unit to molality
    concentrationsInMolality = waterChemistryConversion.convert(
      store.simulationInput.concentrations,
      currentUnit,
      'mol/kg',
      tempC
    );
  }

  let sumCations = 0; // Sum of cation equivalents (mol/kg * charge)
  let sumAnions = 0; // Sum of anion equivalents (mol/kg * |charge|)

  for (const ion of ions) {
    const concentration = concentrationsInMolality[ion];
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
  // Apply preset values from JSON
  const presetValues = presets[preset] || {};
  for (const ion of ions) {
    store.simulationInput.concentrations[ion] = presetValues[ion] ?? 0;
  }
  // Recalculate CBE after preset is applied
  calculateChargeBalance();
};

// Watch for unit changes and convert values accordingly
const previousUnit = ref(store.unitPreferences.concentrationUnit);

watch(
  () => store.unitPreferences.concentrationUnit,
  (newUnit) => {
    if (newUnit !== previousUnit.value) {
      // Convert current concentrations to the new unit
      storeActions.convertWaterChemistryUnits(
        previousUnit.value,
        newUnit,
        store.simulationInput.temperature
      );
      previousUnit.value = newUnit;
      // Recalculate CBE after unit conversion
      calculateChargeBalance();
    }
  }
);

// Watch for temperature changes to recalculate CBE (affects density-dependent conversions)
watch(
  () => store.simulationInput.temperature,
  () => {
    // Recalculate CBE when temperature changes as it affects conversions
    calculateChargeBalance();
  }
);
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