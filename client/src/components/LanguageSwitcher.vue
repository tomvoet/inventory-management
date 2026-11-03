<template>
  <div class="language-switcher">
    <button
      class="language-button"
      aria-haspopup="menu"
      :aria-expanded="isDropdownOpen"
      @click="toggleDropdown"
      @blur="handleBlur"
    >
      <svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="globe-icon">
        <circle cx="8" cy="8" r="6"/>
        <path d="M2 8h12"/>
        <path d="M8 2c1.8 1.7 2.6 3.7 2.6 6S9.8 12.3 8 14c-1.8-1.7-2.6-3.7-2.6-6S6.2 3.7 8 2z"/>
      </svg>
      <span class="language-label">{{ localeName }}</span>
    </button>

    <div v-if="isDropdownOpen" class="dropdown-menu">
      <button
        v-for="locale in availableLocales"
        :key="locale"
        class="dropdown-item"
        :class="{ active: currentLocale === locale }"
        @mousedown.prevent="selectLanguage(locale)"
      >
        <span class="language-name">{{ getLanguageName(locale) }}</span>
        <svg
          aria-hidden="true"
          v-if="currentLocale === locale"
          width="18"
          height="18"
          viewBox="0 0 18 18"
          fill="none"
          class="check-icon"
        >
          <path d="M4 9L7.5 12.5L14 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from '../composables/useI18n'

const { currentLocale, setLocale, availableLocales, localeName } = useI18n()

const isDropdownOpen = ref(false)

const languageNames = {
  en: 'English',
  ja: '日本語'
}

const getLanguageName = (locale) => {
  return languageNames[locale] || locale
}

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const handleBlur = () => {
  // Delay to allow mousedown events on dropdown items to fire first
  setTimeout(() => {
    isDropdownOpen.value = false
  }, 200)
}

const selectLanguage = (locale) => {
  setLocale(locale)
  isDropdownOpen.value = false
}
</script>

<style scoped>
.language-switcher {
  position: relative;
}

.language-button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 36px;
  padding: 0 8px;
  background: transparent;
  border: 0;
  border-radius: 6px;
  cursor: pointer;
  font: inherit;
  font-size: 13.5px;
  white-space: nowrap;
  color: var(--text);
}

.language-button:hover {
  background: var(--sunken);
  color: var(--ink);
}

.language-button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.globe-icon {
  flex-shrink: 0;
}

/* Opens upward because the switcher sits at the bottom of the sidebar */
.dropdown-menu {
  position: absolute;
  bottom: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--surface);
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  box-shadow: 0 8px 24px var(--shadow-md);
  z-index: 1000;
  overflow: hidden;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  height: 36px;
  padding: 0 12px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  font-size: 13.5px;
  color: var(--text);
}

.dropdown-item:hover {
  background: var(--sunken);
}

.dropdown-item.active {
  color: var(--ink);
  font-weight: 500;
}

.language-name {
  flex: 1;
}

.check-icon {
  color: var(--ink);
  flex-shrink: 0;
}

/* In the mobile top bar the switcher is at the top, so open downward again */
@media (max-width: 900px) {
  .language-button {
    width: auto;
  }

  .language-label {
    display: none;
  }

  .dropdown-menu {
    bottom: auto;
    top: calc(100% + 4px);
    left: auto;
    right: 0;
    min-width: 160px;
  }
}
</style>
