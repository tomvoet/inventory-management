<template>
  <BaseModal :open="isOpen && !!costData" :title="`${costData?.month} Cost Breakdown`" max-width="600px" @close="close">

          <div class="modal-body">
            <div class="summary single">
              <div class="summary-cell">
                <div class="summary-label">Total Costs</div>
                <div class="summary-value">{{ money(totalCosts) }}</div>
              </div>
            </div>

            <div class="cost-list">
              <div class="cost-row">
                <div class="cost-top">
                  <span class="cost-name">Procurement</span>
                  <span class="cost-amount num">{{ money(costData.procurement) }}</span>
                </div>
                <div class="cost-bar" aria-hidden="true"><span :style="{ width: getProcurementPercentage() + '%' }"></span></div>
                <div class="cost-pct num">{{ getProcurementPercentage() }}% of total</div>
              </div>
              <div class="cost-row">
                <div class="cost-top">
                  <span class="cost-name">Operational</span>
                  <span class="cost-amount num">{{ money(costData.operational) }}</span>
                </div>
                <div class="cost-bar" aria-hidden="true"><span :style="{ width: getOperationalPercentage() + '%' }"></span></div>
                <div class="cost-pct num">{{ getOperationalPercentage() }}% of total</div>
              </div>
              <div class="cost-row">
                <div class="cost-top">
                  <span class="cost-name">Labor</span>
                  <span class="cost-amount num">{{ money(costData.labor) }}</span>
                </div>
                <div class="cost-bar" aria-hidden="true"><span :style="{ width: getLaborPercentage() + '%' }"></span></div>
                <div class="cost-pct num">{{ getLaborPercentage() }}% of total</div>
              </div>
              <div class="cost-row">
                <div class="cost-top">
                  <span class="cost-name">Overhead</span>
                  <span class="cost-amount num">{{ money(costData.overhead) }}</span>
                </div>
                <div class="cost-bar" aria-hidden="true"><span :style="{ width: getOverheadPercentage() + '%' }"></span></div>
                <div class="cost-pct num">{{ getOverheadPercentage() }}% of total</div>
              </div>
            </div>
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
  costData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const totalCosts = computed(() => {
  if (!props.costData) return 0
  return props.costData.procurement + props.costData.operational +
         props.costData.labor + props.costData.overhead
})

const getProcurementPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.procurement / totalCosts.value) * 100).toFixed(1)
}

const getOperationalPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.operational / totalCosts.value) * 100).toFixed(1)
}

const getLaborPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.labor / totalCosts.value) * 100).toFixed(1)
}

const getOverheadPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.overhead / totalCosts.value) * 100).toFixed(1)
}

const close = () => {
  emit('close')
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

.summary.single {
  grid-template-columns: minmax(0, 1fr);
}

.cost-row {
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}

.cost-row:last-child {
  border-bottom: 0;
}

.cost-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.cost-name {
  font-size: 13.5px;
  color: var(--ink);
}

.cost-amount {
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
}

.cost-bar {
  height: 4px;
  margin: 8px 0 6px;
  border-radius: 2px;
  background: var(--sunken);
  overflow: hidden;
}

.cost-bar span {
  display: block;
  height: 100%;
  background: var(--ink);
}

.cost-pct {
  font-size: 12px;
  color: var(--muted);
}
</style>
