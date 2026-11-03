<script setup>
import { useI18n } from '../composables/useI18n'

defineProps({
  loading: Boolean,
  refreshing: Boolean,
  error: Boolean,
  loaded: Boolean
})
defineEmits(['retry'])

const { t } = useI18n()
</script>

<template>
  <div v-if="loading" class="data-state-loading" role="status">{{ t('common.loading') }}</div>
  <template v-else>
    <div v-if="error" class="data-state-error" role="alert">
      <span>{{ t('common.loadError') }}</span>
      <button type="button" class="retry-btn" @click="$emit('retry')">{{ t('common.retry') }}</button>
    </div>
    <div v-if="refreshing" class="refresh-indicator" role="status">{{ t('common.refreshing') }}</div>
    <slot v-if="loaded" />
  </template>
</template>

<style scoped>
.data-state-loading {
  padding: 32px 0;
  text-align: center;
  color: var(--muted);
  font-size: 13.5px;
}

.data-state-error {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding: 10px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  color: var(--neg);
  font-size: 13.5px;
}

.retry-btn {
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--line-strong);
  border-radius: 6px;
  background: var(--surface);
  color: var(--neg);
  font: inherit;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
}

.retry-btn:hover {
  border-color: var(--neg);
}

.retry-btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.refresh-indicator {
  margin-bottom: 12px;
  color: var(--muted);
  font-size: 12.5px;
}
</style>
