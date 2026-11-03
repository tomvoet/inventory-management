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
      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.totalRevenue') }}</div>
          <div class="stat-value">{{ formatWhole(totalRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.avgMonthlyRevenue') }}</div>
          <div class="stat-value">{{ formatWhole(avgMonthlyRevenue) }}</div>
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

      <!-- Quarterly Performance -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.quarterly.title') }}</h3>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('reports.quarterly.quarter') }}</th>
                <th class="num">{{ t('reports.quarterly.totalOrders') }}</th>
                <th class="num">{{ t('reports.quarterly.totalRevenue') }}</th>
                <th class="num">{{ t('reports.quarterly.avgOrderValue') }}</th>
                <th>{{ t('reports.quarterly.fulfillmentRate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="q in quarterlyData" :key="q.quarter">
                <td><strong>{{ q.quarter }}</strong></td>
                <td class="num">{{ q.total_orders }}</td>
                <td class="num">{{ formatMoney(q.total_revenue) }}</td>
                <td class="num">{{ formatMoney(q.avg_order_value) }}</td>
                <td>
                  <span :class="getFulfillmentClass(q.fulfillment_rate)">
                    <span class="num">{{ q.fulfillment_rate }}%</span>
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
          <div class="chart-plot">
            <div class="y-axis" aria-hidden="true">
              <span
                v-for="tick in yTicks"
                :key="tick.offset"
                class="y-label num"
                :style="{ bottom: tick.offset + 'px' }"
              >{{ tick.label }}</span>
            </div>
            <div class="bar-chart">
              <div v-for="month in monthlyData" :key="month.month" class="bar-wrapper">
                <div class="bar-container">
                  <div
                    class="bar"
                    :style="{ height: getBarHeight(month.revenue) + 'px' }"
                    :title="formatMoney(month.revenue)"
                  ></div>
                </div>
                <div class="bar-label num">{{ formatMonth(month.month) }}</div>
              </div>
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
          <table>
            <thead>
              <tr>
                <th>{{ t('reports.mom.month') }}</th>
                <th class="num">{{ t('reports.mom.orders') }}</th>
                <th class="num">{{ t('reports.mom.revenue') }}</th>
                <th class="num">{{ t('reports.mom.change') }}</th>
                <th class="num">{{ t('reports.mom.growthRate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in monthRows" :key="row.month">
                <td><strong>{{ formatMonth(row.month) }}</strong></td>
                <td class="num">{{ row.order_count }}</td>
                <td class="num">{{ formatMoney(row.revenue) }}</td>
                <td class="num">
                  <span v-if="row.previousRevenue !== null" :class="getChangeClass(row.revenue, row.previousRevenue)">
                    {{ getChangeValue(row.revenue, row.previousRevenue) }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td class="num">
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
import { formatCurrencyWithDecimals, formatCurrency, formatCompactCurrency } from '../utils/currency'

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

// Gridline ticks at 0-100% of the tallest bar, 50px apart
const yTicks = computed(() =>
  [0, 1, 2, 3, 4].map(i => ({
    offset: i * (MAX_BAR_HEIGHT / 4),
    label: formatCompactCurrency((maxRevenue.value * i) / 4, currentCurrency.value)
  }))
)

const formatMoney = (value) => formatCurrencyWithDecimals(value, currentCurrency.value, 2)

const formatWhole = (value) => formatCurrency(value, currentCurrency.value)

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
/* Bottom padding leaves room for the month labels that hang below the axis */
.chart-container {
  padding: 20px 18px 36px;
  overflow-x: auto;
}

.chart-plot {
  display: flex;
  gap: 8px;
  min-width: 720px;
}

.y-axis {
  position: relative;
  flex: 0 0 48px;
  height: 200px;
}

.y-label {
  position: absolute;
  right: 0;
  transform: translateY(50%);
  font-size: 12px;
  line-height: 1;
  color: var(--muted);
}

/* Hairline gridlines every 50px (quarter of the 200px plot) */
.bar-chart {
  flex: 1;
  display: flex;
  align-items: flex-end;
  height: 200px;
  background-image: repeating-linear-gradient(
    to top,
    var(--line) 0,
    var(--line) 1px,
    transparent 1px,
    transparent 50px
  );
  border-bottom: 1px solid var(--line-strong);
}

.bar-wrapper {
  position: relative;
  flex: 1;
  height: 100%;
  display: flex;
  align-items: flex-end;
}

.bar-container {
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 40%;
  max-width: 28px;
  background: var(--accent);
  border-radius: 2px 2px 0 0;
}

.bar:hover {
  background: var(--accent-2);
}

.bar-label {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  padding-top: 6px;
  text-align: center;
  font-size: 12px;
  color: var(--muted);
  white-space: nowrap;
}

.positive-change {
  color: var(--pos);
}

.negative-change {
  color: var(--neg);
}

.empty-state {
  padding: 32px 18px;
  text-align: center;
  color: var(--muted);
}
</style>

