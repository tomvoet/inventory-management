<template>
  <div class="spending">
    <div class="page-header">
      <h2>{{ t('finance.title') }}</h2>
      <p>{{ t('finance.description') }}</p>
    </div>

    <DataState
      :loading="loading"
      :refreshing="refreshing"
      :error="error"
      :loaded="loaded"
      @retry="load"
    >
      <!-- Revenue & Financial KPIs -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-label">{{ t('finance.totalRevenue') }}</span>
          <span class="stat-value">{{ formatCurrency(revenueMetrics.totalRevenue) }}</span>
          <span class="stat-meta">{{ t('finance.fromOrders', { count: revenueMetrics.orderCount }) }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">{{ t('finance.totalCosts') }}</span>
          <span class="stat-value">{{ formatCurrency(totalCosts) }}</span>
          <span class="stat-meta">{{ t('finance.costBreakdown') }}</span>
        </div>
        <div class="stat-card" :class="netProfit >= 0 ? 'success' : 'danger'">
          <span class="stat-label">{{ t('finance.netProfit') }}</span>
          <span class="stat-value">{{ formatCurrency(netProfit) }}</span>
          <span class="stat-meta"><span class="num">{{ profitMargin }}%</span> {{ t('finance.margin') }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">{{ t('finance.avgOrderValue') }}</span>
          <span class="stat-value">{{ formatCurrency(revenueMetrics.avgOrderValue) }}</span>
          <span class="stat-meta">{{ t('finance.perOrderRevenue') }}</span>
        </div>
      </div>

      <!-- Monthly Revenue vs Cost Chart -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('finance.revenueVsCosts.title') }}</h3>
          <div class="chart-legend">
            <span class="legend-item"><span class="legend-swatch revenue-color"></span>{{ t('finance.revenueVsCosts.revenue') }}</span>
            <span class="legend-item"><span class="legend-swatch cost-color"></span>{{ t('finance.revenueVsCosts.costs') }}</span>
          </div>
        </div>
        <div class="chart-scroll">
          <div class="bar-chart">
            <div class="y-axis num">
              <span>{{ formatCompact(maxRevenueValue * 1000) }}</span>
              <span>{{ formatCompact(maxRevenueValue * 750) }}</span>
              <span>{{ formatCompact(maxRevenueValue * 500) }}</span>
              <span>{{ formatCompact(maxRevenueValue * 250) }}</span>
              <span>{{ formatCompact(0) }}</span>
            </div>
            <div class="plot">
              <div class="gridlines" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
              <div class="cols">
                <div v-for="month in monthlyRevenue" :key="month.month" class="col">
                  <div class="revenue-bars">
                    <div class="revenue-bar" :style="{ height: getRevenueBarHeight(month.revenue) + '%' }" :title="`Revenue: ${formatCurrency(month.revenue)}`"></div>
                    <div class="cost-bar" :style="{ height: getRevenueBarHeight(month.costs) + '%' }" :title="`Costs: ${formatCurrency(month.costs)}`"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="x-axis num">
              <span v-for="month in monthlyRevenue" :key="month.month">{{ translateMonth(month.month) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Monthly Cost Flow Chart -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('finance.monthlyCostFlow.title') }}</h3>
          <div class="chart-legend">
            <span class="legend-item"><span class="legend-swatch procurement"></span>{{ t('finance.monthlyCostFlow.procurement') }}</span>
            <span class="legend-item"><span class="legend-swatch operational"></span>{{ t('finance.monthlyCostFlow.operational') }}</span>
            <span class="legend-item"><span class="legend-swatch labor"></span>{{ t('finance.monthlyCostFlow.labor') }}</span>
            <span class="legend-item"><span class="legend-swatch overhead"></span>{{ t('finance.monthlyCostFlow.overhead') }}</span>
          </div>
        </div>
        <div class="chart-scroll">
          <div class="bar-chart">
            <div class="y-axis num">
              <span>{{ formatCompact(25000) }}</span>
              <span>{{ formatCompact(20000) }}</span>
              <span>{{ formatCompact(15000) }}</span>
              <span>{{ formatCompact(10000) }}</span>
              <span>{{ formatCompact(5000) }}</span>
              <span>{{ formatCompact(0) }}</span>
            </div>
            <div class="plot">
              <div class="gridlines" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div>
              <div class="cols">
                <div v-for="month in monthlySpending" :key="month.month" class="col">
                  <button type="button" class="stacked-bar" :aria-label="`${month.month} - ${t('common.viewDetails')}`" @click="showCostDetail(month)">
                    <div class="bar-segment procurement" :style="{ height: getBarHeight(month.procurement) + '%' }" :title="`Procurement: ${formatCurrency(month.procurement)}`"></div>
                    <div class="bar-segment operational" :style="{ height: getBarHeight(month.operational) + '%' }" :title="`Operational: ${formatCurrency(month.operational)}`"></div>
                    <div class="bar-segment labor" :style="{ height: getBarHeight(month.labor) + '%' }" :title="`Labor: ${formatCurrency(month.labor)}`"></div>
                    <div class="bar-segment overhead" :style="{ height: getBarHeight(month.overhead) + '%' }" :title="`Overhead: ${formatCurrency(month.overhead)}`"></div>
                  </button>
                </div>
              </div>
            </div>
            <div class="x-axis num">
              <span v-for="month in monthlySpending" :key="month.month">{{ translateMonth(month.month) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="two-column-grid">
        <!-- Category Spending Breakdown -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ t('finance.categorySpending.title') }}</h3>
          </div>
          <div class="category-list">
            <div v-for="category in categorySpending" :key="category.category" class="category-item">
              <div class="category-info">
                <span class="category-name">{{ translateCategory(category.category) }}</span>
                <span class="num category-amount">{{ formatCurrency(category.amount) }}</span>
              </div>
              <div class="category-bar-container">
                <div class="category-bar" :style="{ width: category.percentage + '%' }"></div>
              </div>
              <div class="category-meta">
                <span><span class="num">{{ category.percentage }}%</span> {{ t('finance.categorySpending.ofTotal') }}</span>
                <span class="num" :class="{ 'delta-pos': category.change > 0, 'delta-neg': category.change < 0 }">
                  {{ category.change > 0 ? '+' : '' }}{{ category.change }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Transactions -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ t('finance.transactions.title') }}</h3>
          </div>
          <div class="table-container transactions-scroll">
            <table>
              <thead>
                <tr>
                  <th>{{ t('finance.transactions.id') }}</th>
                  <th>{{ t('finance.transactions.description') }}</th>
                  <th>{{ t('finance.transactions.vendor') }}</th>
                  <th>{{ t('finance.transactions.date') }}</th>
                  <th class="num">{{ t('finance.transactions.amount') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="transaction in recentTransactions"
                  :key="transaction.id"
                  class="clickable-row"
                  tabindex="0"
                  @click="handleTransactionClick(transaction)"
                  @keydown.enter.self.prevent="handleTransactionClick(transaction)"
                  @keydown.space.self.prevent="handleTransactionClick(transaction)"
                >
                  <td class="num cell-code">{{ transaction.id.toString().padStart(3, '0') }}</td>
                  <td>{{ transaction.description }}</td>
                  <td class="muted">{{ transaction.vendor }}</td>
                  <td class="num cell-code">{{ formatDateShort(transaction.date) }}</td>
                  <td class="num">{{ formatCurrency(transaction.amount) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DataState>

    <CostDetailModal
      :is-open="showCostModal"
      :cost-data="selectedCostData"
      @close="showCostModal = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrency as formatCurrencyUtil, formatCompactCurrency } from '../utils/currency'
import CostDetailModal from '../components/CostDetailModal.vue'
import DataState from '../components/DataState.vue'
import { useDataLoader } from '../composables/useDataLoader'

export default {
  name: 'Spending',
  components: {
    CostDetailModal,
    DataState
  },
  setup() {
    const { t, currentCurrency } = useI18n()
    const allMonthlySpending = ref([])
    const allCategorySpending = ref([])
    const allTransactions = ref([])
    const summaryData = ref({})
    const allOrders = ref([])

    // Modal state
    const showCostModal = ref(false)
    const selectedCostData = ref(null)

    // Use shared filters
    const { selectedPeriod, getCurrentFilters } = useFilters()

    // Monthly spending chart always shows all months (not filtered)
    const monthlySpending = computed(() => {
      return allMonthlySpending.value
    })

    // Filtered monthly spending for summary calculations only
    const filteredMonthlySpending = computed(() => {
      if (selectedPeriod.value === 'all') {
        return allMonthlySpending.value
      }

      // Extract month name from YYYY-MM format
      const monthMap = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
      }
      const selectedMonth = monthMap[selectedPeriod.value.split('-')[1]]
      return allMonthlySpending.value.filter(m => m.month === selectedMonth)
    })

    const categorySpending = computed(() => {
      return allCategorySpending.value
    })

    const recentTransactions = computed(() => {
      if (selectedPeriod.value === 'all') {
        return allTransactions.value
      }
      // Filter transactions by selected month
      return allTransactions.value.filter(t => {
        const transactionMonth = new Date(t.date).toISOString().slice(0, 7)
        return transactionMonth === selectedPeriod.value
      })
    })

    const summary = computed(() => {
      // Recalculate summary based on filteredMonthlySpending (not the chart data)
      if (filteredMonthlySpending.value.length === 0) {
        return summaryData.value
      }

      const totals = filteredMonthlySpending.value.reduce((acc, month) => ({
        procurement: acc.procurement + month.procurement,
        operational: acc.operational + month.operational,
        labor: acc.labor + month.labor,
        overhead: acc.overhead + month.overhead
      }), { procurement: 0, operational: 0, labor: 0, overhead: 0 })

      return {
        total_procurement_cost: totals.procurement,
        total_operational_cost: totals.operational,
        total_labor_cost: totals.labor,
        total_overhead: totals.overhead,
        procurement_change: summaryData.value.procurement_change || 0,
        operational_change: summaryData.value.operational_change || 0,
        labor_change: summaryData.value.labor_change || 0,
        overhead_change: summaryData.value.overhead_change || 0
      }
    })

    // Filtered orders based on selected period
    const filteredOrders = computed(() => {
      if (selectedPeriod.value === 'all') {
        return allOrders.value
      }

      // Filter orders by selected month
      return allOrders.value.filter(order => {
        const orderMonth = new Date(order.order_date).toISOString().slice(0, 7)
        return orderMonth === selectedPeriod.value
      })
    })

    // Revenue metrics from filtered orders
    const revenueMetrics = computed(() => {
      const totalRevenue = filteredOrders.value.reduce((sum, order) => sum + (order.total_value || 0), 0)
      const orderCount = filteredOrders.value.length
      const avgOrderValue = orderCount > 0 ? totalRevenue / orderCount : 0

      return {
        totalRevenue,
        orderCount,
        avgOrderValue,
        revenueGrowth: 15.3 // Placeholder - could calculate from historical data
      }
    })

    // Total costs from summary
    const totalCosts = computed(() => {
      return summary.value.total_procurement_cost +
             summary.value.total_operational_cost +
             summary.value.total_labor_cost +
             summary.value.total_overhead
    })

    // Net profit
    const netProfit = computed(() => {
      return revenueMetrics.value.totalRevenue - totalCosts.value
    })

    // Profit margin percentage
    const profitMargin = computed(() => {
      if (revenueMetrics.value.totalRevenue === 0) return 0
      return ((netProfit.value / revenueMetrics.value.totalRevenue) * 100).toFixed(1)
    })

    // Monthly revenue data for chart
    const monthlyRevenue = computed(() => {
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

      // Initialize all months
      const revenueByMonth = monthNames.map(month => ({
        month,
        revenue: 0,
        costs: 0
      }))

      // Calculate revenue from orders
      allOrders.value.forEach(order => {
        const orderDate = new Date(order.order_date)
        const monthIndex = orderDate.getMonth()
        if (monthIndex >= 0 && monthIndex < 12) {
          revenueByMonth[monthIndex].revenue += order.total_value || 0
        }
      })

      // Add costs from spending data
      allMonthlySpending.value.forEach(spending => {
        const monthIndex = monthNames.indexOf(spending.month)
        if (monthIndex >= 0) {
          revenueByMonth[monthIndex].costs = spending.procurement + spending.operational + spending.labor + spending.overhead
        }
      })

      return revenueByMonth
    })

    // Max value for chart scaling
    const maxRevenueValue = computed(() => {
      const maxRevenue = Math.max(...monthlyRevenue.value.map(m => m.revenue))
      const maxCost = Math.max(...monthlyRevenue.value.map(m => m.costs))
      const max = Math.max(maxRevenue, maxCost)
      return Math.ceil(max / 1000) // Return in K
    })

    // Period filtering is client-side, so no refetch on filter change
    const { loading, refreshing, error, loaded, load } = useDataLoader(
      () => Promise.all([
        api.getSpendingSummary(),
        api.getMonthlySpending(),
        api.getCategorySpending(),
        api.getTransactions(),
        api.getOrders()
      ]),
      ([summaryRes, monthlyRes, categoryRes, transactionsRes, ordersRes]) => {
        summaryData.value = summaryRes
        allMonthlySpending.value = monthlyRes
        allCategorySpending.value = categoryRes
        allTransactions.value = transactionsRes
        allOrders.value = ordersRes
      }
    )

    const formatCurrency = (value) => {
      return formatCurrencyUtil(value, currentCurrency.value)
    }

    const formatCompact = (value) => formatCompactCurrency(value, currentCurrency.value)

    const getBarHeight = (value) => {
      const maxValue = 25000
      return (value / maxValue) * 100
    }

    const getRevenueBarHeight = (value) => {
      const maxValue = maxRevenueValue.value * 1000
      return (value / maxValue) * 100
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      })
    }

    const formatDateShort = (dateString) => {
      const date = new Date(dateString)
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      const year = date.getFullYear().toString().slice(-2)
      return `${month}/${day}/${year}`
    }

    const translateMonth = (month) => {
      const monthMap = {
        'Jan': t('months.jan'),
        'Feb': t('months.feb'),
        'Mar': t('months.mar'),
        'Apr': t('months.apr'),
        'May': t('months.may'),
        'Jun': t('months.jun'),
        'Jul': t('months.jul'),
        'Aug': t('months.aug'),
        'Sep': t('months.sep'),
        'Oct': t('months.oct'),
        'Nov': t('months.nov'),
        'Dec': t('months.dec')
      }
      return monthMap[month] || month
    }

    const translateCategory = (category) => {
      // First try spending categories
      const spendingCategoryMap = {
        'Raw Materials': t('spendingCategories.rawMaterials'),
        'Components': t('spendingCategories.components'),
        'Equipment': t('spendingCategories.equipment'),
        'Consumables': t('spendingCategories.consumables')
      }

      // Then try product categories
      const productCategoryMap = {
        'Circuit Boards': t('categories.circuitBoards'),
        'Sensors': t('categories.sensors'),
        'Actuators': t('categories.actuators'),
        'Controllers': t('categories.controllers'),
        'Power Supplies': t('categories.powerSupplies')
      }

      return spendingCategoryMap[category] || productCategoryMap[category] || category
    }

    const handleTransactionClick = (transaction) => {
      alert(`Transaction Details:\n\nID: ${transaction.id}\nDescription: ${transaction.description}\nVendor: ${transaction.vendor}\nDate: ${formatDateShort(transaction.date)}\nAmount: ${formatCurrency(transaction.amount)}`)
    }

    const showCostDetail = (monthData) => {
      selectedCostData.value = monthData
      showCostModal.value = true
    }

    onMounted(load)

    return {
      t,
      loading,
      refreshing,
      error,
      loaded,
      load,
      summary,
      monthlySpending,
      categorySpending,
      recentTransactions,
      revenueMetrics,
      totalCosts,
      netProfit,
      profitMargin,
      monthlyRevenue,
      maxRevenueValue,
      formatCurrency,
      formatCompact,
      getBarHeight,
      getRevenueBarHeight,
      formatDate,
      formatDateShort,
      translateMonth,
      translateCategory,
      handleTransactionClick,
      showCostModal,
      selectedCostData,
      showCostDetail,
      Math
    }
  }
}
</script>

<style scoped>
.stat-meta {
  font-size: 13px;
  color: var(--muted);
}

.delta-pos { color: var(--pos); }
.delta-neg { color: var(--neg); }

.muted { color: var(--muted); }

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 16px;
  font-size: 13px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
}

