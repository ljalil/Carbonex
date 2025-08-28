<template>
  <html >
  <div class="common-layout">
    <el-container>
    <el-header><Header></Header></el-header>
    <el-container>
    <el-aside width="20%" class="sidebar-container">
      <el-scrollbar height="100%">
        <Sidebar></Sidebar>
      </el-scrollbar>
    </el-aside>
      <el-main>
        <div class="center-content">
          <ActionBar></ActionBar>
          <TabsContainer></TabsContainer>
        </div>
        </el-main>
        <el-aside width="25%">
        <SimulationInfo></SimulationInfo>
        </el-aside>

    </el-container>
    </el-container>
  </div>
  </html>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import Sidebar from './components/Sidebar.vue'
import SimulationInfo from './components/SimulationInfo.vue'
import Header from './components/Header.vue'
import ActionBar from './components/ActionBar.vue'
import TabsContainer from './components/TabsContainer.vue'
import { store } from './store'

// Reactive getters
const simulationOutput = computed(() => store.simulationOutput)
</script>

<style scoped>
/* Apply font to the entire app */
* {
  font-family: 'Roboto' !important;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Roboto' !important;
}

.main-content {
  flex: 1;
  height: calc(100vh - 60px); /* Adjust based on header height */
  margin: 0 !important;
}

.center-column {
  height: 100%;
}

.center-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-container {
  height: calc(100vh - 60px); /* Adjust based on header height */
}

.sidebar-container .el-scrollbar {
  height: 100%;
}

.sidebar-content {
  padding-right: 15px;
}
</style>