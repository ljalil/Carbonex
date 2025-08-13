<template>
  <ModelSelection />
  <UnitsSettings 
    @temperature-unit-changed="updateTemperatureUnit"
    @pressure-unit-changed="updatePressureUnit"
  />
  <WaterChemistry />
  <OperationalSettings />
</template>

<script lang="ts">
import { defineComponent } from "vue";
import ModelSelection from "./ModelSelection.vue";
import UnitsSettings from "./UnitsSettings.vue";
import WaterChemistry from "./WaterChemistry.vue";
import OperationalSettings from "./OperationalSettings.vue";

export default defineComponent({
  name: "Sidebar",
  components: {
    ModelSelection,
    UnitsSettings,
    WaterChemistry,
    OperationalSettings,
  },
  setup() {
    const updateTemperatureUnit = () => {
      // This can be used to sync any additional state if needed
      console.log("Temperature unit updated");
    };

    const updatePressureUnit = () => {
      // This can be used to sync any additional state if needed
      console.log("Pressure unit updated");
    };

    return {
      updateTemperatureUnit,
      updatePressureUnit,
    };
  },
});
</script>

<style scoped>
/* Global sidebar styles can be added here if needed */
</style>
