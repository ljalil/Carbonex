<template>
    <div id="header">
    <h1>Carbonex  <span class="subtext">A simulator for CO<sub>2</sub> dissolution in formation water.</span></h1>

    <div id="links-and-controls">
        <a href="#">About</a>
        <el-icon :size="30" :color="color">
      <Sunny />
    </el-icon>
    </div>

</div>
</template>

<script>
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

}

#links-and-controls{
    display: flex;
    align-items: center;
}

a {
    margin-right: 10px;
    text-decoration: none;
    color: black;
}

.subtext {
    font-size: 0.6em;
    font-weight: 100;
    font-style: italic;
    color: gray;
}
</style>