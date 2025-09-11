<template>
  <div class="tab-content">

  </div>
</template>

<script>
import Plot from '../Plot.vue';
import { store } from '../../store';

export default {
  name: 'MineralTrappingTab',
  components: { 
    Plot 
  },
  data() {
    return {
      store
    };
  }
}
</script>

<style scoped>
.tab-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
