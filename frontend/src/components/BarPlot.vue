<template>
  <div class="bar-plot-container">
    <v-chart class="chart" v-if="hasData" :option="chartOption" autoresize />
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

// Define the data types
type SingleSeriesData = {label: string, value: number}[];
type MultiSeriesData = {categories: string[], series: {name: string, data: number[]}[]};

export default defineComponent({
  name: 'BarPlot',
  components: {
    VChart,
  },
  props: {
    // Array of objects with label and value properties, or multi-series data
    data: {
      type: [Array, Object] as PropType<SingleSeriesData | MultiSeriesData>,
      required: true,
    },
    xAxisLabel: {
      type: String,
      default: 'Species'
    },
    yAxisLabel: {
      type: String,
      default: 'Value'
    },

  },
  setup(props) {
    const isMultiSeries = computed(() => {
      return !Array.isArray(props.data);
    });

    const hasData = computed(() => {
      if (isMultiSeries.value) {
        const multiData = props.data as MultiSeriesData;
        return multiData.categories.length > 0 && multiData.series.length > 0;
      } else {
        const singleData = props.data as SingleSeriesData;
        return singleData.length > 0;
      }
    });

    const chartOption = computed(() => {
      if (isMultiSeries.value) {
        const multiData = props.data as MultiSeriesData;
        
        return {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: multiData.series.map(s => s.name)
          },
          grid: {
            left: '10%',
            right: '5%',
            bottom: '15%',
            top: '15%',
            containLabel: true,
          },
          xAxis: {
            type: 'category',
            data: multiData.categories,
            name: props.xAxisLabel,
            nameLocation: 'center',
            nameGap: 50,
            axisTick: { alignWithLabel: true },
            axisLabel: {
              interval: 0,
              rotate: 45,
              formatter: (value: string) => value
            }
          },
          yAxis: {
            type: 'value',
            name: props.yAxisLabel,
            nameLocation: 'center',
            nameGap: 35,
            nameTextStyle: {
              fontSize: 12
            }
          },
          series: multiData.series.map((seriesItem, index) => ({
            name: seriesItem.name,
            type: 'bar',
            data: seriesItem.data,
            barGap: 0,
            emphasis: {
              focus: 'series'
            },
            itemStyle: { 
              color: index === 0 ? '#67C23A' : '#409EFF' // Green for initial, blue for final
            }
          }))
        };
      } else {
        const singleData = props.data as SingleSeriesData;
        
        return {
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
          xAxis: {
            type: 'category',
            data: singleData.map(item => item.label),
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
            nameGap: 35,
            nameTextStyle: {
              fontSize: 12
            }
          },
          series: [
            {
              type: 'bar',
              data: singleData.map(item => item.value),
              itemStyle: { color: '#409EFF' }
            }
          ],
        };
      }
    });

    return {
      chartOption,
      hasData,
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
