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
    emphasis: {type: Object as PropType<[number, number]>},
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
      grid: { left: '4%', right: '2%', bottom: '10%', top:'5%', containLabel: true },
      xAxis: [
        {
          type: 'value', name: props.xAxisLabel, nameLocation: 'center',
          nameGap: 30, min: 'dataMin', max: 'dataMax',
          position: 'bottom', axisTicks: { inside: true , interval: "auto"}
        },
        // {
        //   type: 'value', name: props.xAxisLabel, nameLocation: 'center',
        //   nameGap: 30, min: 'dataMin', max: 'dataMax',
        //   position: 'top', axisTicks: { inside: true }
        // }
      ],
      yAxis: [
        {
          type: 'value', name: props.yAxisLabel, nameLocation: 'center',
          nameGap: 30, min: 0, max: yMax.value,
          position: 'left', axisTicks: { inside: true }
        },
        // {
        //   type: 'value', name: props.yAxisLabel, nameLocation: 'center',
        //   nameGap: 30, min: 0, max: yMax.value,
        //   position: 'right', axisTicks: { inside: true }
        // }
      ],
      series: [
        {
          data: props.data,
          type: 'line',
          smooth: false,
          itemStyle: { color: '#409EFF' }
        },
        {
          data: [props.emphasis],
          type: 'line',
          smooth: false,
          symbolSize:10,
          itemStyle: {  color: 'red' }
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
  min-height: 0;
  overflow: hidden;
}

.chart {
  flex: 1;
  height: 100%;
  width: 100%;
  min-height: 0;
  overflow: hidden;
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
