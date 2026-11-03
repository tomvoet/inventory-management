<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-overlay" @click.self="close">
        <div
          ref="dialogRef"
          class="modal-container"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          tabindex="-1"
          :style="{ maxWidth }"
          @keydown="onKeydown"
        >
          <div class="modal-header">
            <h3 :id="titleId" class="modal-title">{{ title }}</h3>
            <button type="button" class="close-button" :aria-label="t('common.close')" @click="close">
              <svg width="16" height="16" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { useI18n } from '../composables/useI18n'

let uid = 0

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  maxWidth: { type: String, default: '700px' }
})
const emit = defineEmits(['close'])

const { t } = useI18n()
const titleId = `modal-title-${++uid}`
const dialogRef = ref(null)
let previouslyFocused = null

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

const close = () => emit('close')

const onKeydown = (e) => {
  if (e.key === 'Escape') {
    e.stopPropagation()
    close()
    return
  }
  if (e.key !== 'Tab' || !dialogRef.value) return
  const items = [...dialogRef.value.querySelectorAll(FOCUSABLE)].filter(el => el.offsetParent !== null)
  if (items.length === 0) {
    e.preventDefault()
    return
  }
  const first = items[0]
  const last = items[items.length - 1]
  const active = document.activeElement
  // Wrap at the ends; also catch focus resting on the dialog container itself
  if (e.shiftKey && (active === first || active === dialogRef.value)) {
    e.preventDefault()
    last.focus()
  } else if (!e.shiftKey && active === last) {
    e.preventDefault()
    first.focus()
  }
}

watch(() => props.open, async (isOpen) => {
  if (isOpen) {
    previouslyFocused = document.activeElement
    await nextTick()
    dialogRef.value?.focus()
  } else if (previouslyFocused) {
    // The trigger may have been removed by a re-render; focus() on a detached node is a no-op
    previouslyFocused.focus?.()
    previouslyFocused = null
  }
})

onBeforeUnmount(() => {
  previouslyFocused = null
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 16px;
}

.modal-container {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  /* The only shadow in the app: modals float above the page */
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
  width: 100%;
  max-height: calc(100vh - 32px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-container:focus {
  outline: none;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--line);
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.3;
  margin: 0;
}

.close-button {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  margin-right: -6px;
  background: transparent;
  border: 0;
  color: var(--muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
}

.close-button:hover {
  background: var(--sunken);
  color: var(--ink);
}

.close-button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.12s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@media (max-width: 480px) {
  .modal-overlay {
    padding: 8px;
  }

  .modal-container {
    max-height: calc(100vh - 16px);
  }
}
</style>
