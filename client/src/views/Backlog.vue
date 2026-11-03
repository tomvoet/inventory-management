<template>
  <div class="backlog">
    <div class="page-header">
      <h2>Backlog Management</h2>
      <p>Track and resolve inventory shortages</p>
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
          <div class="stat-label">High Priority</div>
          <div class="stat-value">{{ getBacklogByPriority('high').length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">Medium Priority</div>
          <div class="stat-value">{{ getBacklogByPriority('medium').length }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">Low Priority</div>
          <div class="stat-value">{{ getBacklogByPriority('low').length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Backlog Items</div>
          <div class="stat-value">{{ backlogItems.length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Backlog Items</h3>
        </div>
        <div v-if="backlogItems.length === 0" style="padding: 3rem; text-align: center;">
          <p style="font-size: 1.125rem; color: var(--success); font-weight: 600;">
            ✓ No backlog items - all orders can be fulfilled!
          </p>
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>SKU</th>
                <th>Item Name</th>
                <th>Quantity Needed</th>
                <th>Quantity Available</th>
                <th>Shortage</th>
                <th>Days Delayed</th>
                <th>Priority</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in backlogItems" :key="item.id">
                <td><strong>{{ item.order_id }}</strong></td>
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.quantity_needed }}</td>
                <td>{{ item.quantity_available }}</td>
                <td>
                  <span class="badge danger">
                    {{ item.quantity_needed - item.quantity_available }} units short
                  </span>
                </td>
                <td>
                  <span :style="{ color: item.days_delayed > 7 ? 'var(--danger)' : 'var(--warning)' }">
                    {{ item.days_delayed }} days
                  </span>
                </td>
                <td>
                  <span :class="['badge', item.priority]">
                    {{ item.priority }}
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

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import DataState from '../components/DataState.vue'
import { useDataLoader } from '../composables/useDataLoader'

export default {
  name: 'Backlog',
  components: { DataState },
  setup() {
    const allBacklogItems = ref([])
    const inventoryItems = ref([])

    // Use shared filters
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

    // Watch for filter changes and reload data
    watch([selectedLocation, selectedCategory], loadDebounced)

    onMounted(load)

    return {
      loading,
      refreshing,
      error,
      loaded,
      load,
      backlogItems,
      getBacklogByPriority
    }
  }
}
</script>
