<script setup lang="ts">
import type { ChartData, ChartOptions } from 'chart.js'
import { BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Tooltip } from 'chart.js'
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

export interface ChartDataset {
  label: string
  data: number[]
  color: string
}

const props = withDefaults(
  defineProps<{
    labels: string[]
    datasets: ChartDataset[]
    heightClass?: string
    ariaLabel?: string
  }>(),
  {
    heightClass: 'h-64 sm:h-72',
    ariaLabel: 'График отчёта',
  },
)

const chartData = computed<ChartData<'bar'>>(() => ({
  labels: props.labels,
  datasets: props.datasets.map((dataset) => ({
    label: dataset.label,
    data: dataset.data,
    backgroundColor: dataset.color,
    borderRadius: 6,
    maxBarThickness: 48,
  })),
}))

const chartOptions = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: props.datasets.length > 1,
      position: 'bottom',
      labels: {
        usePointStyle: true,
        boxWidth: 8,
        boxHeight: 8,
        padding: 16,
        color: '#475569',
        font: { size: 12 },
      },
    },
    tooltip: {
      padding: 10,
      backgroundColor: '#0f172a',
      titleFont: { size: 12 },
      bodyFont: { size: 12 },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      border: { display: false },
      ticks: {
        color: '#64748b',
        maxRotation: 0,
        autoSkip: true,
        font: { size: 11 },
      },
    },
    y: {
      beginAtZero: true,
      grid: { color: '#e2e8f0' },
      border: { display: false },
      ticks: {
        color: '#64748b',
        precision: 0,
        font: { size: 11 },
      },
    },
  },
}))
</script>

<template>
  <div :class="heightClass" role="img" :aria-label="ariaLabel">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
