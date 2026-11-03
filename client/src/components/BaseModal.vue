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
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
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
  padding: 1rem;
}

.modal-container {
  background: var(--surface);
  border-radius: 12px;
  box-shadow: 0 20px 50px var(--shadow-lg);
  width: 100%;
  max-height: 90vh;
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
  padding: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.025em;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: var(--surface-subtle);
  color: var(--text);
}

.close-button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--focus-ring);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
