<template>
  <div class="plot-container">
    <v-chart class="chart" v-if="data.length !== 0" :option="chartOption" autoresize />
    <div class="no-plot" v-else>
      <h2>No data to display</h2>
      <p>Run simulation to display the resulting plots.</p>
    </div>
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
  components: { VChart },
  props: {
    data: {
      type: Array as PropType<[number, number][]>,
      required: true,
    },
    xAxisLabel: { type: String, default: 'X Axis' },
    yAxisLabel: { type: String, default: 'Y Axis' },
    tooltipLabels: {
      type: Object as PropType<[string, string]>,
      default: () => ['X', 'Y'] as [string, string],
    },
  },
  setup(props) {
    // Compute ceiling of the max Y value (or 0 if no data)
    const yMax = computed(() => {
      if (props.data.length === 0) return 0;
      return Math.ceil(Math.max(...props.data.map(point => point[1])));
    });

    const chartOption = computed(() => ({
      title: { left: 'center' },
      tooltip: {
        trigger: 'axis',
        formatter(params: any) {
          const x = params[0].data[0].toFixed(2);
          const y = params[0].data[1].toFixed(4);
          return `${props.tooltipLabels[0]}: ${x}<br>${props.tooltipLabels[1]}: ${y}`;
        }
      },
      grid: { left: '5%', right: '5%', bottom: '5%', containLabel: true },
      xAxis: [
        {
          type: 'value', name: props.xAxisLabel, nameLocation: 'center',
          nameGap: 30, min: 'dataMin', max: 'dataMax',
          position: 'bottom', axisTicks: { inside: true }
        },
        {
          type: 'value', name: props.xAxisLabel, nameLocation: 'center',
          nameGap: 30, min: 'dataMin', max: 'dataMax',
          position: 'top', axisTicks: { inside: true }
        }
      ],
      yAxis: [
        {
          type: 'value', name: props.yAxisLabel, nameLocation: 'center',
          nameGap: 30, min: 0, max: yMax.value,
          position: 'left', axisTicks: { inside: true }
        },
        {
          type: 'value', name: props.yAxisLabel, nameLocation: 'center',
          nameGap: 30, min: 0, max: yMax.value,
          position: 'right', axisTicks: { inside: true }
        }
      ],
      series: [
        {
          data: props.data,
          type: 'line',
          smooth: false,
        },
      ],
    }));

    return { chartOption };
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
