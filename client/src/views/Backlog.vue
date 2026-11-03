<template>
  <div class="backlog">
    <div class="page-header">
      <h2>{{ t('backlog.title') }}</h2>
      <p>{{ t('backlog.subtitle') }}</p>
    </div>

    <DataState
      :loading="loading"
      :refreshing="refreshing"
      :error="error"
      :loaded="loaded"
      @retry="load"
    >
      <div class="stats-grid">
        <div class="stat-card danger">
          <div class="stat-label">{{ t('backlog.highPriority') }}</div>
          <div class="stat-value">{{ getBacklogByPriority('high').length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('backlog.mediumPriority') }}</div>
          <div class="stat-value">{{ getBacklogByPriority('medium').length }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('backlog.lowPriority') }}</div>
          <div class="stat-value">{{ getBacklogByPriority('low').length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('backlog.totalItems') }}</div>
          <div class="stat-value">{{ backlogItems.length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('backlog.itemsTitle') }}</h3>
        </div>
        <div v-if="backlogItems.length === 0" style="padding: 3rem; text-align: center;">
          <p style="font-size: 1.125rem; color: var(--success); font-weight: 600;">
            {{ t('backlog.empty') }}
          </p>
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('backlog.columns.orderId') }}</th>
                <th>{{ t('backlog.columns.sku') }}</th>
                <th>{{ t('backlog.columns.itemName') }}</th>
                <th>{{ t('backlog.columns.quantityNeeded') }}</th>
                <th>{{ t('backlog.columns.quantityAvailable') }}</th>
                <th>{{ t('backlog.columns.shortage') }}</th>
                <th>{{ t('backlog.columns.daysDelayed') }}</th>
                <th>{{ t('backlog.columns.priority') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in backlogItems" :key="item.id">
                <td><strong>{{ item.order_id }}</strong></td>
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ translateProductName(item.item_name) }}</td>
                <td>{{ item.quantity_needed }}</td>
                <td>{{ item.quantity_available }}</td>
                <td>
                  <span class="badge danger">
                    {{ t('backlog.unitsShort', { count: item.quantity_needed - item.quantity_available }) }}
                  </span>
                </td>
                <td>
                  <span :style="{ color: item.days_delayed > 7 ? 'var(--danger)' : 'var(--warning)' }">
                    {{ t(item.days_delayed === 1 ? 'backlog.day' : 'backlog.days', { count: item.days_delayed }) }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', item.priority]">
                    {{ t(`priority.${item.priority}`) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </DataState>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import DataState from '../components/DataState.vue'
import { useDataLoader } from '../composables/useDataLoader'

const { t, translateProductName } = useI18n()

const allBacklogItems = ref([])
const inventoryItems = ref([])

const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

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
      api.getBacklog(),
      api.getInventory({ warehouse: filters.warehouse, category: filters.category })
    ])
  },
  ([backlogData, inventoryData]) => {
    allBacklogItems.value = backlogData
    inventoryItems.value = inventoryData
  }
)

const getBacklogByPriority = (priority) => {
  return backlogItems.value.filter(item => item.priority === priority)
}

watch([selectedLocation, selectedCategory], loadDebounced)

onMounted(load)
</script>
