<template>
  <BaseModal :open="isOpen && !!inventoryItem" title="Inventory Item Details" max-width="700px" @close="close">

          <div class="modal-body">
            <div class="detail-head">
              <div class="detail-title">
                <h4 class="detail-name">{{ translateProductName(inventoryItem.name) }}</h4>
                <div class="detail-sub num">SKU: {{ inventoryItem.sku }}</div>
              </div>
            </div>

            <div class="summary">
              <div class="summary-cell">
                <div class="summary-label">Quantity on Hand</div>
                <div class="summary-value">{{ inventoryItem.quantity_on_hand }} units</div>
              </div>
              <div class="summary-cell">
                <div class="summary-label">Stock Level</div>
                <div class="summary-value" :class="getSummaryValueClass()">{{ stockPercentage }}%</div>
                <div class="summary-note">vs. reorder point</div>
              </div>
            </div>

            <dl class="detail-list">
              <div class="detail-row">
                <dt class="detail-label">Category</dt>
                <dd class="detail-value">{{ inventoryItem.category }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Reorder Point</dt>
                <dd class="detail-value num">{{ inventoryItem.reorder_point }} units</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Units Remaining</dt>
                <dd class="detail-value num" :class="inventoryItem.quantity_on_hand <= inventoryItem.reorder_point ? 'neg' : 'pos'">{{ inventoryItem.quantity_on_hand - inventoryItem.reorder_point }} units</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Unit Cost</dt>
                <dd class="detail-value num">{{ money(inventoryItem.unit_cost, 2) }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Total Value</dt>
                <dd class="detail-value num">{{ money(totalValue, 2) }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Warehouse</dt>
                <dd class="detail-value">{{ translateWarehouse(inventoryItem.location) }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Status</dt>
                <dd class="detail-value">
                  <span :class="['badge', getStockStatusClass()]">{{ getStockStatus() }}</span>
                </dd>
              </div>
            </dl>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="close">Close</button>
          </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'

const { currentCurrency, translateProductName, translateWarehouse } = useI18n()

const money = (value, decimals = 0) => formatCurrencyWithDecimals(value, currentCurrency.value, decimals)

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  inventoryItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const totalValue = computed(() => {
  if (!props.inventoryItem) return 0
  return props.inventoryItem.quantity_on_hand * props.inventoryItem.unit_cost
})

const stockPercentage = computed(() => {
  if (!props.inventoryItem || props.inventoryItem.reorder_point === 0) return 0
  return Math.round((props.inventoryItem.quantity_on_hand / props.inventoryItem.reorder_point) * 100)
})

const close = () => {
  emit('close')
}

const getStockStatus = () => {
  if (!props.inventoryItem) return 'Unknown'
  if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point) {
    return 'Low Stock'
  } else if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point * 1.5) {
    return 'Adequate'
  } else {
    return 'In Stock'
  }
}

const getStockStatusClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger'
  if (status === 'Adequate') return 'warning'
  return 'success'
}

const getSummaryValueClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'neg'
  if (status === 'Adequate') return ''
  return 'pos'
}
</script>

<style scoped>
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.detail-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-title {
  min-width: 0;
}

.detail-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.3;
  margin: 0;
}

.detail-sub {
  margin-top: 2px;
  font-size: 12.5px;
  color: var(--muted);
}

.summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
}

.summary-cell {
  background: var(--surface);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.summary-label {
  font-size: 13px;
  color: var(--muted);
}

.summary-value {
  font-size: 20px;
  font-weight: 500;
  letter-spacing: -0.01em;
  font-variant-numeric: tabular-nums;
  color: var(--ink);
  line-height: 1.2;
}

.summary-note {
  font-size: 12px;
  color: var(--muted);
}

.summary-value.neg { color: var(--neg); }
.summary-value.pos { color: var(--pos); }

.detail-list {
  margin: 0;
}

.detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 40px;
  padding: 8px 0;
  border-bottom: 1px solid var(--line);
}

.detail-row:last-child {
  border-bottom: 0;
}

.detail-label {
  font-size: 13px;
  color: var(--muted);
  flex-shrink: 0;
}

.detail-value {
  font-size: 13.5px;
  color: var(--ink);
  text-align: right;
  min-width: 0;
  overflow-wrap: anywhere;
}

.detail-value.neg { color: var(--neg); }
.detail-value.pos { color: var(--pos); }

.modal-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--line);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
