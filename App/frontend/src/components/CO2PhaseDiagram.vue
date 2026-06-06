<template>
  <div class="plot-container">
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, ScatterChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';
import { provide, computed } from 'vue';

// --- ECharts Registration ---
use([
  CanvasRenderer,
  LineChart,
  ScatterChart, // Register ScatterChart for special points
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

// Provide a theme for the chart (e.g., 'dark')
provide(THEME_KEY, 'light');


// --- CO2 Physical Constants (Span and Wagner Model) ---
const P_TRIPLE = 0.51795; // MPa
const T_TRIPLE = 216.592; // K
const P_CRITICAL = 7.3773; // MPa
const T_CRITICAL = 304.1282; // K


// --- TypeScript implementation of the Span and Wagner equations ---

/**
 * Calculates the melting curve pressure for a given temperature.
 * @param T Temperature in Kelvin (K)
 * @returns Pressure in Megapascals (MPa)
 */
function meltingCurve(T: number): number {
  if (T < T_TRIPLE) return NaN; // Not valid below triple point
  const a = [1955.5390, 2055.4593];
  const term = T / T_TRIPLE - 1;
  const p_m = P_TRIPLE * (1 + a[0] * term + a[1] * term ** 2);
  return p_m;
}

/**
 * Calculates the sublimation curve pressure for a given temperature.
 * @param T Temperature in Kelvin (K)
 * @returns Pressure in Megapascals (MPa)
 */
function sublimationCurve(T: number): number {
  if (T <= 0 || T > T_TRIPLE) return NaN; // Not valid in this range
  const a = [-14.740846, 2.4327015, -5.3061778];
  const theta = 1 - T / T_TRIPLE;
  const exponent = (T_TRIPLE / T) * (a[0] * theta + a[1] * theta ** 1.9 + a[2] * theta ** 2.9);
  return Math.exp(exponent) * P_TRIPLE;
}

/**
 * Calculates the vaporization curve pressure for a given temperature.
 * @param T Temperature in Kelvin (K)
 * @returns Pressure in Megapascals (MPa)
 */
function vaporizationCurve(T: number): number {
  if (T < T_TRIPLE || T > T_CRITICAL) return NaN; // Not valid in this range
  const a = [-7.0602087, 1.9391218, -1.6463597, -3.2995634];
  const t = [1, 1.5, 2, 4];
  const theta = 1 - T / T_CRITICAL;
  let sumValue = 0;
  for (let i = 0; i < a.length; i++) {
    sumValue += a[i] * Math.pow(theta, t[i]);
  }
  return Math.exp((T_CRITICAL / T) * sumValue) * P_CRITICAL;
}

/**
 * Helper function to generate an array of [x, y] points for a curve.
 * @param func The function to call (e.g., meltingCurve)
 * @param startT Starting temperature
 * @param endT Ending temperature
 * @param steps Number of points to generate
 * @returns An array of [T, P] coordinates
 */
function generateData(func: (T: number) => number, startT: number, endT: number, steps: number): [number, number][] {
  const data: [number, number][] = [];
  const stepSize = (endT - startT) / (steps - 1);
  for (let i = 0; i < steps; i++) {
    const T = startT + i * stepSize;
    const P = func(T);
    // Ensure we only add valid points
    if (!isNaN(P)) {
      data.push([T, P]);
    }
  }
  return data;
}

// --- Generate Data for Plotting ---
const sublimationData = generateData(sublimationCurve, 150, T_TRIPLE, 100);
const vaporizationData = generateData(vaporizationCurve, T_TRIPLE, T_CRITICAL, 100);
// The melting curve is very steep, so we don't need a large temperature range to show it.
const meltingData = generateData(meltingCurve, T_TRIPLE, 230, 50);

// Dynamically compute chart options
const chartOption = computed(() => ({
  title: {
    text: 'CO₂ Phase Diagram',
    show: false,
  },
  tooltip: {
    trigger: 'axis',
    formatter: (params: any[]) => {
      let tooltipText = `Temperature: ${params[0].axisValueLabel} K<br/>`;
      params.forEach(param => {
        // param.value[1] is the pressure
        const pressure = param.value[1].toExponential(3);
        tooltipText += `${param.marker} ${param.seriesName}: ${pressure} MPa<br/>`;
      });
      return tooltipText;
    },
    textStyle: {
        fontSize: 10
    }
  },
  
  legend: {
    data: ['Sublimation', 'Vaporization', 'Melting', 'Triple Point', 'Critical Point'],
    center: 'center',
    show: true,
    visible: false,
    itemHeight: 8,
    textStyle: {
        fontSize: 11
    }
  },

  grid: {
    left: '8%',
    right: '5%',
    bottom: '10%',
    containLabel: true,
  },
  xAxis: {
    type: 'value',
    name: 'Temperature (K)',
    nameLocation: 'center',
    nameGap: 30,
    min: 150,
    max: 350,
  },
  yAxis: {
    type: 'log', // Use logarithmic scale for wide pressure range
    name: 'Pressure (MPa)',
    nameLocation: 'center',
    nameGap: 50,
  },
  series: [
    {
      name: 'Sublimation',
      data: sublimationData,
      type: 'line',
      smooth: true,
      lineStyle: { color: '#5470C6' },
      showSymbol: false,
      label: {
        show: true,
        position: 'end',
        formatter: '{a}',
        fontSize: 12
      }
    },
    {
      name: 'Vaporization',
      data: vaporizationData,
      type: 'line',
      smooth: true,
      lineStyle: { color: '#91CC75' },
      showSymbol: false,
      label: {
        show: true,
        position: 'end',
        formatter: '{a}',
        fontSize: 12
      }
    },
    {
      name: 'Melting',
      data: meltingData,
      type: 'line',
      smooth: true,
      lineStyle: { color: '#FAC858' },
      showSymbol: false,
      label: {
        show: true,
        position: 'end',
        formatter: '{a}',
        fontSize: 12
      }
    },
    {
      name: 'Triple Point',
      type: 'scatter',
      symbolSize: 12,
      data: [[T_TRIPLE, P_TRIPLE]],
      itemStyle: { color: '#EE6666' },
      label: {
        show: true,
        position: 'right',
        formatter: '{a}',
        fontSize: 10
      }
    },
    {
      name: 'Critical Point',
      type: 'scatter',
      symbolSize: 12,
      data: [[T_CRITICAL, P_CRITICAL]],
      itemStyle: { color: '#73C0DE' },
      label: {
        show: true,
        position: 'right',
        formatter: '{a}',
        fontSize: 10
      }
    },
  ],
}));

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
  min-height: 300px; /* Ensure a minimum height */
}
</style>