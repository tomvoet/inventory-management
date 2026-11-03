import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'app-theme'

const readInitialTheme = () => {
  // localStorage can throw (privacy modes, blocked storage), so never let it break startup
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === 'light' || saved === 'dark') return saved
  } catch (e) {
    // fall through to system preference
  }
  const prefersDark = typeof window !== 'undefined' &&
    window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  return prefersDark ? 'dark' : 'light'
}

const theme = ref(readInitialTheme())

const applyTheme = (value) => {
  document.documentElement.dataset.theme = value
}

applyTheme(theme.value)

watch(theme, (value) => {
  applyTheme(value)
  try {
    localStorage.setItem(STORAGE_KEY, value)
  } catch (e) {
    // persistence is best-effort
  }
})

export function useTheme() {
  const isDark = computed(() => theme.value === 'dark')
  const toggleTheme = () => {
    theme.value = isDark.value ? 'light' : 'dark'
  }
  return { theme, isDark, toggleTheme }
}
