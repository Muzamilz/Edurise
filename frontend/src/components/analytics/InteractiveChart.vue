<template>
  <div class="interactive-chart">
    <div class="chart-header">
      <div class="chart-title-section">
        <h3 class="chart-title">{{ config.title }}</h3>
        <p v-if="config.subtitle" class="chart-subtitle">{{ config.subtitle }}</p>
      </div>
      
      <div class="chart-controls">
        <!-- Interactive Filters -->
        <div class="filter-controls">
          <select 
            v-if="showPeriodFilter"
            v-model="selectedPeriod"
            @change="updatePeriod"
            class="filter-select"
          >
            <option value="day">Daily</option>
            <option value="week">Weekly</option>
            <option value="month">Monthly</option>
          </select>
          
          <select 
            v-if="showCategoryFilter && categories.length"
            v-model="selectedCategory"
            @change="updateCategory"
            class="filter-select"
          >
            <option value="">All Categories</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
          
          <button 
            v-if="showRefresh"
            @click="refreshData"
            :disabled="loading"
            class="refresh-btn"
            :class="{ 'animate-spin': loading }"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        
        <!-- Chart Type Switcher -->
        <div v-if="allowTypeSwitch" class="chart-type-switcher">
          <button 
            v-for="type in availableTypes" 
            :key="type"
            @click="switchChartType(type)"
            :class="['type-btn', { active: config.type === type }]"
            :title="`Switch to ${type} chart`"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path v-if="type === 'line'" d="M2 10l3-3 3 3 6-6 2 2" />
              <path v-else-if="type === 'bar'" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
              <path v-else-if="type === 'pie'" d="M10 18a8 8 0 100-16 8 8 0 000 16zM4.332 8.027a6.012 6.012 0 011.912-2.706C6.512 5.73 6.974 6 7.5 6A1.5 1.5 0 019 7.5V8a2 2 0 004 0 2 2 0 011.523-1.943A5.977 5.977 0 0116 10c0 3.314-2.686 6-6 6s-6-2.686-6-6a7.966 7.966 0 01.332-2.027z" />
              <path v-else d="M2 10l3-3 3 3 6-6 2 2" /> 
           </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Chart Container -->
    <div class="chart-container">
      <AnalyticsChart
        :chart-data="filteredChartData"
        :config="chartConfig"
        :loading="loading"
        :error="error"
        @refresh="handleRefresh"
        @export="handleExport"
      />
    </div>
    
    <!-- Interactive Data Filters -->
    <div v-if="showDataFilters" class="data-filters">
      <div class="filter-section">
        <h4 class="filter-title">Data Filters</h4>
        
        <div class="filter-grid">
          <div v-if="showDateRange" class="filter-group">
            <label class="filter-label">Date Range</label>
            <div class="date-inputs">
              <input 
                v-model="dateRange.start"
                type="date"
                class="date-input"
                @change="applyDateFilter"
              />
              <span class="date-separator">to</span>
              <input 
                v-model="dateRange.end"
                type="date"
                class="date-input"
                @change="applyDateFilter"
              />
            </div>
          </div>
          
          <div v-if="showValueRange" class="filter-group">
            <label class="filter-label">Value Range</label>
            <div class="range-inputs">
              <input 
                v-model.number="valueRange.min"
                type="number"
                placeholder="Min"
                class="range-input"
                @input="applyValueFilter"
              />
              <span class="range-separator">-</span>
              <input 
                v-model.number="valueRange.max"
                type="number"
                placeholder="Max"
                class="range-input"
                @input="applyValueFilter"
              />
            </div>
          </div>
          
          <div class="filter-actions">
            <button @click="resetFilters" class="reset-filters-btn">
              Reset Filters
            </button>
            <button @click="applyAllFilters" class="apply-filters-btn">
              Apply Filters
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Data Summary -->
    <div v-if="showSummary && filteredChartData.length" class="data-summary">
      <div class="summary-stats">
        <div class="stat-item">
          <span class="stat-label">Total Points:</span>
          <span class="stat-value">{{ filteredChartData.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Max Value:</span>
          <span class="stat-value">{{ formatValue(maxValue) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Min Value:</span>
          <span class="stat-value">{{ formatValue(minValue) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Average:</span>
          <span class="stat-value">{{ formatValue(averageValue) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import AnalyticsChart from './AnalyticsChart.vue'
import type { ChartDataPoint, ChartConfig } from '@/services/analytics'
import { AnalyticsService } from '@/services/analytics'

interface Props {
  chartData: ChartDataPoint[]
  config: ChartConfig
  loading?: boolean
  error?: string | null
  showPeriodFilter?: boolean
  showCategoryFilter?: boolean
  showRefresh?: boolean
  allowTypeSwitch?: boolean
  showDataFilters?: boolean
  showDateRange?: boolean
  showValueRange?: boolean
  showSummary?: boolean
  categories?: string[]
  availableTypes?: Array<'line' | 'bar' | 'pie' | 'doughnut' | 'area'>
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
  showPeriodFilter: true,
  showCategoryFilter: false,
  showRefresh: true,
  allowTypeSwitch: true,
  showDataFilters: false,
  showDateRange: false,
  showValueRange: false,
  showSummary: true,
  categories: () => [],
  availableTypes: () => ['line', 'bar', 'pie', 'doughnut']
})

const emit = defineEmits<{
  refresh: []
  export: [data: ChartDataPoint[]]
  periodChange: [period: string]
  categoryChange: [category: string]
  typeChange: [type: string]
  filterChange: [filters: any]
}>()

// Reactive state
const selectedPeriod = ref('month')
const selectedCategory = ref('')
const chartConfig = ref<ChartConfig>({ ...props.config })
const dateRange = ref({
  start: '',
  end: ''
})
const valueRange = ref({
  min: null as number | null,
  max: null as number | null
})

// Computed properties
const filteredChartData = computed(() => {
  let data = [...props.chartData]
  
  // Apply category filter
  if (selectedCategory.value && props.showCategoryFilter) {
    data = data.filter(item => 
      item.metadata?.category === selectedCategory.value
    )
  }
  
  // Apply date range filter
  if (dateRange.value.start && dateRange.value.end && props.showDateRange) {
    const startDate = new Date(dateRange.value.start)
    const endDate = new Date(dateRange.value.end)
    
    data = data.filter(item => {
      if (!item.date) return true
      const itemDate = new Date(item.date)
      return itemDate >= startDate && itemDate <= endDate
    })
  }
  
  // Apply value range filter
  if ((valueRange.value.min !== null || valueRange.value.max !== null) && props.showValueRange) {
    data = data.filter(item => {
      if (valueRange.value.min !== null && item.value < valueRange.value.min) return false
      if (valueRange.value.max !== null && item.value > valueRange.value.max) return false
      return true
    })
  }
  
  return data
})

const maxValue = computed(() => {
  if (!filteredChartData.value.length) return 0
  return Math.max(...filteredChartData.value.map(item => item.value))
})

const minValue = computed(() => {
  if (!filteredChartData.value.length) return 0
  return Math.min(...filteredChartData.value.map(item => item.value))
})

const averageValue = computed(() => {
  if (!filteredChartData.value.length) return 0
  const sum = filteredChartData.value.reduce((acc, item) => acc + item.value, 0)
  return sum / filteredChartData.value.length
})

// Methods
const updatePeriod = () => {
  emit('periodChange', selectedPeriod.value)
}

const updateCategory = () => {
  emit('categoryChange', selectedCategory.value)
}

const switchChartType = (type: string) => {
  chartConfig.value = { ...chartConfig.value, type: type as any }
  emit('typeChange', type)
}

const refreshData = () => {
  emit('refresh')
}

const handleRefresh = () => {
  refreshData()
}

const handleExport = (data: ChartDataPoint[]) => {
  emit('export', data)
}

const applyDateFilter = () => {
  emit('filterChange', {
    dateRange: dateRange.value,
    category: selectedCategory.value,
    valueRange: valueRange.value
  })
}

const applyValueFilter = () => {
  emit('filterChange', {
    dateRange: dateRange.value,
    category: selectedCategory.value,
    valueRange: valueRange.value
  })
}

const applyAllFilters = () => {
  emit('filterChange', {
    dateRange: dateRange.value,
    category: selectedCategory.value,
    valueRange: valueRange.value,
    period: selectedPeriod.value
  })
}

const resetFilters = () => {
  selectedCategory.value = ''
  dateRange.value = { start: '', end: '' }
  valueRange.value = { min: null, max: null }
  selectedPeriod.value = 'month'
  
  emit('filterChange', {
    dateRange: dateRange.value,
    category: selectedCategory.value,
    valueRange: valueRange.value,
    period: selectedPeriod.value
  })
}

const formatValue = (value: number): string => {
  return AnalyticsService.formatNumber(value)
}

// Watch for config changes
watch(
  () => props.config,
  (newConfig) => {
    chartConfig.value = { ...newConfig }
  },
  { deep: true }
)
</script>

<style scoped>
.interactive-chart {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
}

.chart-header {
  @apply flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6 space-y-4 lg:space-y-0;
}

.chart-title-section {
  @apply flex-1;
}

.chart-title {
  @apply text-lg font-semibold text-gray-900;
}

.chart-subtitle {
  @apply text-sm text-gray-600 mt-1;
}

.chart-controls {
  @apply flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4;
}

.filter-controls {
  @apply flex flex-wrap gap-2;
}

.filter-select {
  @apply border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.refresh-btn {
  @apply inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed;
}

.chart-type-switcher {
  @apply flex space-x-1 bg-gray-100 rounded-md p-1;
}

.type-btn {
  @apply inline-flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-500 hover:text-gray-700 hover:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.type-btn.active {
  @apply bg-white text-gray-900 shadow-sm;
}

.chart-container {
  @apply mb-6;
}

.data-filters {
  @apply border-t border-gray-200 pt-6 mb-6;
}

.filter-section {
  @apply space-y-4;
}

.filter-title {
  @apply text-sm font-medium text-gray-900;
}

.filter-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

.filter-group {
  @apply space-y-2;
}

.filter-label {
  @apply block text-sm font-medium text-gray-700;
}

.date-inputs {
  @apply flex items-center space-x-2;
}

.date-input {
  @apply border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.date-separator {
  @apply text-sm text-gray-500;
}

.range-inputs {
  @apply flex items-center space-x-2;
}

.range-input {
  @apply border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-24;
}

.range-separator {
  @apply text-sm text-gray-500;
}

.filter-actions {
  @apply flex space-x-2 md:col-span-2 lg:col-span-1;
}

.reset-filters-btn {
  @apply px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500;
}

.apply-filters-btn {
  @apply px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500;
}

.data-summary {
  @apply border-t border-gray-200 pt-6;
}

.summary-stats {
  @apply grid grid-cols-2 lg:grid-cols-4 gap-4;
}

.stat-item {
  @apply flex flex-col space-y-1;
}

.stat-label {
  @apply text-sm font-medium text-gray-500;
}

.stat-value {
  @apply text-lg font-semibold text-gray-900;
}
</style>