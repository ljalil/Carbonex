<template>
  <div class="plot-container">
    <div v-if="hasData" class="chart-wrapper">
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
    <div class="no-plot" v-else>
      <h2>No data to display</h2>
      <p>Run simulation to display the resulting plots.</p>
    </div>
  </div>
</template>

<script lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { HeatmapChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, VisualMapComponent } from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';

import { defineComponent, provide, computed } from 'vue';
import type { PropType } from 'vue';

// Define types for heatmap data
export interface HeatmapData {
  grid_data: [number, number, number][]; // [temp_index, pressure_index, CO2_solubility]
  temperatures: number[]; // Temperature values in Kelvin
  pressures: number[]; // Pressure values in MPa
}

// Register required components for ECharts
use([
  CanvasRenderer,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent,
]);

// Provide the theme for the chart
provide(THEME_KEY, 'dark');

export default defineComponent({
  name: 'HeatMap',
  components: {
    VChart,
  },
  props: {
    data: {
      type: Object as PropType<HeatmapData>,
      required: true
    },
    xAxisLabel: {
      type: String,
      default: 'Temperature (K)'
    },
    yAxisLabel: {
      type: String,
      default: 'Pressure (MPa)'
    },
    title: {
      type: String,
      default: 'CO2 Solubility Heat Map'
    },
  },
  setup(props) {
    // Check if we have valid data
    const hasData = computed(() => {
      return props.data &&
        props.data.grid_data &&
        props.data.grid_data.length > 0 &&
        props.data.temperatures &&
        props.data.temperatures.length > 0 &&
        props.data.pressures &&
        props.data.pressures.length > 0;
    });

    // Dynamically compute chart options
    const chartOption = computed(() => {
      if (!hasData.value) {
        return {};
      }

      // Convert temperature from Kelvin to Celsius for display
      const temperatureLabels = props.data.temperatures.map(t => t.toFixed(1));
      const pressureLabels = props.data.pressures.map(p => p.toFixed(1));

      // Find min and max values for visual map
      const solubilityValues = props.data.grid_data.map(item => item[2]);
      const minValue = Math.min(...solubilityValues);
      const maxValue = Math.max(...solubilityValues);

      return {
        title: {
          text: props.title,
          left: 'center',
          show: false,

        },
        tooltip: {
          position: 'top',
          formatter: function (params: any) {
            const tempIndex = params.data[0];
            const pressureIndex = params.data[1];
            const solubility = params.data[2];
            const tempK = (props.data.temperatures[tempIndex]).toFixed(2);
            const pressure = props.data.pressures[pressureIndex].toFixed(2);
            return `Temperature: ${tempK} K<br/>Pressure: ${pressure} MPa<br/>CO₂ Solubility: ${solubility.toFixed(4)} mol/kg`;
          }
        },
        grid: {
          left: '10%',
          right: '15%',
          bottom: '10%',
          top: '15%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: temperatureLabels,
          name: 'Temperature (K)',
          nameLocation: 'center',
          nameGap: 30,

        },
        yAxis: {
          type: 'category',
          data: pressureLabels,
          name: props.yAxisLabel,
          nameLocation: 'center',
          nameGap: 50,
          min: 0,
          max: 100,
          splitNumber: 20,

        },
        visualMap: {
          min: minValue,
          max: maxValue,
          calculable: true,
          realtime: false,
          orient: 'horizontal',
          left: 'left',
          inRange: {
            color: [
              '#313695',
              '#4575b4',
              '#74add1',
              '#abd9e9',
              '#e0f3f8',
              '#ffffbf',
              '#fee090',
              '#fdae61',
              '#f46d43',
              '#d73027',
              '#a50026'
            ]
          },

        },
        series: [
          {
            name: 'CO2 Solubility',
            type: 'heatmap',
            data: props.data.grid_data,
            emphasis: {
              itemStyle: {

                borderWidth: 1
              }
            },
            progressive: 1000,
            animation: false
          }
        ]
      };
    });

    return {
      hasData,
      chartOption,
    };
  },
});
</script>

<style scoped>
.plot-container {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.chart-wrapper {
  flex: 1;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.chart {
  flex: 1;
  height: 100%;
  width: 100%;
  min-height: 300px;
  /* Ensure a minimum height */
}

.no-plot {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}
</style>