.legend-swatch {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.procurement { background: var(--accent); }
.operational { background: var(--accent-2); }
.labor { background: var(--seg-gray); }
.overhead { background: color-mix(in srgb, var(--seg-gray) 55%, var(--surface)); }
.revenue-color { background: var(--accent); }
.cost-color { background: var(--seg-gray); }

/* Narrow screens scroll the chart rather than squeezing 12 columns */
.chart-scroll {
  overflow-x: auto;
}

.bar-chart {
  --plot-h: 240px;
  min-width: 480px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  column-gap: 12px;
  padding: 6px 0 0;
}

/* Extra 12px and negative margin center the end labels on the first/last gridline */
.y-axis {
  height: calc(var(--plot-h) + 12px);
  margin: -6px 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 12px;
  line-height: 12px;
  color: var(--muted);
  text-align: right;
}

.plot {
  position: relative;
  height: var(--plot-h);
}

.gridlines {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.gridlines i {
  display: block;
  height: 0;
  border-top: 1px solid var(--line);
}

.gridlines i:last-child {
  border-top-color: var(--line-strong);
}

.cols {
  position: absolute;
  inset: 0;
  display: flex;
  gap: 8px;
}

.col {
  flex: 1;
  min-width: 0;
  display: flex;
  justify-content: center;
  height: 100%;
}

.x-axis {
  grid-column: 2;
  display: flex;
  gap: 8px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--muted);
}

.x-axis span {
  flex: 1;
  text-align: center;
}

.revenue-bars {
  width: 100%;
  max-width: 44px;
  display: flex;
  gap: 2px;
  justify-content: center;
  align-items: flex-end;
  height: 100%;
}

.revenue-bar,
.cost-bar {
  flex: 1;
  border-radius: 2px 2px 0 0;
  min-height: 2px;
}

.revenue-bar { background: var(--accent); }
.cost-bar { background: var(--seg-gray); }

.revenue-bar:hover,
.cost-bar:hover {
  opacity: 0.8;
}

.stacked-bar {
  background: none;
  border: 0;
  font: inherit;
  padding: 0;
  width: 100%;
  max-width: 44px;
  display: flex;
  flex-direction: column-reverse;
  align-items: stretch;
  gap: 1px;
  height: 100%;
  cursor: pointer;
}

.stacked-bar:hover {
  opacity: 0.85;
}

.bar-segment {
  width: 100%;
  display: block;
}

.bar-segment:last-child {
  border-radius: 2px 2px 0 0;
}

.two-column-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
}

.two-column-grid .card {
  margin-bottom: 0;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.category-info,
.category-meta {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}

.category-name,
.category-amount {
  color: var(--ink);
}

.category-bar-container {
  height: 6px;
  background: var(--sunken);
  border-radius: 3px;
  overflow: hidden;
}

.category-bar {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
}

.category-meta {
  font-size: 12.5px;
  color: var(--muted);
}

.transactions-scroll {
  max-height: 400px;
  overflow-y: auto;
}

.transactions-scroll th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--surface);
}

/* Mono IDs and dates stay on one line, left-aligned; description and vendor wrap instead */
.cell-code {
  text-align: left;
  white-space: nowrap;
  color: var(--muted);
}

.clickable-row {
  cursor: pointer;
}

@media (max-width: 900px) {
  .two-column-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
