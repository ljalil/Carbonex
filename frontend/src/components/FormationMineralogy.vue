<template>
  <el-card class="formation-mineralogy-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>Formation mineralogy</span>
        <el-button size="small" :icon="Plus" circle />
      </div>
    </template>



    <el-form label-position="left" label-width="auto">
      <!-- Preset selector -->
      <el-form-item label="Preset">
        <el-select
          size="small"
          v-model="store.simulationInput.mineralogyPreset"
          placeholder="Select option"
          @change="updateMineralogyPreset"
          style="width: 100%"
        >
          <el-option
            v-for="option in presetOptions"
            :key="option"
            :label="option"
            :value="option"
          />
        </el-select>
      </el-form-item>
      <template v-for="(groupMins, groupName) in mineralGroups" :key="groupName">
        <el-text tag="b">{{ groupName }}</el-text>
        <el-form-item
          v-for="mineral in groupMins"
          :key="mineral"
          :label="mineral"
        >
          <el-input-number
            v-model="store.simulationInput.minerals[mineral]"
            size="small"
            :min="-0.1"
            :precision="4"
            :step="0.1"
            style="flex: 1"
          >
            <template #suffix>
              <span>{{ formationMineralogyConversion.getUnitLabel(store.unitPreferences.mineralogyUnit) }}</span>
            </template>
          </el-input-number>
        </el-form-item>
      </template>
    </el-form>

        <el-alert style="margin-top: 10px !important;" :closable="false">Value of 0 allows the mineral to precipitate. Values below 0 prohibit its precipitation.</el-alert>
    
    <template #footer v-if="store.unitPreferences.mineralogyUnit === 'w/w'">
      <el-alert
        :title="alertInfo.title"
        :type="alertInfo.type as 'error' | 'success' | 'warning' | 'info'"
        center
        show-icon
        :closable="false"
        class="sum-alert"
      />
    </template>
  </el-card>
</template>

<script setup lang="ts">
// Vue imports
import { computed, watch, ref, onMounted } from 'vue';
import { store } from '../store';
import { formationMineralogyConversion } from '../units';
import { Plus } from '@element-plus/icons-vue';

type MineralName =
  | 'Quartz'
  | 'Albite'
  | 'K-feldspar'
  | 'Illite'
  | 'Kaolinite'
  | 'Calcite'
  | 'Dolomite'
  | 'Siderite'
  | 'Chlorite'
  | 'Pyrite';

// List of all minerals (only those that exist in the store)
const minerals: MineralName[] = [
  'Quartz', 'Albite', 'K-feldspar', 'Illite',
  'Kaolinite', 'Calcite', 'Dolomite',
'Siderite', 'Chlorite', 'Pyrite'
];
// Grouped mineral categories
const carbonates: MineralName[] = ['Calcite', 'Siderite', 'Dolomite'];
const clays: MineralName[] = ['Illite', 'Kaolinite', 'Chlorite'];
const feldspars: MineralName[] = ['Albite', 'K-feldspar'];
const quartzGroup: MineralName[] = ['Quartz'];
const sulfides: MineralName[] = ['Pyrite'];
// Map group names to their mineral arrays
const mineralGroups: Record<string, MineralName[]> = {
  Carbonates: carbonates,
  Clays: clays,
  Feldspars: feldspars,
  Quartz: quartzGroup,
  Sulfides: sulfides
};
// Import presets for mineralogy
import mineralogyPresets from '@/presets/mineralogyPresets.json';
// Cast imported JSON for TS indexing - presets may contain more minerals than store
const presets = (mineralogyPresets as unknown) as Record<string, Record<string, number>>;
// Available preset options
const presetOptions = Object.keys(presets);

// Keep track of the previous unit to handle conversions
const previousUnit = ref(store.unitPreferences.mineralogyUnit);

// Weight fraction sum logic (only when unit is w/w)
const sumWeightFractions = computed(() => {
  if (store.unitPreferences.mineralogyUnit !== 'w/w') return 0;
  return minerals.reduce((sum, mineral) => sum + store.simulationInput.minerals[mineral], 0);
});

const calculateSum = () => { void sumWeightFractions.value };
onMounted(calculateSum);

const alertInfo = computed(() => {
  const sum = sumWeightFractions.value;
  const title = `Weight fractions sum: ${sum.toFixed(2)}`;
  return Math.abs(sum - 1) < 1e-6
    ? { type: 'success', title }
    : { type: 'error', title: title + ' (should be 1)' };
});

// Apply selected preset values to store
const updateMineralogyPreset = (preset: string) => {
  const values = presets[preset] || {};
  
  if (store.unitPreferences.mineralogyUnit === 'moles') {
    // Convert from weight fraction to moles
    // Only include minerals that exist in both preset and store
    const wtFracValues: Record<string, number> = {};
    for (const m of minerals) {
      wtFracValues[m] = values[m] ?? 0;
    }
    
    const molesValues = formationMineralogyConversion.toMoles(wtFracValues, 'w/w');
    
    // Apply converted values to store
    for (const m of minerals) {
      store.simulationInput.minerals[m] = molesValues[m] ?? 0;
    }
  } else {
    // Already in w/w format, only apply store minerals
    for (const m of minerals) {
      store.simulationInput.minerals[m] = values[m] ?? 0;
    }
  }
};

// Watch for unit changes and convert mineral values
watch(() => store.unitPreferences.mineralogyUnit, (newUnit, oldUnit) => {
  if (newUnit !== oldUnit && oldUnit) {
    // Convert current mineral values to new unit
    const currentMinerals = { ...store.simulationInput.minerals };
    const convertedMinerals = formationMineralogyConversion.convert(
      currentMinerals, 
      oldUnit, 
      newUnit
    );
    
    // Update store with converted values
    for (const mineral of minerals) {
      store.simulationInput.minerals[mineral] = convertedMinerals[mineral] ?? 0;
    }
  }
  previousUnit.value = newUnit;
});
</script>

<style scoped>
.formation-mineralogy-card {
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

.sum-alert {
  margin-top: 10px;
}
</style>
