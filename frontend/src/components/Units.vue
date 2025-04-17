<template>
  <div class="sidebar-container">
    <h2>Units</h2>
    <p class="description">Choose values for pressure and temperature.</p>
    

    <div>
      <label>
      <span class="input-name">Temperature</span>
      <DropDownMenu :options="temperatureUnitOptions" @select="handleSelect" />
    </label>
    </div>
    <div>
      <label>
      <span class="input-name">Pressure</span>
      <DropDownMenu :options="pressureUnitOptions" @select="handleSelect" />
    </label>
    </div>
  </div>
</template>

<script>
import DropDownMenu from './DropDownMenu.vue';

export default {
  name: 'Units',
  components: {
    DropDownMenu
  },
  data() {
    return {
      temperatureUnit: 'celsius',
      pressureUnit: 'bar',
      temperatureUnitOptions: ['Celcius', 'Kelvin', 'Fahrenheit'],
      pressureUnitOptions: ['Atmosphere', 'Bar', 'PSI', 'Pascal'],

    }
  },
  methods: {
    handleSelect(option) {
      console.log('Selected option:', option);
    },
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
    }
  }
}
</script>

<style scoped>


.unit-group {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
}

.unit-group h3 {
  margin-right: 20px;
}

.radio-group {
  display: flex;
  flex-direction: column;
}

.radio-group label {
  margin-bottom: 5px;
}
</style>