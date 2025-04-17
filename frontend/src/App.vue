<template>

  <head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto">

  </head>

  <body class="dark">
    <el-col :span="24">
      <Header></Header>
      <el-row :gutter="20">
        <el-col :span="5" :gutter="20">
          <Sidebar></Sidebar>
        </el-col>
        <el-col :span="14" :gutter="20">


            <ActionBar></ActionBar>
            <Plot :data="simulationOutput.plotData"></Plot>

        </el-col>
        <el-col :span="5">
          <SimulationInfo></SimulationInfo>
        </el-col>

      </el-row>
    </el-col>
  </body>


</template>
<script>
import axios from "axios";
import { ElButton } from 'element-plus'
import Sidebar from './components/Sidebar.vue'
import SimulationInfo from './components/SimulationInfo.vue';
import Header from './components/Header.vue';
import Plot from './components/Plot.vue';
import ActionBar from './components/ActionBar.vue';
import { store } from './store';

export default {
  components: { ElButton, Header, Sidebar, SimulationInfo, Plot, ActionBar },
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
body,
html {
  font-family: 'Roboto', sans-serif;
  margin: 0;
  padding: 0;
}
</style>