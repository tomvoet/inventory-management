<template>
  <div class="orders">
    <div class="page-header">
      <h2>{{ t('orders.title') }}</h2>
      <p>{{ t('orders.description') }}</p>
    </div>

    <DataState
      :loading="loading"
      :refreshing="refreshing"
      :error="error"
      :loaded="loaded"
      @retry="load"
    >
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label stat-dot dot-ok">{{ t('status.delivered') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Delivered').length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label stat-dot dot-accent">{{ t('status.shipped') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Shipped').length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label stat-dot dot-warn">{{ t('status.processing') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Processing').length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label stat-dot dot-crit">{{ t('status.backordered') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Backordered').length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('orders.submittedOrders.title') }} ({{ restockingOrders.length }})</h3>
        </div>
        <div v-if="restockingError" class="error" role="alert">{{ restockingError }}</div>
        <div v-else-if="restockingOrders.length === 0" class="empty">{{ t('orders.submittedOrders.empty') }}</div>
        <div v-else class="table-container">
          <table class="orders-table">
            <thead>
              <tr>
                <th class="col-order-number">{{ t('orders.submittedOrders.orderNumber') }}</th>
                <th class="col-items">{{ t('orders.submittedOrders.items') }}</th>
                <th class="col-date">{{ t('orders.submittedOrders.submittedDate') }}</th>
                <th class="col-date">{{ t('orders.submittedOrders.leadTime') }}</th>
                <th class="col-date">{{ t('orders.submittedOrders.expectedDelivery') }}</th>
                <th class="col-value num">{{ t('orders.submittedOrders.total') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in restockingOrders" :key="order.id">
                <td class="col-order-number"><span class="num order-no">{{ order.order_number }}</span></td>
                <td class="col-items">
                  <details class="items-details">
                    <summary class="items-summary">
                      {{ t(order.items.length === 1 ? 'orders.itemsCountOne' : 'orders.itemsCount', { count: order.items.length }) }}
                    </summary>
                    <div class="items-dropdown">
                      <div v-for="item in order.items" :key="item.item_sku" class="item-entry">
                        <span class="item-name">{{ translateProductName(item.item_name) }}</span>
                        <span class="item-meta num">{{ t('orders.quantity') }}: {{ item.quantity }} @ {{ formatCurrencyWithDecimals(item.unit_cost, currentCurrency, 2) }}</span>
                      </div>
                    </div>
                  </details>
                </td>
                <td class="col-date"><span class="num">{{ formatDate(order.submitted_date) }}</span></td>
                <td class="col-date"><span class="num">{{ t('orders.submittedOrders.leadTimeDays', { count: order.lead_time_days }) }}</span></td>
                <td class="col-date"><span class="num">{{ formatDate(order.expected_delivery) }}</span></td>
                <td class="col-value num">{{ formatCurrencyWithDecimals(order.total_cost, currentCurrency, 2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('orders.allOrders') }} ({{ orders.length }})</h3>
        </div>
        <div class="table-container">
          <table class="orders-table">
            <thead>
              <tr>
                <th class="col-order-number">{{ t('orders.table.orderNumber') }}</th>
                <th class="col-customer">{{ t('orders.table.customer') }}</th>
                <th class="col-items">{{ t('orders.table.items') }}</th>
                <th class="col-status">{{ t('orders.table.status') }}</th>
                <th class="col-date">{{ t('orders.table.orderDate') }}</th>
                <th class="col-date">{{ t('orders.table.expectedDelivery') }}</th>
                <th class="col-value num">{{ t('orders.table.totalValue') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders" :key="order.id">
                <td class="col-order-number"><span class="num order-no">{{ order.order_number }}</span></td>
                <td class="col-customer">{{ translateCustomerName(order.customer) }}</td>
                <td class="col-items">
                  <details class="items-details">
                    <summary class="items-summary">
                      {{ t(order.items.length === 1 ? 'orders.itemsCountOne' : 'orders.itemsCount', { count: order.items.length }) }}
                    </summary>
                    <div class="items-dropdown">
                      <div v-for="item in order.items" :key="item.sku" class="item-entry">
                        <span class="item-name">{{ translateProductName(item.name) }}</span>
                        <span class="item-meta num">{{ t('orders.quantity') }}: {{ item.quantity }} @ {{ formatCurrencyWithDecimals(item.unit_price, currentCurrency, 2) }}</span>
                      </div>
                    </div>
                  </details>
                </td>
                <td class="col-status">
                  <span :class="['badge', getOrderStatusClass(order.status)]">
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </span>
                </td>
                <td class="col-date"><span class="num">{{ formatDate(order.order_date) }}</span></td>
                <td class="col-date"><span class="num">{{ formatDate(order.expected_delivery) }}</span></td>
                <td class="col-value num">{{ formatCurrencyWithDecimals(order.total_value, currentCurrency, 2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </DataState>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'
import DataState from '../components/DataState.vue'
import { useDataLoader } from '../composables/useDataLoader'

export default {
  name: 'Orders',
  components: { DataState },
  setup() {
    const { t, currentCurrency, translateProductName, translateCustomerName } = useI18n()

    const orders = ref([])
    const restockingOrders = ref([])
    const restockingError = ref(null)

    // Use shared filters
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      getCurrentFilters
    } = useFilters()

    const { loading, refreshing, error, loaded, load: loadOrders, loadDebounced } = useDataLoader(
      () => api.getOrders(getCurrentFilters()),
      (fetchedOrders) => {
        // Sort orders by order_date (earliest first)
        orders.value = fetchedOrders.sort((a, b) => {
          const dateA = new Date(a.order_date)
          const dateB = new Date(b.order_date)
          return dateA - dateB
        })
      }
    )

    // Separate from loadOrders so a failure here never blanks the main list
    const loadRestockingOrders = async () => {
      try {
        restockingError.value = null
        restockingOrders.value = await api.getRestockingOrders()
      } catch (err) {
        restockingError.value = t('orders.submittedOrders.loadFailed')
        console.error('Restocking orders load error:', err)
      }
    }

    // Watch for filter changes and reload data
    watch([selectedPeriod, selectedLocation, selectedCategory, selectedStatus], loadDebounced)

    const getOrdersByStatus = (status) => {
      return orders.value.filter(order => order.status === status)
    }

    const getOrderStatusClass = (status) => {
      const statusMap = {
        'Delivered': 'success',
        'Shipped': 'info',
        'Processing': 'warning',
        'Backordered': 'danger'
      }
      return statusMap[status] || 'info'
    }

    const formatDate = (dateString) => {
      const { currentLocale } = useI18n()
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return new Date(dateString).toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(() => {
      loadOrders()
      loadRestockingOrders()
    })

    return {
      t,
      loading,
      refreshing,
      error,
      loaded,
      load: loadOrders,
      orders,
      restockingOrders,
      restockingError,
      currentCurrency,
      formatCurrency,
      formatCurrencyWithDecimals,
      getOrdersByStatus,
      getOrderStatusClass,
      formatDate,
      translateProductName,
      translateCustomerName
    }
  }
}
</script>

<style scoped>
/* Fixed layout stops columns shifting; min-width makes narrow screens scroll instead of squash */
.orders-table {
  table-layout: fixed;
  min-width: 860px;
}

.col-order-number { width: 130px; }
.col-customer { width: 180px; }
.col-items { width: 190px; }
.col-status { width: 130px; }
.col-date { width: 130px; }
.col-value { width: 120px; }

.stat-dot {
  display: flex;
  align-items: center;
  gap: 7px;
}

.stat-dot::before {
  content: '';
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--seg-gray);
}

.dot-ok::before { background: var(--dot-ok); }
.dot-accent::before { background: var(--accent); }
.dot-warn::before { background: var(--dot-warn); }
.dot-crit::before { background: var(--dot-crit); }

.order-no {
  color: var(--ink);
}

.empty {
  padding: 32px 18px;
  text-align: center;
  color: var(--muted);
}

/* Expands inline: an absolute popover would be clipped by the scrolling table container */
.items-summary {
  cursor: pointer;
  color: var(--text);
  list-style: none;
  user-select: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.items-summary::-webkit-details-marker {
  display: none;
}

.items-summary::before {
  content: '';
  width: 5px;
  height: 5px;
  border-right: 1.5px solid var(--muted);
  border-bottom: 1.5px solid var(--muted);
  transform: rotate(-45deg);
  transition: transform 0.15s;
}

.items-details[open] .items-summary::before {
  transform: rotate(45deg);
}

.items-summary:hover {
  color: var(--ink);
}

.items-summary:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 4px;
}

.items-dropdown {
  padding: 4px 0 10px;
}

.item-entry {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px 0;
  border-bottom: 1px solid var(--line);
  white-space: normal;
}

.item-entry:last-child {
  border-bottom: 0;
}

.item-name {
  font-size: 13px;
  color: var(--ink);
}

.item-meta {
  font-size: 12px;
  color: var(--muted);
}

td:has(.items-details[open]) {
  vertical-align: top;
  padding-top: 14px;
}
</style>
