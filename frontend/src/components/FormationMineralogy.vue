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
            :min="0"
            :precision="4"
            :step="0.1"
            style="flex: 1"
          >
            <template #suffix>
              <span>moles</span>
            </template>
          </el-input-number>
        </el-form-item>
      </template>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
// Vue imports
import { computed } from 'vue'; // may not be needed
import { store } from '../store';
import { Plus } from '@element-plus/icons-vue';

type MineralName =
  | 'Quartz'
  | 'Albite'
  | 'K-feldspar'
  | 'Illite'
  | 'Kaolinite'
  | 'Calcite'
  | 'Dolomite'
  | 'Smectite'
  | 'Siderite'
  | 'Chlorite';

// List of all minerals
const minerals: MineralName[] = [
  'Quartz', 'Albite', 'K-feldspar', 'Illite',
  'Kaolinite', 'Calcite', 'Dolomite',
  'Smectite', 'Siderite', 'Chlorite'
];
// Grouped mineral categories
const carbonates: MineralName[] = ['Calcite', 'Siderite', 'Dolomite'];
const clays: MineralName[] = ['Illite', 'Kaolinite', 'Smectite'];
const feldspars: MineralName[] = ['Albite', 'K-feldspar'];
const quartzGroup: MineralName[] = ['Quartz'];
const other: MineralName[] = minerals.filter(m =>
  ![...carbonates, ...clays, ...feldspars, ...quartzGroup].includes(m)
) as MineralName[];
// Map group names to their mineral arrays
const mineralGroups: Record<string, MineralName[]> = {
  Carbonates: carbonates,
  Clays: clays,
  Feldspars: feldspars,
  Quartz: quartzGroup,
  Other: other
};
// Import presets for mineralogy
import mineralogyPresets from '@/presets/mineralogyPresets.json';
// Cast imported JSON for TS indexing
const presets = (mineralogyPresets as unknown) as Record<string, Partial<Record<MineralName, number>>>;
// Available preset options
const presetOptions = Object.keys(presets);
// Apply selected preset values to store
const updateMineralogyPreset = (preset: string) => {
  const values = presets[preset] || {};
  for (const m of minerals) {
    store.simulationInput.minerals[m] = values[m] ?? 0;
  }
};
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
</style>
