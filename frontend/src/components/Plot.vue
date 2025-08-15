<template>
  <v-chart class="chart" v-if="data.length !== 0" :option="chartOption" autoresize />
  <div class="no-plot" v-else>
    <h2>No data to display</h2>
    <p>Run simulation to display the resulting plots.</p>
    </div>
</template>

<script lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';

import { defineComponent, provide, computed } from 'vue';
import type { PropType } from 'vue';
import { progressProps } from 'element-plus';





// Register required components for ECharts
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

// Provide the theme for the chart
provide(THEME_KEY, 'dark');

export default defineComponent({
  name: 'Plot',
  components: {
    VChart,
  },
  props: {
    // Use PropType for type safety
    data: {
      type: Array as PropType<[number, number][]>, // Array of [number, number] pairs
      required: true,
    },
  },
  setup(props) {
    // Dynamically compute chart options using props.data
    const chartOption = computed(() => ({
      title: {
        left: 'center',
      },
      tooltip: {
        trigger: 'axis',
        formatter: function(params: any) {
          // Extract the x and y values from the data point
          const xValue = params[0].data[0].toFixed(2);
          const yValue = params[0].data[1].toFixed(4);
          // Return formatted string with labels
          return `Pressure: ${xValue} MPa<br>Dissolved CO2: ${yValue} mol/kg`;
        }
      },
      grid: {
        left: '5%',
        right: '5%',
        bottom: '5%',
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        name: 'Pressure (MPa)',
        nameLocation: 'center',
        nameGap: 30,
      },
      yAxis: {
        type: 'value',
        name: 'Dissolved CO2 (mol/kg)',
        nameLocation: 'center',
        nameGap: 30,
      },
      series: [
        {
          data: props.data, // Use the passed prop here
          type: 'line',
          smooth: false,
        },
      ],
    }));

    return {
      chartOption,
    };
  },
});
</script>

<style scoped>
.chart, .no-plot {
  height: 90%;
}
</style>
