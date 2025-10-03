<template>
  <el-tabs 
    stretch="true" 
    tab-position="top"
    class="tabs-container"
    v-model="activeTab"
  >
    <el-tab-pane 
      v-for="tab in tabs" 
      :key="tab.name"
      :label="tab.label" 
      :name="tab.name"
      class="tab-pane"
    >
      <component :is="tab.component" />
    </el-tab-pane>
  </el-tabs>
</template>

<script>
import {
  SolubilityTrappingTab,
  MineralTrappingTab,
  SensitivityAnalysisTab
} from './tabs/index.js';

export default {
  name: 'TabsContainer',
  components: {
    SolubilityTrappingTab,
    MineralTrappingTab,
    SensitivityAnalysisTab
  },
  data() {
    return {
      activeTab: 'solubility-trapping',
      tabs: [
        {
          name: 'solubility-trapping',
          label: 'Solubility trapping',
          component: 'SolubilityTrappingTab'
        },
        {
          name: 'mineral-trapping',
          label: 'Mineral trapping',
          component: 'MineralTrappingTab'
        },
        {
          name: 'sensitivity-analysis',
          label: 'Sensitivity analysis',
          component: 'SensitivityAnalysisTab'
        }
      ]
    };
  }
}
</script>

<style scoped>
.tabs-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0; /* Important for flex children */
  height: 100%; /* Take full available height */
  margin-top: 15px; /* Space between ActionBar and tabs */
  margin-bottom: 0; /* Remove bottom margin to use full space */
  overflow: hidden; /* Prevent this container from creating scroll */
}

.tabs-container :deep(.el-tabs__content) {
  flex: 1;
  height: 100%;
  overflow: hidden; /* Prevent tab content from creating scroll */
}

.tab-pane {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Ensure individual tab panes don't overflow */
}

/* Make sure the plot component fills the tab */

</style>
