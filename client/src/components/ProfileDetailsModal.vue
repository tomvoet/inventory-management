<template>
  <BaseModal :open="isOpen" :title="t('profileDetails.title')" max-width="600px" @close="close">

          <div class="modal-body">
            <div class="detail-head profile-head">
              <div class="avatar" aria-hidden="true">{{ getInitials(currentUser.name) }}</div>
              <div class="detail-title">
                <h4 class="detail-name">{{ currentUser.name }}</h4>
                <div class="detail-sub">{{ currentUser.jobTitle }}</div>
              </div>
            </div>

            <dl class="detail-list">
              <div class="detail-row">
                <dt class="detail-label">{{ t('profileDetails.email') }}</dt>
                <dd class="detail-value">{{ currentUser.email }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('profileDetails.department') }}</dt>
                <dd class="detail-value">{{ currentUser.department }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('profileDetails.location') }}</dt>
                <dd class="detail-value">{{ currentUser.location }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('profileDetails.phone') }}</dt>
                <dd class="detail-value num">{{ currentUser.phone }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('profileDetails.joinDate') }}</dt>
                <dd class="detail-value">{{ formatDate(currentUser.joinDate) }}</dd>
              </div>
              <div class="detail-row">
                <dt class="detail-label">{{ t('profileDetails.employeeId') }}</dt>
                <dd class="detail-value num">CC-{{ currentUser.id.toString().padStart(5, '0') }}</dd>
              </div>
            </dl>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="close">{{ t('profileDetails.close') }}</button>
          </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'
import { useAuth } from '../composables/useAuth'
import { useI18n } from '../composables/useI18n'

const { currentUser, getInitials } = useAuth()
const { t, currentLocale } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
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

.profile-head {
  align-items: center;
  justify-content: flex-start;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--line);
}

.avatar {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--ink);
  color: var(--on-ink);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}
</style>
