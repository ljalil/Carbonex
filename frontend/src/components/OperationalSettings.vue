<template>
    <div class="sidebar-container">
      <h2>Operational Settings</h2>
      <p class="description">Choose values for pressure and temperature.</p>
      <div>
        <label>
          <span class="input-name">Temperature</span>
          <input type="number" v-model="temperature" placeholder="Temperature">
          <span class="unit" v-html="temperature_unit"></span>
        </label>
      </div>
      <div>
        <label>
          <span class="input-name">Pressure</span>
          <input type="number" v-model="pressure" placeholder="Pressure">
          <span class="unit" v-html="pressure_unit"></span>
        </label>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'OperationalSettings',
    data() {
      return {
        temperature: 0,
        pressure: 0,
        temperature_unit: '°C',
        pressure_unit: 'bar'
      }
    }
  }
  </script>
  
  <style scoped>
  .operational-settings {
    background-color: #1E1E1E;
    
    padding: 15px;
    border-radius: 8px;
  }
  </style>