<template>
  <div class="demand">
    <div class="page-header">
      <h2>{{ t('demand.title') }}</h2>
      <p>{{ t('demand.description') }}</p>
    </div>

    <DataState
      :loading="loading"
      :refreshing="refreshing"
      :error="error"
      :loaded="loaded"
      @retry="load"
    >
      <div class="card flush trend-card">
        <section v-for="group in trendGroups" :key="group.trend" class="trend-col">
          <div class="trend-head">
            <span :class="['badge', group.trend]">{{ t(group.label) }}</span>
            <span class="trend-count num">{{ t(group.items.length === 1 ? 'demand.itemsCountOne' : 'demand.itemsCount', { count: group.items.length }) }}</span>
          </div>
          <ul class="trend-items">
            <li v-for="item in group.items.slice(0, 5)" :key="item.id" class="trend-item">
              <span class="item-name">{{ item.item_name }}</span>
              <span class="num" :style="{ color: getChangeColor(item) }">{{ getChangePercent(item) }}%</span>
            </li>
          </ul>
          <div v-if="group.items.length > 5" class="more-items">
            +{{ group.items.length - 5 }} {{ t('demand.more') }}
          </div>
        </section>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('demand.demandForecasts') }}</h3>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('demand.table.sku') }}</th>
                <th>{{ t('demand.table.itemName') }}</th>
                <th class="num">{{ t('demand.table.currentDemand') }}</th>
                <th class="num">{{ t('demand.table.forecastedDemand') }}</th>
                <th class="num">{{ t('demand.table.change') }}</th>
                <th>{{ t('demand.table.trend') }}</th>
                <th>{{ t('demand.table.period') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="forecast in forecasts" :key="forecast.id">
                <td class="num sku">{{ forecast.item_sku }}</td>
                <td>{{ forecast.item_name }}</td>
                <td class="num">{{ forecast.current_demand }}</td>
                <td class="num"><strong>{{ forecast.forecasted_demand }}</strong></td>
                <td class="num" :style="{ color: getChangeColor(forecast) }">
                  {{ getChangePercent(forecast) }}%
                </td>
                <td>
                  <span :class="['badge', forecast.trend]">
                    {{ trendLabel(forecast.trend) }}
                  </span>
                </td>
                <td>{{ translatePeriod(forecast.period) }}</td>
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
import DataState from '../components/DataState.vue'
import { useDataLoader } from '../composables/useDataLoader'

export default {
  name: 'Demand',
  components: { DataState },
  setup() {
    const { t } = useI18n()
    const allForecasts = ref([])
    const inventoryItems = ref([])

    // Use shared filters
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    // Filter forecasts based on inventory filters
    const forecasts = computed(() => {
      if (selectedLocation.value === 'all' && selectedCategory.value === 'all') {
        return allForecasts.value
      }

      // Get SKUs of items that match the filters
      const validSkus = new Set(inventoryItems.value.map(item => item.sku))
      return allForecasts.value.filter(f => validSkus.has(f.item_sku))
    })

    const { loading, refreshing, error, loaded, load, loadDebounced } = useDataLoader(
      () => {
        const filters = getCurrentFilters()
        return Promise.all([
          api.getDemandForecasts(),
          api.getInventory({ warehouse: filters.warehouse, category: filters.category })
        ])
      },
      ([forecastsData, inventoryData]) => {
        allForecasts.value = forecastsData
        inventoryItems.value = inventoryData
      }
    )

    // Watch for filter changes and reload data
    watch([selectedLocation, selectedCategory], loadDebounced)

    const getForecastsByTrend = (trend) => {
      return forecasts.value.filter(f => f.trend === trend)
    }

    const trendGroups = computed(() => [
      { trend: 'increasing', label: 'demand.increasingDemand', items: getForecastsByTrend('increasing') },
      { trend: 'stable', label: 'demand.stableDemand', items: getForecastsByTrend('stable') },
      { trend: 'decreasing', label: 'demand.decreasingDemand', items: getForecastsByTrend('decreasing') }
    ])

    // Locale strings are lowercase; capitalize for display (no-op in Japanese)
    const trendLabel = (trend) => {
      const label = t(`trends.${trend}`)
      return label.charAt(0).toUpperCase() + label.slice(1)
    }

    const getChangePercent = (forecast) => {
      const change = ((forecast.forecasted_demand - forecast.current_demand) / forecast.current_demand * 100).toFixed(1)
      return change > 0 ? `+${change}` : change
    }

    const getChangeColor = (forecast) => {
      const change = forecast.forecasted_demand - forecast.current_demand
      const changePercent = Math.abs((change / forecast.current_demand) * 100)

      // Within ±2% counts as stable, so no semantic color
      if (changePercent <= 2) return 'var(--muted)'

      if (change > 0) return 'var(--pos)'
      if (change < 0) return 'var(--neg)'
      return 'var(--muted)'
    }

    const translatePeriod = (period) => {
      // Period values like "Next 3 months", "Q1 2025", "30 days", etc.
      const { currentLocale } = useI18n()
      if (currentLocale.value === 'ja') {
        return period
          .replace(/Next\s+/i, '次の')
          .replace(/\s+months/i, 'か月')
          .replace(/\s+month/i, 'か月')
          .replace(/\s+days/i, '日間')
          .replace(/\s+day/i, '日')
          .replace('Q1', '第1四半期')
          .replace('Q2', '第2四半期')
          .replace('Q3', '第3四半期')
          .replace('Q4', '第4四半期')
      }
      return period
    }

    onMounted(load)

    return {
      t,
      loading,
      refreshing,
      error,
      loaded,
      load,
      forecasts,
      trendGroups,
      trendLabel,
      getForecastsByTrend,
      getChangePercent,
      getChangeColor,
      translatePeriod
    }
  }
}
</script>

<style scoped>
/* Three columns joined by 1px gaps, same technique as the stat strip */
.trend-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1px;
  background: var(--line);
  overflow: hidden;
}

.trend-col {
  background: var(--surface);
  padding: 16px 18px;
}

.trend-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13.5px;
  color: var(--ink);
}

.trend-count {
  color: var(--muted);
  font-size: 13px;
}

.trend-items {
  list-style: none;
  margin: 0;
  padding: 0;
}

.trend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  height: 36px;
  border-top: 1px solid var(--line);
  font-size: 13.5px;
}

.item-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text);
}

.sku {
  text-align: left;
  color: var(--muted);
  font-weight: 400;
}

.more-items {
  padding-top: 8px;
  border-top: 1px solid var(--line);
  font-size: 13px;
  color: var(--muted);
}
</style>
