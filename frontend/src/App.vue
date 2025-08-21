<template>
  <html >
  <div class="app-container">
    <Header></Header>
    <el-row :gutter="20" class="main-content">
      <el-col :span="5">
        <Sidebar></Sidebar>
      </el-col>
      <el-col :span="14" class="center-column">
        <div class="center-content">
          <ActionBar></ActionBar>
          <TabsContainer></TabsContainer>
        </div>
      </el-col>
      <el-col :span="5">
        <SimulationInfo></SimulationInfo>
      </el-col>
    </el-row>
  </div>
  </html>
</template>
<script>
import axios from "axios";
import { ElButton } from 'element-plus'
import Sidebar from './components/Sidebar.vue'
import SimulationInfo from './components/SimulationInfo.vue';
import Header from './components/Header.vue';
import ActionBar from './components/ActionBar.vue';
import TabsContainer from './components/TabsContainer.vue';
import { store } from './store';

export default {
  components: { ElButton, Header, Sidebar, SimulationInfo, ActionBar, TabsContainer },
  data() {
    return {
      store
    };
  },
  computed: {
    simulationOutput() {
      return store.simulationOutput;
    }
  }
}
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
</style>