<template>
  <div class="analytics-chart">
    <canvas ref="chartCanvas" :width="width" :height="height"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'

interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string
    borderWidth?: number
    tension?: number
  }>
}

interface ChartOptions {
  responsive?: boolean
  maintainAspectRatio?: boolean
  plugins?: {
    legend?: {
      display: boolean
      position: string
    }
  }
  scales?: {
    y?: {
      beginAtZero: boolean
    }
  }
}

interface Props {
  data: ChartData
  type: 'line' | 'bar' | 'pie' | 'doughnut'
  options?: ChartOptions
  width?: number
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  width: 400,
  height: 200,
  options: () => ({
    responsive: true,
    maintainAspectRatio: false
  })
})

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: any = null

// Simple chart drawing functions
const drawLineChart = (ctx: CanvasRenderingContext2D, data: ChartData, width: number, height: number) => {
  if (!data.datasets.length || !data.labels.length) return

  const padding = 40
  const chartWidth = width - 2 * padding
  const chartHeight = height - 2 * padding

  // Clear canvas
  ctx.clearRect(0, 0, width, height)

  // Set styles
  ctx.fillStyle = '#374151'
  ctx.strokeStyle = '#6b7280'
  ctx.lineWidth = 1

  // Draw axes
  ctx.beginPath()
  ctx.moveTo(padding, padding)
  ctx.lineTo(padding, height - padding)
  ctx.lineTo(width - padding, height - padding)
  ctx.stroke()

  // Draw data
  const dataset = data.datasets[0]
  if (dataset && dataset.data.length > 0) {
    const maxValue = Math.max(...dataset.data)
    const minValue = Math.min(...dataset.data)
    const valueRange = maxValue - minValue || 1

    ctx.strokeStyle = dataset.borderColor || '#7c3aed'
    ctx.lineWidth = 2
    ctx.beginPath()

    dataset.data.forEach((value, index) => {
      const x = padding + (index / (dataset.data.length - 1)) * chartWidth
      const y = height - padding - ((value - minValue) / valueRange) * chartHeight

      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // Draw points
    ctx.fillStyle = dataset.borderColor || '#7c3aed'
    dataset.data.forEach((value, index) => {
      const x = padding + (index / (dataset.data.length - 1)) * chartWidth
      const y = height - padding - ((value - minValue) / valueRange) * chartHeight

      ctx.beginPath()
      ctx.arc(x, y, 3, 0, 2 * Math.PI)
      ctx.fill()
    })
  }

  // Draw labels
  ctx.fillStyle = '#6b7280'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  
  data.labels.forEach((label, index) => {
    const x = padding + (index / (data.labels.length - 1)) * chartWidth
    ctx.fillText(label, x, height - 10)
  })
}

const drawBarChart = (ctx: CanvasRenderingContext2D, data: ChartData, width: number, height: number) => {
  if (!data.datasets.length || !data.labels.length) return

  const padding = 40
  const chartWidth = width - 2 * padding
  const chartHeight = height - 2 * padding

  // Clear canvas
  ctx.clearRect(0, 0, width, height)

  // Set styles
  ctx.fillStyle = '#374151'
  ctx.strokeStyle = '#6b7280'
  ctx.lineWidth = 1

  // Draw axes
  ctx.beginPath()
  ctx.moveTo(padding, padding)
  ctx.lineTo(padding, height - padding)
  ctx.lineTo(width - padding, height - padding)
  ctx.stroke()

  // Draw data
  const dataset = data.datasets[0]
  if (dataset && dataset.data.length > 0) {
    const maxValue = Math.max(...dataset.data)
    const barWidth = chartWidth / data.labels.length * 0.8
    const barSpacing = chartWidth / data.labels.length * 0.2

    ctx.fillStyle = dataset.backgroundColor || '#10b981'

    dataset.data.forEach((value, index) => {
      const barHeight = (value / maxValue) * chartHeight
      const x = padding + index * (chartWidth / data.labels.length) + barSpacing / 2
      const y = height - padding - barHeight

      ctx.fillRect(x, y, barWidth, barHeight)
    })
  }

  // Draw labels
  ctx.fillStyle = '#6b7280'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  
  data.labels.forEach((label, index) => {
    const x = padding + index * (chartWidth / data.labels.length) + (chartWidth / data.labels.length) / 2
    ctx.fillText(label, x, height - 10)
  })
}

const drawChart = () => {
  if (!chartCanvas.value) return

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  const width = props.width
  const height = props.height

  // Set canvas size
  chartCanvas.value.width = width
  chartCanvas.value.height = height

  switch (props.type) {
    case 'line':
      drawLineChart(ctx, props.data, width, height)
      break
    case 'bar':
      drawBarChart(ctx, props.data, width, height)
      break
    default:
      // Fallback to simple text
      ctx.fillStyle = '#6b7280'
      ctx.font = '16px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('Chart not available', width / 2, height / 2)
  }
}

onMounted(() => {
  nextTick(() => {
    drawChart()
  })
})

watch(() => props.data, () => {
  nextTick(() => {
    drawChart()
  })
}, { deep: true })

watch(() => props.type, () => {
  nextTick(() => {
    drawChart()
  })
})
</script>

<style scoped>
.analytics-chart {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

canvas {
  max-width: 100%;
  max-height: 100%;
}
</style>