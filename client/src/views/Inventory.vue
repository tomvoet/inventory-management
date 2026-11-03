<template>
  <div class="inventory">
    <div class="page-header">
      <h2>{{ t('inventory.title') }}</h2>
      <p>
        {{ t('inventory.description') }}
        <span class="meta">
          <span class="num">{{ items.length }}</span> {{ t('inventory.skus') }}
          · <span class="num">{{ formatCurrencyWithDecimals(totalValue, currentCurrency, 0) }}</span> {{ t('inventory.totalValue') }}
          · <span class="num">{{ statusCounts.lowStock }}</span> {{ t('inventory.lowStockItems') }}
        </span>
      </p>
    </div>

    <DataState
      :loading="loading"
      :refreshing="refreshing"
      :error="error"
      :loaded="loaded"
      @retry="load"
    >
    <div class="card flush">
      <div class="toolbar">
        <div class="segmented" role="group" :aria-label="t('inventory.table.status')">
          <button
            v-for="seg in segments"
            :key="seg.key"
            type="button"
            class="seg"
            :class="{ active: statusFilter === seg.key }"
            :aria-pressed="statusFilter === seg.key"
            @click="statusFilter = seg.key"
          >
            <span>{{ seg.label }}</span>
            <span class="num seg-count">{{ seg.count }}</span>
          </button>
        </div>
        <div class="search-box">
          <svg class="search-icon" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true">
            <circle cx="7" cy="7" r="4.5" /><path d="M10.5 10.5 14 14" />
          </svg>
          <input
            v-model="searchQuery"
            type="search"
            :placeholder="t('inventory.searchPlaceholder')"
            :aria-label="t('inventory.searchPlaceholder')"
            class="search-input"
          />
        </div>
      </div>
      <div class="table-container">
        <table class="inventory-table">
          <thead>
            <tr>
              <th>{{ t('inventory.table.itemName') }}</th>
              <th>{{ t('inventory.table.category') }}</th>
              <th class="num">{{ t('inventory.table.quantityOnHand') }}</th>
              <th>{{ t('inventory.table.reorderPoint') }}</th>
              <th class="num">{{ t('inventory.table.unitCost') }}</th>
              <th class="num">{{ t('inventory.table.totalValue') }}</th>
              <th>{{ t('inventory.table.location') }}</th>
              <th>{{ t('inventory.table.status') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in filteredItems"
              :key="item.id"
              class="clickable-row"
              tabindex="0"
              @click="showItemDetail(item)"
              @keydown.enter.self.prevent="showItemDetail(item)"
              @keydown.space.self.prevent="showItemDetail(item)"
            >
              <td>
                <div class="item-cell">
                  <span class="num item-sku">{{ item.sku }}</span>
                  <span class="item-name">{{ translateProductName(item.name) }}</span>
                </div>
              </td>
              <td>{{ translateCategory(item.category) }}</td>
              <td class="num strong">{{ item.quantity_on_hand.toLocaleString() }}</td>
              <td>
                <div class="reorder">
                  <div class="reorder-track">
                    <div
                      class="reorder-fill"
                      :class="{ low: getStockStatusKey(item) === 'lowStock' }"
                      :style="{ width: getReorderFill(item) + '%' }"
                    ></div>
                    <div class="reorder-tick"></div>
                  </div>
                  <span class="num reorder-value">{{ item.reorder_point.toLocaleString() }}</span>
                </div>
              </td>
              <td class="num">{{ formatCurrencyWithDecimals(item.unit_cost, currentCurrency, 2) }}</td>
              <td class="num strong">{{ formatCurrencyWithDecimals(item.quantity_on_hand * item.unit_cost, currentCurrency, 2) }}</td>
              <td class="num bin">{{ translateWarehouse(item.location) }}</td>
              <td>
                <span :class="['badge', getStockStatusClass(item)]">
                  {{ getStockStatus(item) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span>{{ t('inventory.stockLevels') }}: <span class="num">{{ filteredItems.length }}</span> / <span class="num">{{ items.length }}</span></span>
      </div>
    </div>
    </DataState>

    <InventoryDetailModal
      :is-open="showItemModal"
      :inventory-item="selectedItem"
      @close="showItemModal = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import InventoryDetailModal from '../components/InventoryDetailModal.vue'
import DataState from '../components/DataState.vue'
import { useDataLoader } from '../composables/useDataLoader'
import { formatCurrencyWithDecimals } from '../utils/currency'

export default {
  name: 'Inventory',
  components: {
    InventoryDetailModal,
    DataState
  },
  setup() {
    const { t, currentCurrency, translateProductName, translateWarehouse } = useI18n()

    const items = ref([])
    const searchQuery = ref('')
    const statusFilter = ref('all')

    // Modal state
    const showItemModal = ref(false)
    const selectedItem = ref(null)

    // Use shared filters
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    // Stock status order for sorting (using status keys)
    const STATUS_ORDER = { 'lowStock': 0, 'adequate': 1, 'inStock': 2 }

    // Get stock status key (for sorting and translation)
    const getStockStatusKey = (item) => {
      if (item.quantity_on_hand <= item.reorder_point) {
        return 'lowStock'
      } else if (item.quantity_on_hand <= item.reorder_point * 1.5) {
        return 'adequate'
      } else {
        return 'inStock'
      }
    }

    const searchedItems = computed(() => {
      const query = searchQuery.value.toLowerCase().trim()
      if (!query) return items.value
      return items.value.filter(item => item.name.toLowerCase().includes(query))
    })

    // Counts follow the search box but not the status segment, so each segment shows what it would reveal
    const statusCounts = computed(() => {
      const counts = { all: searchedItems.value.length, lowStock: 0, adequate: 0, inStock: 0 }
      searchedItems.value.forEach(item => { counts[getStockStatusKey(item)]++ })
      return counts
    })

    const segments = computed(() => [
      { key: 'all', label: t('filters.all'), count: statusCounts.value.all },
      { key: 'lowStock', label: t('status.lowStock'), count: statusCounts.value.lowStock },
      { key: 'adequate', label: t('status.adequate'), count: statusCounts.value.adequate },
      { key: 'inStock', label: t('status.inStock'), count: statusCounts.value.inStock }
    ])

    const totalValue = computed(() =>
      items.value.reduce((sum, item) => sum + item.quantity_on_hand * item.unit_cost, 0)
    )

    // Sort by stock status: Low Stock first, then Adequate, then In Stock
    // Always create a copy to avoid mutating the original array
    const filteredItems = computed(() => {
      const visible = statusFilter.value === 'all'
        ? searchedItems.value
        : searchedItems.value.filter(item => getStockStatusKey(item) === statusFilter.value)
      return visible.slice().sort((a, b) => {
        return STATUS_ORDER[getStockStatusKey(a)] - STATUS_ORDER[getStockStatusKey(b)]
      })
    })

    // Bar spans 0 to 3x the reorder point so the tick sits at one third
    const getReorderFill = (item) => {
      if (!item.reorder_point) return 100
      return Math.min(item.quantity_on_hand / (item.reorder_point * 3), 1) * 100
    }

    const { loading, refreshing, error, loaded, load, loadDebounced } = useDataLoader(
      () => {
        const filters = getCurrentFilters()
        // Inventory doesn't support month/status filters, only warehouse and category
        return api.getInventory({ warehouse: filters.warehouse, category: filters.category })
      },
      (data) => { items.value = data }
    )

    watch([selectedLocation, selectedCategory], loadDebounced)

    const getStockStatus = (item) => {
      const key = getStockStatusKey(item)
      return t(`status.${key}`)
    }

    const getStockStatusClass = (item) => {
      if (item.quantity_on_hand <= item.reorder_point) {
        return 'danger'
      } else if (item.quantity_on_hand <= item.reorder_point * 1.5) {
        return 'warning'
      } else {
        return 'success'
      }
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

    const showItemDetail = (item) => {
      selectedItem.value = item
      showItemModal.value = true
    }

    onMounted(load)

    return {
      t,
      loading,
      refreshing,
      error,
      loaded,
      load,
      items,
      searchQuery,
      statusFilter,
      segments,
      statusCounts,
      totalValue,
      getReorderFill,
      getStockStatusKey,
      filteredItems,
      getStockStatus,
      getStockStatusClass,
      translateCategory,
      showItemModal,
      selectedItem,
      showItemDetail,
      currentCurrency,
      formatCurrencyWithDecimals,
      translateProductName,
      translateWarehouse
    }
  }
}
</script>

<style scoped>
.meta {
  margin-left: 4px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px 10px 14px;
  border-bottom: 1px solid var(--line);
}

.segmented {
  display: flex;
  gap: 2px;
  padding: 2px;
  background: var(--sunken);
  border-radius: 7px;
  max-width: 100%;
  overflow-x: auto;
}

.seg {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border: 0;
  border-radius: 5px;
  background: transparent;
  color: var(--text);
  font: inherit;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}

.seg:hover {
  color: var(--ink);
}

.seg.active {
  background: var(--surface);
  color: var(--ink);
  font-weight: 500;
  box-shadow: 0 0 0 1px var(--line-strong);
}

.seg-count {
  font-size: 12px;
  font-weight: 400;
  color: var(--muted);
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 280px;
  max-width: 100%;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: var(--muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 36px;
  padding: 0 10px 0 32px;
  border: 1px solid var(--line);
  border-radius: 6px;
  font: inherit;
  font-size: 13.5px;
  color: var(--ink);
  background: transparent;
}

.search-input:focus {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.search-input::placeholder {
  color: var(--muted);
}

.inventory-table {
  min-width: 900px;
}

.item-cell {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.item-sku {
  width: 64px;
  flex-shrink: 0;
  font-size: 12.5px;
  color: var(--muted);
}

.item-name,
.strong {
  color: var(--ink);
}

.reorder {
  display: flex;
  align-items: center;
  gap: 10px;
}

.reorder-track {
  position: relative;
  width: 96px;
  height: 4px;
  background: var(--sunken);
  border-radius: 2px;
}

.reorder-fill {
  height: 4px;
  border-radius: 2px;
  background: var(--ink);
}

.reorder-fill.low {
  background: var(--dot-crit);
}

.reorder-tick {
  position: absolute;
  left: 33.3%;
  top: -3px;
  width: 1px;
  height: 10px;
  background: var(--muted);
}

.reorder-value,
.bin {
  font-size: 12.5px;
  color: var(--muted);
}

td.bin {
  text-align: left;
  white-space: nowrap;
}

.table-footer {
  padding: 10px 18px;
  font-size: 12.5px;
  color: var(--muted);
  border-top: 1px solid var(--line);
}

.clickable-row {
  cursor: pointer;
}
</style>
