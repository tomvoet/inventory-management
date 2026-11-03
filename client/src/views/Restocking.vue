<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error" role="alert">{{ error }}</div>
    <div v-else>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }}</h3>
          <span class="budget-max num">{{ t('restocking.budgetMax', { amount: formatCurrency(maxBudget, currentCurrency) }) }}</span>
        </div>
        <div class="budget-controls">
          <input
            v-model.number="displayBudget"
            type="range"
            min="0"
            :max="displayMax"
            :step="displayStep"
            class="budget-slider"
            :aria-label="t('restocking.budget')"
          />
          <span class="budget-symbol">{{ currencySymbol }}</span>
          <input
            v-model.number="displayBudget"
            type="number"
            min="0"
            :max="displayMax"
            :step="displayStep"
            class="budget-input num"
            :aria-label="t('restocking.budget')"
          />
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.totalCost') }}</div>
          <div class="stat-value">{{ formatCurrencyWithDecimals(totalCost, currentCurrency, 2) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
          <div class="stat-value">{{ formatCurrencyWithDecimals(remainingBudget, currentCurrency, 2) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.maxLeadTime') }}</div>
          <div class="stat-value">{{ t('restocking.days', { count: maxLeadTime }) }}</div>
        </div>
      </div>

      <div v-if="submitError" class="error" role="alert">{{ submitError }}</div>
      <div v-if="submittedOrder" class="card success-card" role="status">
        <span class="badge success">{{ t('restocking.successTitle', { orderNumber: submittedOrder.order_number }) }}</span>
        <span>{{ t('restocking.successDetail', { date: submittedOrder.expected_delivery }) }}</span>
        <router-link to="/orders">{{ t('restocking.viewOrders') }}</router-link>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ recommendations.length }})</h3>
          <button
            type="button"
            class="btn btn-primary btn-sm"
            :disabled="recommendations.length === 0 || submitting || !!submittedOrder"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.submitting') : t('restocking.placeOrder') }}
          </button>
        </div>
        <div v-if="candidates.length === 0" class="empty">{{ t('restocking.noCandidates') }}</div>
        <div v-else-if="recommendations.length === 0" class="empty">{{ t('restocking.empty') }}</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="num">{{ t('restocking.table.quantity') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="num">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rec in recommendations" :key="rec.item_sku">
                <td>
                  <div class="item-cell">
                    <span class="item-name">{{ translateProductName(rec.item_name) }}</span>
                    <span class="num item-sku">{{ rec.item_sku }}</span>
                  </div>
                </td>
                <td>
                  <span :class="['badge', rec.trend]">{{ t(`trends.${rec.trend}`) }}</span>
                </td>
                <td class="num">{{ rec.quantity }}</td>
                <td class="num">{{ formatCurrencyWithDecimals(rec.unit_cost, currentCurrency, 2) }}</td>
                <td class="num line-total">{{ formatCurrencyWithDecimals(rec.quantity * rec.unit_cost, currentCurrency, 2) }}</td>
                <td class="num">{{ t('restocking.days', { count: rec.lead_time_days }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals, convertAmount } from '../utils/currency'

const TREND_RANK = { increasing: 0, stable: 1, decreasing: 2 }
const toCents = (amount) => Math.round(amount * 100)

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()
    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const budget = ref(0)
    const submitting = ref(false)
    const submitError = ref(null)
    const submittedOrder = ref(null)

    const candidates = computed(() =>
      forecasts.value
        .map(f => ({ ...f, gap: f.forecasted_demand - f.current_demand }))
        .filter(f => f.gap > 0)
    )

    const maxBudget = computed(() => {
      const total = candidates.value.reduce((sum, c) => sum + c.gap * c.unit_cost, 0)
      return Math.ceil(total / 100) * 100
    })

    const currencySymbol = computed(() => (currentCurrency.value === 'JPY' ? '¥' : '$'))
    // Budget is stored in USD; the inputs work in the display currency so typed values match the labels
    const rate = computed(() => convertAmount(1, currentCurrency.value))
    const displayStep = computed(() => (currentCurrency.value === 'JPY' ? 10000 : 100))
    const displayMax = computed(() => convertAmount(maxBudget.value, currentCurrency.value))
    const displayBudget = computed({
      get: () => convertAmount(budget.value, currentCurrency.value),
      set: (value) => {
        const num = Number(value)
        budget.value = Number.isFinite(num) && num > 0 ? num / rate.value : 0
      }
    })

    const recommendations = computed(() => {
      const sorted = [...candidates.value].sort((a, b) => {
        const rank = (TREND_RANK[a.trend] ?? 3) - (TREND_RANK[b.trend] ?? 3)
        if (rank !== 0) return rank
        const costDiff = b.gap * b.unit_cost - a.gap * a.unit_cost
        return costDiff !== 0 ? costDiff : a.item_sku.localeCompare(b.item_sku)
      })

      // Integer cents avoid float drift making an exact-fit item fail the comparison
      let remaining = toCents(Number(budget.value) || 0)
      const picked = []
      for (const item of sorted) {
        const unitCents = toCents(item.unit_cost)
        if (unitCents <= 0) continue
        // Partial fill only when the full gap doesn't fit; later cheaper items may still fit
        const quantity = item.gap * unitCents <= remaining ? item.gap : Math.floor(remaining / unitCents)
        if (quantity < 1) continue
        picked.push({ ...item, quantity })
        remaining -= quantity * unitCents
      }
      return picked
    })

    // A changed budget makes the previous result stale and re-enables ordering
    watch(budget, () => {
      submittedOrder.value = null
      submitError.value = null
    })

    const totalCost = computed(() =>
      recommendations.value.reduce((sum, r) => sum + r.quantity * r.unit_cost, 0)
    )
    const remainingBudget = computed(() => Math.max(0, (Number(budget.value) || 0) - totalCost.value))
    const maxLeadTime = computed(() =>
      recommendations.value.reduce((max, r) => Math.max(max, r.lead_time_days), 0)
    )

    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        forecasts.value = await api.getDemandForecasts()
        budget.value = Math.round(maxBudget.value / 2 / 100) * 100
      } catch (err) {
        error.value = t('restocking.loadFailed')
        console.error('Failed to load forecasts:', err)
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      if (recommendations.value.length === 0 || submitting.value) return
      try {
        submitting.value = true
        submitError.value = null
        submittedOrder.value = null
        submittedOrder.value = await api.createRestockingOrder({
          budget: Number(budget.value),
          items: recommendations.value.map(r => ({
            item_sku: r.item_sku,
            item_name: r.item_name,
            quantity: r.quantity,
            unit_cost: r.unit_cost,
            lead_time_days: r.lead_time_days
          }))
        })
      } catch (err) {
        const detail = err.response?.data?.detail
        submitError.value = typeof detail === 'string' ? detail : t('restocking.submitFailed')
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      currentCurrency,
      translateProductName,
      formatCurrency,
      formatCurrencyWithDecimals,
      loading,
      error,
      budget,
      displayBudget,
      displayMax,
      displayStep,
      currencySymbol,
      maxBudget,
      candidates,
      recommendations,
      totalCost,
      remainingBudget,
      maxLeadTime,
      submitting,
      submitError,
      submittedOrder,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-max {
  font-size: 13px;
  color: var(--muted);
}

.budget-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px 18px;
}

.budget-slider {
  flex: 1;
  min-width: 0;
  accent-color: var(--accent);
}

.budget-symbol {
  color: var(--muted);
}

.budget-input {
  width: 140px;
  height: 36px;
  padding: 0 12px;
  border: 1px solid var(--line-strong);
  border-radius: 6px;
  background: var(--surface);
  color: var(--ink);
  font-size: 13.5px;
  text-align: right;
}

.budget-input:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -1px;
}

.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.empty {
  padding: 32px 18px;
  text-align: center;
  color: var(--muted);
}

.success-card {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  padding: 12px 18px;
  color: var(--text);
}

.success-card a {
  margin-left: auto;
}

.item-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-name {
  color: var(--ink);
}

.item-sku {
  font-size: 12px;
  color: var(--muted);
}

/* Trend keys are lowercase; capitalize for display (no effect on Japanese) */
.badge {
  text-transform: capitalize;
}

.line-total {
  color: var(--ink);
}

table {
  min-width: 640px;
}

@media (max-width: 600px) {
  .budget-controls {
    flex-wrap: wrap;
  }

  .budget-slider {
    flex: 1 0 100%;
  }
}
</style>
