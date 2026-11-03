<template>
  <BaseModal :open="isOpen && !!product" title="Product Details" max-width="700px" @close="close">

          <div class="modal-body">
            <div class="detail-head">
              <div class="detail-title">
                <h4 class="detail-name">{{ product.name }}</h4>
                <div class="detail-sub num">SKU: {{ product.sku }}</div>
              </div>
            </div>

            <dl class="detail-list">
              <div class="detail-row">
                <dt class="detail-label">Category</dt>
                <dd class="detail-value">{{ product.category }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Warehouse</dt>
                <dd class="detail-value">{{ product.warehouse }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Units Ordered</dt>
                <dd class="detail-value num">{{ product.unitsOrdered }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Total Revenue</dt>
                <dd class="detail-value num">{{ money(product.revenue) }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Current Stock</dt>
                <dd class="detail-value num">{{ product.quantityOnHand }} units</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Reorder Point</dt>
                <dd class="detail-value num">{{ product.reorderPoint }} units</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">First Order Date</dt>
                <dd class="detail-value">{{ formatDate(product.firstOrderDate) }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">Stock Status</dt>
                <dd class="detail-value">
                  <span :class="['badge', getStockBadgeClass(product.stockLevel)]">{{ product.stockLevel }}</span>
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

const { currentCurrency } = useI18n()

const money = (value, decimals = 0) => formatCurrencyWithDecimals(value, currentCurrency.value, decimals)

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getStockBadgeClass = (stockLevel) => {
  if (stockLevel === 'In Stock') return 'success'
  if (stockLevel === 'Low Stock') return 'warning'
  if (stockLevel === 'Out of Stock') return 'danger'
  return 'info'
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
