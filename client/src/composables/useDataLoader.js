import { ref, onBeforeUnmount } from 'vue'

// fetcher() returns data; apply(data) runs only if no newer request has started since.
export function useDataLoader(fetcher, apply, { debounceMs = 150 } = {}) {
  const loading = ref(true) // initial load only: nothing to show yet
  const refreshing = ref(false)
  const error = ref(false)
  const loaded = ref(false)

  let seq = 0
  let timer = null

  const load = async () => {
    const id = ++seq
    if (loaded.value) refreshing.value = true
    else loading.value = true
    try {
      const data = await fetcher()
      if (id !== seq) return
      apply(data)
      loaded.value = true
      error.value = false
    } catch (err) {
      if (id !== seq) return
      console.error('Data load failed:', err)
      error.value = true
    } finally {
      if (id === seq) {
        loading.value = false
        refreshing.value = false
      }
    }
  }

  const loadDebounced = () => {
    clearTimeout(timer)
    timer = setTimeout(load, debounceMs)
  }

  onBeforeUnmount(() => {
    clearTimeout(timer)
    seq++ // drop any in-flight response
  })

  return { loading, refreshing, error, loaded, load, loadDebounced }
}
