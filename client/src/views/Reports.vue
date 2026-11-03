<template>
  <div class="reports">
    <div class="page-header">
      <h2>{{ t('reports.title') }}</h2>
      <p>{{ t('reports.description') }}</p>
    </div>

    <DataState
      :loading="loading"
      :refreshing="refreshing"
      :error="error"
      :loaded="loaded"
      @retry="load"
    >
      <div v-if="isEmpty" class="card empty-state">{{ t('common.noData') }}</div>
      <template v-else>
      <!-- Quarterly Performance -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.quarterly.title') }}</h3>
        </div>
        <div class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>{{ t('reports.quarterly.quarter') }}</th>
                <th>{{ t('reports.quarterly.totalOrders') }}</th>
                <th>{{ t('reports.quarterly.totalRevenue') }}</th>
                <th>{{ t('reports.quarterly.avgOrderValue') }}</th>
                <th>{{ t('reports.quarterly.fulfillmentRate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="q in quarterlyData" :key="q.quarter">
                <td><strong>{{ q.quarter }}</strong></td>
                <td>{{ q.total_orders }}</td>
                <td>{{ formatMoney(q.total_revenue) }}</td>
                <td>{{ formatMoney(q.avg_order_value) }}</td>
                <td>
                  <span :class="getFulfillmentClass(q.fulfillment_rate)">
                    {{ q.fulfillment_rate }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Monthly Trends Chart -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.trend.title') }}</h3>
        </div>
        <div class="chart-container">
          <div class="bar-chart">
            <div v-for="month in monthlyData" :key="month.month" class="bar-wrapper">
              <div class="bar-container">
                <div
                  class="bar"
                  :style="{ height: getBarHeight(month.revenue) + 'px' }"
                  :title="formatMoney(month.revenue)"
                ></div>
              </div>
              <div class="bar-label">{{ formatMonth(month.month) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Month-over-Month Comparison -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.mom.title') }}</h3>
        </div>
        <div class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>{{ t('reports.mom.month') }}</th>
                <th>{{ t('reports.mom.orders') }}</th>
                <th>{{ t('reports.mom.revenue') }}</th>
                <th>{{ t('reports.mom.change') }}</th>
                <th>{{ t('reports.mom.growthRate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in monthRows" :key="row.month">
                <td><strong>{{ formatMonth(row.month) }}</strong></td>
                <td>{{ row.order_count }}</td>
                <td>{{ formatMoney(row.revenue) }}</td>
                <td>
                  <span v-if="row.previousRevenue !== null" :class="getChangeClass(row.revenue, row.previousRevenue)">
                    {{ getChangeValue(row.revenue, row.previousRevenue) }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td>
                  <span v-if="row.previousRevenue !== null" :class="getChangeClass(row.revenue, row.previousRevenue)">
                    {{ getGrowthRate(row.revenue, row.previousRevenue) }}
                  </span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.totalRevenue') }}</div>
          <div class="stat-value">{{ formatMoney(totalRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.avgMonthlyRevenue') }}</div>
          <div class="stat-value">{{ formatMoney(avgMonthlyRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.totalOrders') }}</div>
          <div class="stat-value">{{ totalOrders }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.bestQuarter') }}</div>
          <div class="stat-value">{{ bestQuarter ?? '-' }}</div>
        </div>
      </div>
      </template>
    </DataState>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../api'
import DataState from '../components/DataState.vue'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { useDataLoader } from '../composables/useDataLoader'
import { formatCurrencyWithDecimals } from '../utils/currency'

const MONTH_KEYS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
const MAX_BAR_HEIGHT = 200

const { t, currentCurrency } = useI18n()
const { selectedPeriod, selectedLocation, selectedCategory, selectedStatus, getCurrentFilters } = useFilters()

const quarterlyData = ref([])
const monthlyData = ref([])

const { loading, refreshing, error, loaded, load, loadDebounced } = useDataLoader(
  async () => {
    const filters = getCurrentFilters()
    const [quarterly, monthly] = await Promise.all([
      api.getQuarterlyReports(filters),
      api.getMonthlyTrends(filters)
    ])
    return { quarterly, monthly }
  },
  ({ quarterly, monthly }) => {
    quarterlyData.value = quarterly
    monthlyData.value = monthly
  }
)

watch([selectedPeriod, selectedLocation, selectedCategory, selectedStatus], loadDebounced)
onMounted(load)

const isEmpty = computed(() => quarterlyData.value.length === 0 && monthlyData.value.length === 0)

const totalRevenue = computed(() => monthlyData.value.reduce((sum, m) => sum + m.revenue, 0))
const avgMonthlyRevenue = computed(() =>
  monthlyData.value.length > 0 ? totalRevenue.value / monthlyData.value.length : 0
)
const totalOrders = computed(() => monthlyData.value.reduce((sum, m) => sum + m.order_count, 0))

// null (rendered as a dash) when no quarter has positive revenue
const bestQuarter = computed(() => {
  let best = null
  for (const q of quarterlyData.value) {
    if (q.total_revenue > 0 && (best === null || q.total_revenue > best.total_revenue)) best = q
  }
  return best ? best.quarter : null
})

const maxRevenue = computed(() => Math.max(0, ...monthlyData.value.map(m => m.revenue)))

const monthRows = computed(() =>
  monthlyData.value.map((m, i) => ({
    ...m,
    previousRevenue: i > 0 ? monthlyData.value[i - 1].revenue : null
  }))
)

const formatMoney = (value) => formatCurrencyWithDecimals(value, currentCurrency.value, 2)

// Falls back to the raw string for anything that isn't YYYY-MM
const formatMonth = (monthStr) => {
  const match = /^(\d{4})-(\d{2})$/.exec(monthStr ?? '')
  const key = match ? MONTH_KEYS[Number(match[2]) - 1] : undefined
  if (!key) return monthStr ?? ''
  return t('reports.monthYear', { month: t(`months.${key}`), year: match[1] })
}

const getBarHeight = (revenue) =>
  maxRevenue.value === 0 ? 0 : (revenue / maxRevenue.value) * MAX_BAR_HEIGHT

const getFulfillmentClass = (rate) => {
  if (rate >= 90) return 'badge success'
  if (rate >= 75) return 'badge warning'
  return 'badge danger'
}

const getChangeValue = (current, previous) => {
  const change = current - previous
  if (change > 0) return '+' + formatMoney(change)
  if (change < 0) return '-' + formatMoney(Math.abs(change))
  return formatMoney(0)
}

const getChangeClass = (current, previous) => {
  const change = current - previous
  if (change > 0) return 'positive-change'
  if (change < 0) return 'negative-change'
  return ''
}

const getGrowthRate = (current, previous) => {
  if (previous === 0) return t('reports.notAvailable')
  const rate = ((current - previous) / previous) * 100
  return (rate > 0 ? '+' : '') + rate.toFixed(1) + '%'
}
</script>

<style scoped>
.reports {
  padding: 0;
}

.card {
  background: var(--surface);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px var(--shadow-md);
}

.card-header {
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.reports-table {
  width: 100%;
  border-collapse: collapse;
}

.reports-table th {
  background: var(--surface-muted);
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-muted);
  border-bottom: 2px solid var(--border);
}

.reports-table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.reports-table tr:hover {
  background: var(--surface-muted);
}

.chart-container {
  padding: 2rem 1rem;
  min-height: 300px;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  gap: 0.5rem;
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
}

.bar-container {
  height: 200px;
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.bar {
  width: 100%;
  background: linear-gradient(to top, var(--accent-bright), var(--accent-light));
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
  cursor: pointer;
}

.bar:hover {
  background: linear-gradient(to top, var(--accent), var(--accent-bright));
}

.bar-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  transform: rotate(-45deg);
  white-space: nowrap;
  margin-top: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.stat-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px var(--shadow-md);
  border-left: 4px solid var(--accent-bright);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text);
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.badge.success {
  background: var(--success-bg);
  color: var(--success-text);
}

.badge.warning {
  background: var(--warning-tint);
  color: var(--warning-text);
}

.badge.danger {
  background: var(--danger-tint);
  color: var(--danger-text);
}

.positive-change {
  color: var(--success-strong);
  font-weight: 600;
}

.negative-change {
  color: var(--danger-strong);
  font-weight: 600;
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
}
</style>
