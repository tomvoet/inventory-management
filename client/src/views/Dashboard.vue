<template>
  <div class="dashboard">
    <div class="page-header header-row">
      <div>
        <h2>{{ t('dashboard.title') }}</h2>
        <p v-if="!loading && !error">
          <span class="num">{{ backlogItems.length }}</span> {{ t('dashboard.blockedOrders') }}
        </p>
      </div>
      <a v-if="!loading && backlogItems.length > 0" href="#shortages" class="review-link">{{ t('dashboard.reviewShortages') }}</a>
    </div>

    <DataState
      :loading="loading"
      :refreshing="refreshing"
      :error="error"
      :loaded="loaded"
      @retry="load"
    >
      <!-- Key Performance Indicators -->
      <div class="stats-grid">
        <div v-for="kpi in kpiCards" :key="kpi.key" class="stat-card">
          <span class="stat-label">{{ kpi.label }}</span>
          <span class="stat-value" :class="{ compact: kpi.value.length > 11 }">{{ kpi.value }}</span>
          <div class="kpi-meta">
            <span class="kpi-target">{{ t('dashboard.kpi.goal') }} <span class="num">{{ kpi.target }}</span></span>
            <span class="num" :class="kpi.favorable ? 'delta-pos' : 'delta-neg'">{{ kpi.delta }}</span>
          </div>
          <div class="meter"><div class="meter-fill" :style="{ width: kpi.fill + '%' }"></div></div>
        </div>
      </div>

      <div class="charts-grid">
        <!-- Order pipeline -->
        <div class="card flush">
          <div class="card-header">
            <h3 class="card-title">{{ t('dashboard.orderHealth.title') }}</h3>
            <span class="header-meta"><span class="num">{{ orderHealthMetrics.totalOrders }}</span> {{ t('dashboard.orderHealth.totalOrders') }}</span>
          </div>
          <div class="card-body pipeline">
            <div class="stacked-bar" role="img" :aria-label="pipelineAriaLabel">
              <div
                v-for="seg in pipeline"
                :key="seg.key"
                class="stacked-seg"
                :style="{ width: seg.share + '%', background: seg.color }"
              ></div>
            </div>
            <div class="legend">
              <div v-for="seg in pipeline" :key="seg.key" class="legend-row">
                <span class="legend-swatch" :style="{ background: seg.color }"></span>
                <span>{{ seg.label }}</span>
                <span class="num legend-count">{{ seg.count }}</span>
                <span class="num legend-share">{{ Math.round(seg.share) }}%</span>
              </div>
            </div>
            <div class="health-metrics">
              <div class="health-metric">
                <span class="health-metric-label">{{ t('dashboard.orderHealth.revenue') }}</span>
                <span class="num health-metric-value">{{ formatCurrency(orderHealthMetrics.totalValue, selectedCurrency) }}</span>
              </div>
              <div class="health-metric">
                <span class="health-metric-label">{{ t('dashboard.orderHealth.avgOrderValue') }}</span>
                <span class="num health-metric-value">{{ formatCurrency(orderHealthMetrics.avgOrderValue, selectedCurrency) }}</span>
              </div>
              <div class="health-metric">
                <span class="health-metric-label">{{ t('dashboard.orderHealth.onTimeRate') }}</span>
                <span
                  class="num health-metric-value"
                  :class="{ 'metric-good': orderHealthMetrics.onTimeRate >= 90, 'metric-bad': orderHealthMetrics.onTimeRate < 75 }"
                >{{ orderHealthMetrics.onTimeRate.toFixed(1) }}%</span>
              </div>
              <div class="health-metric">
                <span class="health-metric-label">{{ t('dashboard.orderHealth.avgFulfillmentDays') }}</span>
                <span class="num health-metric-value">{{ orderHealthMetrics.avgFulfillmentDays.toFixed(1) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Inventory by Category -->
        <div class="card flush">
          <div class="card-header">
            <h3 class="card-title">{{ t('dashboard.inventoryValue.title') }}</h3>
            <span class="header-meta"><span class="num">{{ formatCurrency(totalCategoryValue, selectedCurrency) }}</span> {{ t('dashboard.stockOnHand') }}</span>
          </div>
          <div v-if="sortedCategories.length > 0" class="card-body categories">
            <div v-for="cat in sortedCategories" :key="cat.name" class="cat-row">
              <span class="cat-label">{{ translateCategory(cat.name) }}</span>
              <div class="cat-track">
                <div class="cat-fill" :style="{ width: (cat.value / maxCategoryValue * 100) + '%' }"></div>
              </div>
              <span class="num cat-value">{{ formatCurrency(cat.value, selectedCurrency) }}</span>
            </div>
          </div>
          <div v-else class="no-data">{{ t('dashboard.inventoryShortages.noData') }}</div>
        </div>

        <!-- Inventory Shortages -->
        <div id="shortages" class="card flush full-width">
          <div class="card-header">
            <h3 class="card-title">{{ t('dashboard.inventoryShortages.title') }} <span class="num count-muted">{{ backlogItems.length }}</span></h3>
            <span class="header-meta">{{ t('dashboard.inventoryShortages.subtitle') }}</span>
          </div>
          <div v-if="backlogItems.length === 0" class="no-backlog">
            <p class="no-backlog-text">{{ t('dashboard.inventoryShortages.noShortages') }}</p>
          </div>
          <div v-else class="table-container">
            <table class="shortages-table">
              <thead>
                <tr>
                  <th>{{ t('dashboard.inventoryShortages.orderId') }}</th>
                  <th>{{ t('dashboard.inventoryShortages.itemName') }}</th>
                  <th>{{ t('dashboard.inventoryShortages.coverage') }}</th>
                  <th class="num">{{ t('dashboard.inventoryShortages.shortage') }}</th>
                  <th class="num">{{ t('dashboard.inventoryShortages.daysDelayed') }}</th>
                  <th>{{ t('dashboard.inventoryShortages.priority') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in backlogItems"
                  :key="item.id"
                  class="clickable-row"
                  tabindex="0"
                  @click="showBacklogDetail(item)"
                  @keydown.enter.self.prevent="showBacklogDetail(item)"
                  @keydown.space.self.prevent="showBacklogDetail(item)"
                >
                  <td class="num order-id">{{ item.order_id }}</td>
                  <td>
                    <div class="item-stack">
                      <span class="item-name">{{ translateProductName(item.item_name) }}</span>
                      <span class="num item-sku">{{ item.item_sku }}</span>
                    </div>
                  </td>
                  <td>
                    <div class="coverage">
                      <div class="coverage-track">
                        <div class="coverage-fill" :style="{ width: getCoveragePercent(item) + '%' }"></div>
                      </div>
                      <span class="num coverage-text">{{ item.quantity_available.toLocaleString() }} / {{ item.quantity_needed.toLocaleString() }}</span>
                    </div>
                  </td>
                  <td class="num short">&minus;{{ Math.abs(item.quantity_needed - item.quantity_available).toLocaleString() }}</td>
                  <td class="num strong">{{ t(item.days_delayed === 1 ? 'dashboard.inventoryShortages.dayCount' : 'dashboard.inventoryShortages.daysCount', { count: item.days_delayed }) }}</td>
                  <td>
                    <span :class="['badge', item.priority]">
                      {{ translatePriority(item.priority) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Top Products Table -->
        <div class="card flush full-width">
          <div class="card-header">
            <h3 class="card-title">{{ t('dashboard.topProducts.title') }}</h3>
          </div>
          <div class="table-container">
            <table class="products-table">
              <thead>
                <tr>
                  <th>{{ t('dashboard.topProducts.product') }}</th>
                  <th>{{ t('dashboard.topProducts.sku') }}</th>
                  <th>{{ t('dashboard.topProducts.category') }}</th>
                  <th class="num">{{ t('dashboard.topProducts.unitsOrdered') }}</th>
                  <th class="num">{{ t('dashboard.topProducts.revenue') }}</th>
                  <th>{{ t('dashboard.topProducts.firstOrder') }}</th>
                  <th>{{ t('dashboard.topProducts.stockStatus') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in topProducts"
                  :key="item.sku"
                  class="clickable-row"
                  tabindex="0"
                  @click="showProductDetail(item)"
                  @keydown.enter.self.prevent="showProductDetail(item)"
                  @keydown.space.self.prevent="showProductDetail(item)"
                >
                  <td class="item-name">{{ translateProductName(item.name) }}</td>
                  <td class="num item-sku">{{ item.sku }}</td>
                  <td>{{ translateCategory(item.category) }}</td>
                  <td class="num">{{ item.unitsOrdered.toLocaleString() }}</td>
                  <td class="num strong">{{ formatCurrency(item.revenue, selectedCurrency) }}</td>
                  <td>{{ formatDate(item.firstOrderDate) }}</td>
                  <td>
                    <span :class="['badge', getStockBadge(item.stockLevel)]">
                      {{ translateStockLevel(item.stockLevel) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DataState>

    <ProductDetailModal
      :is-open="showProductModal"
      :product="selectedProduct"
      @close="showProductModal = false"
    />

    <BacklogDetailModal
      :is-open="showBacklogModal"
      :backlog-item="selectedBacklogItem"
      @close="showBacklogModal = false"
    />

  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCompactCurrency } from '../utils/currency'
import DataState from '../components/DataState.vue'
import { useDataLoader } from '../composables/useDataLoader'
import ProductDetailModal from '../components/ProductDetailModal.vue'
import BacklogDetailModal from '../components/BacklogDetailModal.vue'

export default {
  name: 'Dashboard',
  components: {
    DataState,
    ProductDetailModal,
    BacklogDetailModal,
  },
  setup() {
    const { t, currentCurrency, translateProductName, translateWarehouse } = useI18n()
    const summary = ref({})
    const allOrders = ref([])
    const inventoryItems = ref([])

    // Modal state
    const showProductModal = ref(false)
    const selectedProduct = ref(null)
    const showBacklogModal = ref(false)
    const selectedBacklogItem = ref(null)

    // Use shared filters
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      getCurrentFilters
    } = useFilters()

    const ordersData = ref({ fulfilled: 187, goal: 200 })
    const fillRate = ref(96.8)

    const revenueGoal = computed(() => {
      // $800K per month, so if looking at all months (12 months), goal is 12 * 800K = 9.6M
      const monthlyGoal = 800000
      if (selectedPeriod.value === 'all') {
        return monthlyGoal * 12 // $9,600,000 for the full year
      }
      return monthlyGoal // $800,000 for a single month
    })

    const revenueGoalDisplay = computed(() => formatCompactCurrency(revenueGoal.value, currentCurrency.value))

    const statusData = computed(() => {
      const counts = { delivered: 0, shipped: 0, processing: 0, backordered: 0 }
      allOrders.value.forEach(order => {
        const status = order.status.toLowerCase()
        if (counts[status] !== undefined) counts[status]++
      })
      return counts
    })

    const orderHealthMetrics = computed(() => {
      const totalOrders = allOrders.value.length
      const totalValue = allOrders.value.reduce((sum, order) => sum + (order.total_value || 0), 0)
      const avgOrderValue = totalOrders > 0 ? totalValue / totalOrders : 0

      // Calculate on-time delivery rate (delivered orders that arrived on or before expected date)
      const deliveredOrders = allOrders.value.filter(o => o.status.toLowerCase() === 'delivered')
      const onTimeDeliveries = deliveredOrders.filter(o => {
        if (o.actual_delivery && o.expected_delivery) {
          return new Date(o.actual_delivery) <= new Date(o.expected_delivery)
        }
        return false
      }).length
      const onTimeRate = deliveredOrders.length > 0 ? (onTimeDeliveries / deliveredOrders.length) * 100 : 0

      // Calculate average fulfillment speed (days from order to delivery for delivered orders)
      let totalDays = 0
      let countWithDates = 0
      deliveredOrders.forEach(o => {
        if (o.order_date && o.actual_delivery) {
          const orderDate = new Date(o.order_date)
          const deliveryDate = new Date(o.actual_delivery)
          const days = Math.round((deliveryDate - orderDate) / (1000 * 60 * 60 * 24))
          totalDays += days
          countWithDates++
        }
      })
      const avgFulfillmentDays = countWithDates > 0 ? totalDays / countWithDates : 0

      return {
        totalOrders,
        totalValue,
        avgOrderValue,
        onTimeRate,
        avgFulfillmentDays
      }
    })

    const categoryData = computed(() => {
      // Group inventory by category and calculate values
      // Filter inventory items to only include those with orders in the selected period
      const categoryMap = {}

      // Use a single neutral slate/gray color for all categories
      const singleColor = 'var(--btn-secondary)' // Neutral slate; white bar labels need a fill that stays dark in dark mode

      // Get SKUs from orders in the filtered time period
      const orderedSkus = new Set()
      allOrders.value.forEach(order => {
        if (order.items) {
          order.items.forEach(item => {
            orderedSkus.add(item.sku)
          })
        }
      })

      // Only include inventory items that have orders in the selected period
      // If no period is selected (all), include all inventory items
      const itemsToInclude = selectedPeriod.value === 'all'
        ? inventoryItems.value
        : inventoryItems.value.filter(item => orderedSkus.has(item.sku))

      itemsToInclude.forEach(item => {
        const cat = item.category.toLowerCase()
        if (!categoryMap[cat]) {
          categoryMap[cat] = {
            name: item.category,
            value: 0,
            color: singleColor,
            category: cat,
            count: 0
          }
        }
        categoryMap[cat].value += item.quantity_on_hand * item.unit_cost
        categoryMap[cat].count += 1
      })

      return Object.values(categoryMap)
    })

    const maxCategoryValue = computed(() => {
      if (categoryData.value.length === 0) return 1
      return Math.max(...categoryData.value.map(c => c.value))
    })

    const orderTrendData = computed(() => {
      // Group orders by month from the actual data
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

      // Initialize all months with 0 orders
      const monthMap = {}
      monthNames.forEach(month => {
        monthMap[month] = { month, orders: 0 }
      })

      // Count orders for each month
      if (Array.isArray(allOrders.value)) {
        allOrders.value.forEach(order => {
          if (order && order.order_date) {
            const date = new Date(order.order_date)
            const monthIndex = date.getMonth()
            // Check if monthIndex is valid (0-11)
            if (!isNaN(monthIndex) && monthIndex >= 0 && monthIndex <= 11) {
              const monthName = monthNames[monthIndex]
              monthMap[monthName].orders++
            }
          }
        })
      }

      // Return all months in order
      return monthNames.map(month => monthMap[month])
    })

    const maxOrderCount = computed(() => {
      if (orderTrendData.value.length === 0) return 10
      const max = Math.max(...orderTrendData.value.map(d => d.orders))
      // Round up to nearest 10 for cleaner axis, minimum 10
      return Math.max(10, Math.ceil(max / 10) * 10)
    })

    const topProducts = computed(() => {
      // Calculate top products from filtered order data
      const productMap = {}

      // allOrders is already filtered by API based on: month, warehouse, category, status
      allOrders.value.forEach(order => {
        if (order.items) {
          order.items.forEach(item => {
            const sku = item.sku

            // Find matching inventory item to get full product details
            // Note: inventoryItems is also filtered by API based on: warehouse, category
            const invItem = inventoryItems.value.find(i => i.sku === sku)

            // Skip products that don't match current inventory filters
            // (e.g., if filtering by warehouse A, don't show products from warehouse B)
            if (!invItem && (selectedLocation.value !== 'all' || selectedCategory.value !== 'all')) {
              return // Skip this product as it doesn't match inventory filters
            }

            if (!productMap[sku]) {
              productMap[sku] = {
                name: item.name,
                sku: sku,
                category: invItem?.category || 'Unknown',
                warehouse: invItem?.warehouse || 'Unknown',
                unitsOrdered: 0,
                revenue: 0,
                stockLevel: invItem ? (invItem.quantity_on_hand > invItem.reorder_point ? 'In Stock' : 'Low Stock') : 'Unknown',
                firstOrderDate: order.order_date
              }
            } else {
              // Update to EARLIEST order date (to show January at top when selecting All Months)
              if (order.order_date && (!productMap[sku].firstOrderDate || order.order_date < productMap[sku].firstOrderDate)) {
                productMap[sku].firstOrderDate = order.order_date
              }
            }
            productMap[sku].unitsOrdered += item.quantity
            productMap[sku].revenue += item.quantity * item.unit_price
          })
        }
      })

      // Convert to array, sort by first order date (earliest first = January at top), then by revenue, and take top 12
      return Object.values(productMap)
        .sort((a, b) => {
          // Sort by first order date (earliest first)
          // This ensures products first ordered in January appear before those first ordered in December
          const dateA = new Date(a.firstOrderDate || '9999-12-31')
          const dateB = new Date(b.firstOrderDate || '9999-12-31')
          if (dateA.getTime() !== dateB.getTime()) {
            return dateA.getTime() - dateB.getTime() // Earlier dates come first
          }
          // If dates are equal, sort by revenue (highest first)
          return b.revenue - a.revenue
        })
        .slice(0, 12)
    })

    const allBacklogItems = ref([])

    // Filter backlog based on inventory filters
    const backlogItems = computed(() => {
      if (selectedLocation.value === 'all' && selectedCategory.value === 'all') {
        return allBacklogItems.value
      }

      // Get SKUs of items that match the filters
      const validSkus = new Set(inventoryItems.value.map(item => item.sku))
      return allBacklogItems.value.filter(b => validSkus.has(b.item_sku))
    })

    const { loading, refreshing, error, loaded, load, loadDebounced } = useDataLoader(
      () => {
        const filters = getCurrentFilters()
        return Promise.all([
          api.getDashboardSummary(filters),
          api.getOrders(filters),
          api.getInventory(filters),
          api.getBacklog()
        ])
      },
      ([summaryData, ordersResp, inventoryData, backlogData]) => {
        summary.value = summaryData
        allOrders.value = ordersResp
        inventoryItems.value = inventoryData
        allBacklogItems.value = backlogData
      }
    )

    const calculatePercentage = (value, goal) => {
      return ((value / goal) * 100).toFixed(2)
    }

    // Compute total orders once for efficiency
    const totalOrders = computed(() => {
      return statusData.value.delivered + statusData.value.shipped +
             statusData.value.processing + statusData.value.backordered
    })

    const kpiCards = computed(() => {
      const signed = (n, digits, suffix) => `${n > 0 ? '+' : n < 0 ? '−' : ''}${Math.abs(n).toFixed(digits)}${suffix}`
      const pctOfGoal = (value, goal) => (goal > 0 ? (value / goal) * 100 : 0)
      const fulfilledPct = pctOfGoal(ordersData.value.fulfilled, ordersData.value.goal)
      const revenue = summary.value.total_orders_value || 0
      const revenuePct = pctOfGoal(revenue, revenueGoal.value)
      return [
        {
          key: 'turnover',
          label: t('dashboard.kpi.inventoryTurnover'),
          value: '4.2',
          target: '4.5',
          delta: signed(4.2 / 4.5 * 100 - 100, 1, '%'),
          favorable: false,
          fill: 93.3
        },
        {
          key: 'fulfilled',
          label: t('dashboard.kpi.ordersFulfilled'),
          value: String(ordersData.value.fulfilled),
          target: String(ordersData.value.goal),
          delta: signed(fulfilledPct - 100, 1, '%'),
          favorable: fulfilledPct >= 100,
          fill: Math.min(fulfilledPct, 100)
        },
        {
          key: 'fillRate',
          label: t('dashboard.kpi.orderFillRate'),
          value: `${fillRate.value}%`,
          target: '95%',
          delta: signed(fillRate.value - 95, 1, ' pts'),
          favorable: fillRate.value >= 95,
          fill: Math.min(fillRate.value / 95 * 100, 100)
        },
        {
          key: 'revenue',
          label: t(selectedPeriod.value === 'all' ? 'dashboard.kpi.revenueYTD' : 'dashboard.kpi.revenueMTD'),
          value: formatCurrency(Math.round(revenue), currentCurrency.value),
          target: formatCurrency(revenueGoal.value, currentCurrency.value),
          delta: signed(revenuePct - 100, 1, '%'),
          favorable: revenuePct >= 100,
          fill: Math.min(revenuePct, 100)
        },
        {
          key: 'processing',
          label: t('dashboard.kpi.avgProcessingTime'),
          value: '2.8',
          target: '3.0',
          delta: signed(2.8 - 3.0, 1, ''),
          // Lower is better for processing time
          favorable: 2.8 <= 3.0,
          fill: 93.3
        }
      ]
    })

    const PIPELINE_COLORS = {
      delivered: 'var(--accent)',
      shipped: 'var(--accent-2)',
      processing: 'var(--seg-gray)',
      backordered: 'var(--dot-crit)'
    }

    const pipeline = computed(() => {
      const total = totalOrders.value
      return ['delivered', 'shipped', 'processing', 'backordered'].map(key => ({
        key,
        label: t(`status.${key}`),
        count: statusData.value[key],
        share: total > 0 ? (statusData.value[key] / total) * 100 : 0,
        color: PIPELINE_COLORS[key]
      }))
    })

    const pipelineAriaLabel = computed(() =>
      pipeline.value.map(seg => `${seg.count} ${seg.label}`).join(', ')
    )

    const sortedCategories = computed(() =>
      categoryData.value.slice().sort((a, b) => b.value - a.value)
    )

    const totalCategoryValue = computed(() =>
      categoryData.value.reduce((sum, cat) => sum + cat.value, 0)
    )

    const getCoveragePercent = (item) => {
      if (!item.quantity_needed) return 100
      return Math.min(Math.max(item.quantity_available / item.quantity_needed, 0), 1) * 100
    }

    const getStockBadge = (level) => {
      if (level === 'In Stock') return 'success'
      if (level === 'Low Stock') return 'warning'
      return 'danger'
    }

    const translateCategory = (category) => {
      const categoryMap = {
        'Circuit Boards': t('categories.circuitBoards'),
        'Sensors': t('categories.sensors'),
        'Actuators': t('categories.actuators'),
        'Controllers': t('categories.controllers'),
        'Power Supplies': t('categories.powerSupplies')
      }
      return categoryMap[category] || category
    }

    const translateStockLevel = (stockLevel) => {
      const stockMap = {
        'In Stock': t('status.inStock'),
        'Low Stock': t('status.lowStock')
      }
      return stockMap[stockLevel] || stockLevel
    }

    const translatePriority = (priority) => {
      const priorityMap = {
        'high': t('priority.high'),
        'medium': t('priority.medium'),
        'low': t('priority.low'),
        'High': t('priority.high'),
        'Medium': t('priority.medium'),
        'Low': t('priority.low')
      }
      return priorityMap[priority] || priority
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const { currentLocale } = useI18n()
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      const date = new Date(dateString)
      return date.toLocaleDateString(locale, { month: 'short', day: 'numeric', year: 'numeric' })
    }

    const showProductDetail = (product) => {
      selectedProduct.value = product
      showProductModal.value = true
    }

    const showBacklogDetail = (item) => {
      selectedBacklogItem.value = item
      showBacklogModal.value = true
    }

    // Watch for filter changes and reload data
    watch([selectedPeriod, selectedLocation, selectedCategory, selectedStatus], loadDebounced)

    onMounted(load)

    return {
      t,
      loading,
      refreshing,
      error,
      loaded,
      load,
      formatCompactCurrency,
      summary,
      ordersData,
      fillRate,
      statusData,
      orderHealthMetrics,
      categoryData,
      maxCategoryValue,
      orderTrendData,
      maxOrderCount,
      topProducts,
      backlogItems,
      calculatePercentage,
      kpiCards,
      pipeline,
      pipelineAriaLabel,
      sortedCategories,
      totalCategoryValue,
      getCoveragePercent,
      getStockBadge,
      translateCategory,
      translateStockLevel,
      translatePriority,
      formatDate,
      revenueGoal,
      revenueGoalDisplay,
      showProductModal,
      selectedProduct,
      showProductDetail,
      showBacklogModal,
      selectedBacklogItem,
      showBacklogDetail,
      selectedPeriod,
      selectedCurrency: currentCurrency,
      formatCurrency,
      Math,
      translateProductName,
      translateWarehouse
    }
  }
}
</script>

<style scoped>
.header-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}

.review-link {
  font-size: 13.5px;
  font-weight: 500;
  text-decoration: none;
}

.kpi-meta {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 12.5px;
}

.kpi-target {
  color: var(--muted);
}

.kpi-target .num {
  color: var(--text);
}

/* Yen totals run to 14 characters; scale down with the cell so they never spill into the neighbour */
.stat-card {
  container-type: inline-size;
}

.stat-value.compact {
  font-size: clamp(16px, 11cqw, 21px);
}

.delta-pos {
  color: var(--pos);
}

.delta-neg {
  color: var(--neg);
}

.meter {
  height: 3px;
  margin-top: 4px;
  background: var(--sunken);
  border-radius: 2px;
  overflow: hidden;
}

.meter-fill {
  height: 3px;
  background: var(--ink);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(420px, 100%), 1fr));
  gap: 16px;
  align-items: start;
}

/* min-width: 0 lets wide tables scroll inside their card instead of stretching the grid track */
.charts-grid .card {
  margin-bottom: 0;
  min-width: 0;
}

.full-width {
  grid-column: 1 / -1;
}

.header-meta {
  font-size: 12.5px;
  color: var(--muted);
}

.count-muted {
  font-weight: 400;
  color: var(--muted);
}

.card-body {
  padding: 18px;
}

.pipeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stacked-bar {
  display: flex;
  gap: 2px;
  height: 10px;
  border-radius: 3px;
  overflow: hidden;
}

.stacked-seg {
  min-width: 0;
}

.legend {
  display: flex;
  flex-direction: column;
}

.legend-row {
  display: grid;
  grid-template-columns: 16px 1fr 56px 56px;
  align-items: center;
  height: 32px;
  border-top: 1px solid var(--line);
  font-size: 13.5px;
}

.legend-swatch {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.legend-count {
  text-align: right;
  color: var(--ink);
}

.legend-share {
  text-align: right;
  color: var(--muted);
}

.health-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
}

.health-metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.health-metric-label {
  font-size: 12.5px;
  color: var(--muted);
}

.health-metric-value {
  font-family: 'Geist', ui-sans-serif, system-ui, sans-serif;
  font-size: 17px;
  color: var(--ink);
}

.health-metric-value.metric-good {
  color: var(--pos);
}

.health-metric-value.metric-bad {
  color: var(--neg);
}

.categories {
  display: flex;
  flex-direction: column;
  padding-top: 10px;
}

.cat-row {
  display: grid;
  grid-template-columns: 116px 1fr 100px;
  align-items: center;
  gap: 14px;
  height: 46px;
  font-size: 13.5px;
}

.cat-label {
  color: var(--text);
}

.cat-track {
  height: 8px;
  background: var(--sunken);
  border-radius: 2px;
  overflow: hidden;
}

.cat-fill {
  height: 8px;
  background: var(--accent);
  border-radius: 2px;
}

.cat-value {
  text-align: right;
  color: var(--ink);
}

.no-data,
.no-backlog {
  padding: 24px 18px;
  text-align: center;
  color: var(--muted);
}

.no-backlog-text {
  font-size: 13.5px;
}

.shortages-table {
  min-width: 820px;
}

.products-table {
  min-width: 760px;
}

.clickable-row {
  cursor: pointer;
}

.order-id,
.item-sku {
  font-size: 12.5px;
  color: var(--muted);
}

td.order-id,
td.item-sku {
  text-align: left;
  white-space: nowrap;
}

.item-stack {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.item-name {
  color: var(--ink);
}

.item-stack .item-sku {
  font-size: 12px;
}

.coverage {
  display: flex;
  align-items: center;
  gap: 10px;
}

.coverage-track {
  width: 88px;
  height: 4px;
  background: var(--sunken);
  border-radius: 2px;
  overflow: hidden;
}

.coverage-fill {
  height: 4px;
  background: var(--ink);
}

.coverage-text {
  font-size: 12.5px;
  color: var(--muted);
  white-space: nowrap;
}

td.short {
  color: var(--neg);
}

td.strong {
  color: var(--ink);
  white-space: nowrap;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
</style>
