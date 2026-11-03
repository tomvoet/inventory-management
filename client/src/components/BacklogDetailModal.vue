<template>
  <BaseModal :open="isOpen && !!backlogItem" :title="t('backlogDetail.title')" max-width="700px" @close="close">

          <div class="modal-body">
            <div class="detail-head">
              <div class="detail-title">
                <h4 class="detail-name">{{ translateProductName(backlogItem.item_name) }}</h4>
                <div class="detail-sub num">{{ t('backlogDetail.sku', { sku: backlogItem.item_sku }) }}</div>
              </div>
              <span class="badge" :class="backlogItem.priority">
                {{ t('backlogDetail.priorityLabel', { priority: t(`priority.${backlogItem.priority}`) }) }}
              </span>
            </div>

            <div class="summary">
              <div class="summary-cell">
                <div class="summary-label">{{ t('backlogDetail.shortageAmount') }}</div>
                <div class="summary-value neg">{{ t(shortage === 1 ? 'backlog.unit' : 'backlog.units', { count: shortage }) }}</div>
              </div>
              <div class="summary-cell">
                <div class="summary-label">{{ t('backlogDetail.daysDelayed') }}</div>
                <div class="summary-value">{{ t(backlogItem.days_delayed === 1 ? 'backlog.day' : 'backlog.days', { count: backlogItem.days_delayed }) }}</div>
              </div>
            </div>

            <dl class="detail-list">
              <div class="detail-row">
                <dt class="detail-label">{{ t('backlogDetail.orderId') }}</dt>
                <dd class="detail-value num">{{ backlogItem.order_id }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('backlogDetail.itemSku') }}</dt>
                <dd class="detail-value num">{{ backlogItem.item_sku }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('backlogDetail.quantityNeeded') }}</dt>
                <dd class="detail-value num">{{ t(backlogItem.quantity_needed === 1 ? 'backlog.unit' : 'backlog.units', { count: backlogItem.quantity_needed }) }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('backlogDetail.quantityAvailable') }}</dt>
                <dd class="detail-value num">{{ t(backlogItem.quantity_available === 1 ? 'backlog.unit' : 'backlog.units', { count: backlogItem.quantity_available }) }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('backlogDetail.expectedDate') }}</dt>
                <dd class="detail-value">{{ formatDate(backlogItem.expected_date) }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('backlogDetail.status') }}</dt>
                <dd class="detail-value"><span class="badge danger">{{ t('status.backordered') }}</span></dd>
              </div>
            </dl>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="close">{{ t('common.close') }}</button>
          </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const { t, currentLocale, translateProductName } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
})

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  if (!dateString) return t('backlogDetail.notAvailable')
  const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
  const date = new Date(dateString)
  return date.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
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
