<template>
  <div class="bar-plot-container">
    <v-chart class="chart" v-if="data.length !== 0" :option="chartOption" autoresize />
    <div class="no-plot" v-else>
      <h2>No data to display</h2>
      <p>Run simulation to display the resulting bar chart.</p>
    </div>
  </div>
</template>

<script lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';

import { defineComponent, provide, computed } from 'vue';
import type { PropType } from 'vue';

// Register required components for ECharts
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

// Provide the theme for the chart
provide(THEME_KEY, 'dark');

export default defineComponent({
  name: 'BarPlot',
  components: {
    VChart,
  },
  props: {
    // Array of objects with label and value properties
    data: {
      type: Array as PropType<{label: string, value: number}[]>,
      required: true,
    },
    xAxisLabel: {
      type: String,
      default: 'Species'
    },
    yAxisLabel: {
      type: String,
      show: false,
      
    },

  },
  setup(props) {
    const chartOption = computed(() => ({

      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: function(params: any) {
          const value = params[0].value.toFixed(4);
          return `${params[0].name}: ${value}`;
        }
      },
      grid: {
        left: '5%',
        right: '5%',
        bottom: '15%',
        top: '5%',
        containLabel: true,
      },
      // Configure vertical bar orientation with category x-axis and value y-axis
      xAxis: {
        type: 'category',
        data: props.data.map(item => item.label),
        name: props.xAxisLabel,
        nameLocation: 'center',
        nameGap: 50,
        axisTick: { alignWithLabel: true, rotation: 90 },
        axisLabel: {
          interval: 0,
          rotate: 90,
          formatter: (value: string) => value
        }
      },
      yAxis: {
        type: 'value',
        name: props.yAxisLabel,
        nameLocation: 'center',
        nameGap: 30,
        min: 0,
        max: 1,
      },
      series: [
        {
          type: 'bar',
          data: props.data.map(item => item.value),
          itemStyle: { color: '#409EFF' }
        }
      ],
    }));

    return {
      chartOption,
    };
  },
});
</script>

<style scoped>
.bar-plot-container {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.chart {
  flex: 1;
  height: 100%;
  width: 100%;
  min-height: 200px; /* Ensure a minimum height */
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
