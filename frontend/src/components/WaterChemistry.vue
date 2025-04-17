<template>
  <div class="sidebar-container">
    <h2>Water Chemistry</h2>
    <p class="description">Choose water composition from a predefined preset, or specify ionic species concentration and pH manually.</p>
    <div v-for="ion in ions" :key="ion.name">
      <label>
        <span class="input-name" v-html="ion.displayName"></span>
        <input type="number" v-model="ion.concentration" :placeholder="`${ion.name} concentration`">
        <span class="unit" v-html="unit"></span>
      </label>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WaterChemistry',
  data() {
    return {
      unit: 'mg/L',
      ions: [
        { name: 'Na+', displayName: 'Na<sup>+</sup>', concentration: 0 },
        { name: 'K+', displayName: 'K<sup>+</sup>', concentration: 0 },
        { name: 'Mg2+', displayName: 'Mg<sup>2+</sup>', concentration: 0 },
        { name: 'Ca2+', displayName: 'Ca<sup>2+</sup>', concentration: 0 },
        { name: 'Cl-', displayName: 'Cl<sup>-</sup>', concentration: 0 },
        { name: 'SO42-', displayName: 'SO<sub>4</sub><sup>2-</sup>', concentration: 0 },
        { name: 'HCO3-', displayName: 'HCO<sub>3</sub><sup>-</sup>', concentration: 0 },
        // Add more ions as needed
      ]
    }
  }

}
</script>

<style scoped>

</style>