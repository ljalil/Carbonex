<template>
    <div id="header">
    <h1>Carbonex  <span class="subtext">A simulator for CO<sub>2</sub> dissolution in formation water.</span></h1>

    <div id="links-and-controls">
        <a href="#" @click="openAboutDialog">About</a>
        <el-icon :size="30" :color="color">
      <Sunny />
    </el-icon>
    </div>

</div>

  <el-dialog
    v-model="aboutDialogVisible"
    class="about-dialog"
    title="About Carbonex"
    width="50%"
    transition="dialog-fade"
  >
    <div class="about-content">
      <p>
        Carbonex is a tool to analyze CO₂ dissolution  in formation water under geological conditions.
      </p>
      
      <p>It supports different solubility models:</p>
      
      <ul>
        <li>PHREEQC Geochemical simulation software</li>
        <li>Duan and Sun model (2006) [<a href="https://doi.org/10.1016/j.marchem.2005.09.001">reference</a>]</li>
        <li>Carbonex, a physics-informed machine learning model</li>
      </ul>

      <div class="version-info">
        <p><strong>Version:</strong> 1.0.0</p>
        <p><strong>Last Updated:</strong> August 2025</p>
      </div>
    </div>
    <template #footer>
      <el-button @click="aboutDialogVisible = false">Close</el-button>
    </template>
  </el-dialog>
</template>

<script>
import { ref } from 'vue'
import {
  Sunny,
  Delete,
  Edit,
  Eleme,
  PartlyCloudy,
  Search,
  Share,
  Upload,
} from "@element-plus/icons-vue";

export default {
  components: {
    Sunny,
    Delete,
    Edit,
    Eleme,
    PartlyCloudy,
    Search,
    Share,
    Upload,
  },
  setup() {
    const aboutDialogVisible = ref(false)
    
    const openAboutDialog = () => {
      aboutDialogVisible.value = true
    }

    return {
      aboutDialogVisible,
      openAboutDialog
    }
  }
}
</script>

<style scoped>

h1 {

    font-size: 1.5em;
    font-weight: 100;
    margin: 5px 0px;
}
#header {
    box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    padding: 0 10px 0 10px;

}

#links-and-controls{
    display: flex;
    align-items: center;
}

a {
    margin-right: 10px;
    text-decoration: none;
    color: black;
    cursor: pointer;
}

a:hover {
    color: #409eff;
    text-decoration: underline;
}

.subtext {
    font-size: 0.6em;
    font-weight: 100;
    font-style: italic;
    color: gray;
}

.about-content {
    line-height: 1.6;
}

.about-content h3 {
    color: #409eff;
    margin-bottom: 15px;
    font-size: 1.3em;
}

.about-content h4 {
    color: #333;
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 1.1em;
}

.about-content ul {
    margin-left: 20px;
    margin-bottom: 15px;
}

.about-content li {
    margin-bottom: 5px;
}

.version-info {
    margin-top: 25px;
    padding-top: 15px;
    border-top: 1px solid #eee;
    color: #666;
    font-size: 0.9em;
}
</style>