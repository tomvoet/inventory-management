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
  <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
  <template v-else>
    <div v-if="error" class="error data-state-error" role="alert">
      <span>{{ t('common.loadError') }}</span>
      <button type="button" class="retry-btn" @click="$emit('retry')">{{ t('common.retry') }}</button>
    </div>
    <div v-if="refreshing" class="refresh-indicator" role="status">{{ t('common.refreshing') }}</div>
    <slot v-if="loaded" />
  </template>
</template>

<style scoped>
.data-state-error {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.retry-btn {
  padding: 0.375rem 0.875rem;
  border: 1px solid var(--danger-border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--danger-text);
  font-size: 0.875rem;
  cursor: pointer;
}

.retry-btn:hover {
  background: var(--danger-tint);
}

.refresh-indicator {
  margin-bottom: 0.75rem;
  color: var(--text-muted);
  font-size: 0.813rem;
}
</style>
