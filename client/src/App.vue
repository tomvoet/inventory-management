<template>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">CC</div>
        <div class="brand-text">
          <span class="brand-name">{{ t('nav.companyName') }}</span>
          <span class="brand-sub">{{ t('nav.brandSub') }}</span>
        </div>
      </div>

      <nav class="nav" aria-label="Main">
        <span class="nav-group">{{ t('nav.groupOperations') }}</span>
        <router-link to="/" class="nav-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="2.5" width="4.5" height="4.5" rx="1"/><rect x="9" y="2.5" width="4.5" height="4.5" rx="1"/><rect x="2.5" y="9" width="4.5" height="4.5" rx="1"/><rect x="9" y="9" width="4.5" height="4.5" rx="1"/></svg>
          <span class="nav-label">{{ t('nav.overview') }}</span>
        </router-link>
        <router-link to="/inventory" class="nav-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 1.8 14 5v6l-6 3.2L2 11V5z"/><path d="M2 5l6 3.2L14 5"/><path d="M8 8.2v6"/></svg>
          <span class="nav-label">{{ t('nav.inventory') }}</span>
        </router-link>
        <router-link to="/orders" class="nav-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5.5 4h8"/><path d="M5.5 8h8"/><path d="M5.5 12h8"/><path d="M2.5 4h.01"/><path d="M2.5 8h.01"/><path d="M2.5 12h.01"/></svg>
          <span class="nav-label">{{ t('nav.orders') }}</span>
        </router-link>
        <router-link to="/restocking" class="nav-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13.5 6.5A5.5 5.5 0 0 0 3 5"/><path d="M2.5 2v3h3"/><path d="M2.5 9.5A5.5 5.5 0 0 0 13 11"/><path d="M13.5 14v-3h-3"/></svg>
          <span class="nav-label">{{ t('nav.restocking') }}</span>
        </router-link>

        <span class="nav-group nav-group-second">{{ t('nav.groupPlanning') }}</span>
        <router-link to="/demand" class="nav-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12l4-4 3 2.5L14 4.5"/><path d="M10.5 4.5H14V8"/></svg>
          <span class="nav-label">{{ t('nav.demandForecast') }}</span>
        </router-link>
        <router-link to="/spending" class="nav-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 1.5v13"/><path d="M11.5 4.5H6.75a2 2 0 0 0 0 4h2.5a2 2 0 0 1 0 4H4.5"/></svg>
          <span class="nav-label">{{ t('nav.finance') }}</span>
        </router-link>
        <router-link to="/reports" class="nav-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 1.5h5l3 3v10H4z"/><path d="M9 1.5v3h3"/><path d="M6 9h4"/><path d="M6 11.5h4"/></svg>
          <span class="nav-label">{{ t('nav.reports') }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button
          type="button"
          class="nav-item theme-toggle"
          :aria-label="themeLabel"
          :title="themeLabel"
          @click="toggleTheme"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="8" r="6"/><path d="M8 2a6 6 0 0 0 0 12z" fill="currentColor"/></svg>
          <span class="nav-label">{{ t(isDark ? 'theme.lightMode' : 'theme.darkMode') }}</span>
        </button>
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="openTasks"
        />
      </div>
    </aside>

    <div class="content">
      <FilterBar />
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      :error="taskError"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import { useRoute } from 'vue-router'
import { useTheme } from './composables/useTheme'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const { isDark, toggleTheme } = useTheme()
    const themeLabel = computed(() => t(isDark.value ? 'theme.switchToLight' : 'theme.switchToDark'))
    const route = useRoute()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])
    const taskError = ref('')

    // Errors from a previous session of the modal shouldn't greet the user on reopen
    const openTasks = () => {
      taskError.value = ''
      showTasks.value = true
    }

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
        taskError.value = t('tasks.loadFailed')
      }
    }

    const addTask = async (taskData) => {
      try {
        taskError.value = ''
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
        taskError.value = t('tasks.addFailed')
      }
    }

    const deleteTask = async (taskId) => {
      try {
        taskError.value = ''
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
        taskError.value = t('tasks.deleteFailed')
      }
    }

    const toggleTask = async (taskId) => {
      try {
        taskError.value = ''
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            // Merge so a partial PATCH response can't drop fields like title
            apiTasks.value[index] = { ...apiTasks.value[index], ...updatedTask }
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
        taskError.value = t('tasks.toggleFailed')
      }
    }

    // Nav scrolls horizontally on narrow widths, so keep the active one visible after navigation
    const scrollActiveTabIntoView = () => {
      nextTick(() => {
        document.querySelector('.nav a.router-link-exact-active')?.scrollIntoView({ inline: 'nearest', block: 'nearest' })
      })
    }
    watch(() => route.path, scrollActiveTabIntoView)

    onMounted(() => {
      loadTasks()
      scrollActiveTabIntoView()
    })

    return {
      t,
      isDark,
      toggleTheme,
      themeLabel,
      showProfileDetails,
      showTasks,
      openTasks,
      tasks,
      taskError,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
:root {
  color-scheme: light;
  --bg: #f7f7f8;
  --surface: #ffffff;
  --sunken: #f1f1f3;
  --line: #e5e5e8;
  --line-strong: #d4d4d8;
  --ink: #09090b;
  --text: #27272a;
  --muted: #64646c;
  --accent: #3346ff;
  --accent-2: #a3adff;
  --pos: #137a3a;
  --neg: #c43d1c;
  --dot-ok: #22a559;
  --dot-warn: #e59a0c;
  --dot-crit: #e5484d;
  --seg-gray: #b4b4bb;
  --on-ink: #ffffff;
  --overlay: rgba(9, 9, 11, 0.5);
}

:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #09090b;
  --surface: #111113;
  --sunken: #1a1a1d;
  --line: #232327;
  --line-strong: #34343a;
  --ink: #fafafa;
  --text: #d4d4d8;
  --muted: #9b9ba4;
  --accent: #7f8cff;
  --accent-2: #414c9f;
  --pos: #4ade80;
  --neg: #ff7a5c;
  --dot-ok: #3fcf73;
  --dot-warn: #f2b136;
  --dot-crit: #ff6369;
  --seg-gray: #52525b;
  --on-ink: #09090b;
  --overlay: rgba(0, 0, 0, 0.7);
}

/*
  Legacy names used by not-yet-redesigned components, aliased to the new tokens.
  Declared once on :root; var() resolves per element, so they follow the active theme.
*/
:root {
  --surface-muted: var(--sunken);
  --surface-subtle: var(--sunken);
  --border: var(--line);
  --border-strong: var(--line-strong);
  --text-body: var(--text);
  --text-secondary: var(--text);
  --text-soft: var(--muted);
  --text-muted: var(--muted);
  --text-faint: var(--muted);
  --chart-ink: var(--ink);
  --solid: var(--ink);
  --solid-hover: var(--text);
  --on-accent: var(--on-ink);
  --btn-secondary: var(--muted);
  --btn-secondary-hover: var(--text);

  --accent-deep: var(--accent);
  --accent-bright: var(--accent);
  --accent-light: var(--accent-2);
  --accent-soft: color-mix(in srgb, var(--accent) 10%, transparent);
  --info-bg: color-mix(in srgb, var(--accent) 14%, transparent);
  --info-border: color-mix(in srgb, var(--accent) 35%, transparent);
  --info-text: var(--accent);

  --success: var(--dot-ok);
  --success-strong: var(--pos);
  --success-bg: color-mix(in srgb, var(--dot-ok) 18%, transparent);
  --success-soft: color-mix(in srgb, var(--dot-ok) 8%, transparent);
  --success-border: color-mix(in srgb, var(--dot-ok) 35%, transparent);
  --success-text: var(--pos);

  --warning: var(--dot-warn);
  --warning-strong: color-mix(in srgb, var(--dot-warn) 70%, var(--ink));
  --warning-bg: color-mix(in srgb, var(--dot-warn) 20%, transparent);
  --warning-tint: color-mix(in srgb, var(--dot-warn) 16%, transparent);
  --warning-soft: color-mix(in srgb, var(--dot-warn) 8%, transparent);
  --warning-border: color-mix(in srgb, var(--dot-warn) 40%, transparent);
  --warning-text: color-mix(in srgb, var(--dot-warn) 60%, var(--ink));

  --danger: var(--dot-crit);
  --danger-strong: var(--neg);
  --danger-bg: color-mix(in srgb, var(--dot-crit) 16%, transparent);
  --danger-tint: color-mix(in srgb, var(--dot-crit) 14%, transparent);
  --danger-soft: color-mix(in srgb, var(--dot-crit) 8%, transparent);
  --danger-border: color-mix(in srgb, var(--dot-crit) 35%, transparent);
  --danger-text: var(--neg);

  --purple: var(--accent);
  --purple-soft: var(--accent-soft);
  --purple-border: var(--info-border);
  --indigo-bg: var(--info-bg);
  --indigo-text: var(--accent);

  --shadow-xs: rgba(0, 0, 0, 0.04);
  --shadow-sm: rgba(0, 0, 0, 0.06);
  --shadow-md: rgba(0, 0, 0, 0.12);
  --shadow-lg: rgba(0, 0, 0, 0.18);
  --shadow-xl: rgba(0, 0, 0, 0.3);
  --focus-ring: color-mix(in srgb, var(--accent) 22%, transparent);
  --accent-shadow: color-mix(in srgb, var(--accent) 30%, transparent);
  --accent-shadow-sm: color-mix(in srgb, var(--accent) 20%, transparent);
  --slate-shadow: rgba(0, 0, 0, 0.2);
}

:root[data-theme="dark"] {
  --shadow-xs: rgba(0, 0, 0, 0.3);
  --shadow-sm: rgba(0, 0, 0, 0.35);
  --shadow-md: rgba(0, 0, 0, 0.5);
  --shadow-lg: rgba(0, 0, 0, 0.6);
  --shadow-xl: rgba(0, 0, 0, 0.7);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Geist', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Hiragino Sans', 'Noto Sans JP', sans-serif;
  font-size: 14px;
  line-height: 1.45;
  background: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.num {
  font-family: 'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  font-variant-numeric: tabular-nums;
}

/* Layout shell */
.app {
  display: grid;
  grid-template-columns: 232px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  align-self: start;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 16px 12px;
  background: var(--surface);
  border-right: 1px solid var(--line);
  z-index: 100;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px;
  min-width: 0;
}

.brand-mark {
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  border-radius: 6px;
  background: var(--ink);
  color: var(--on-ink);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.brand-sub {
  font-size: 12px;
  color: var(--muted);
  line-height: 1.2;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-group {
  font-size: 12px;
  font-weight: 500;
  color: var(--muted);
  padding: 0 8px 6px;
}

.nav-group-second {
  padding-top: 16px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 36px;
  padding: 0 8px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--text);
  font: inherit;
  font-size: 13.5px;
  text-decoration: none;
  text-align: left;
  cursor: pointer;
  white-space: nowrap;
}

.nav-item svg {
  flex-shrink: 0;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item:hover {
  background: var(--sunken);
  color: var(--ink);
}

.nav-item.router-link-exact-active {
  background: var(--sunken);
  color: var(--ink);
  font-weight: 500;
}

.nav-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.clickable-row:focus-visible,
.stacked-bar:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.sidebar-footer {
  position: relative;
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-top: 1px solid var(--line);
  padding-top: 12px;
}

.content {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1312px;
  padding: 28px 32px 48px;
}

@media (max-width: 900px) {
  .app {
    display: block;
  }

  .sidebar {
    position: static;
    height: auto;
    overflow-y: visible;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 8px;
    padding: 8px 12px 0;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .brand {
    flex: 1 1 0;
  }

  .brand-sub {
    display: none;
  }

  .sidebar-footer {
    order: 2;
    margin: 0 0 0 auto;
    flex-direction: row;
    align-items: center;
    border-top: 0;
    padding-top: 0;
    gap: 2px;
  }

  .sidebar-footer .nav-item {
    width: auto;
  }

  .sidebar-footer .nav-label {
    display: none;
  }

  .nav {
    order: 3;
    flex: 1 0 100%;
    flex-direction: row;
    gap: 2px;
    overflow-x: auto;
    scrollbar-width: none;
    padding-bottom: 8px;
  }

  .nav::-webkit-scrollbar {
    display: none;
  }

  .nav-group {
    display: none;
  }

  .nav .nav-item {
    width: auto;
    flex-shrink: 0;
    padding: 0 12px;
  }

  .main-content {
    padding: 20px 16px 40px;
  }
}

/* Page header */
.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.015em;
  color: var(--ink);
  line-height: 1.3;
}

.page-header p {
  margin-top: 4px;
  font-size: 13.5px;
  color: var(--muted);
}

/* Stat strip: cells joined by a 1px gap showing the line colour */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.stat-card {
  background: var(--surface);
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-label {
  color: var(--muted);
  font-size: 13px;
  font-weight: 400;
}

.stat-value {
  font-family: 'Geist', ui-sans-serif, system-ui, sans-serif;
  font-variant-numeric: tabular-nums;
  font-size: 26px;
  font-weight: 500;
  letter-spacing: -0.02em;
  color: var(--ink);
  line-height: 1.15;
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .stat-card {
    padding: 12px 14px 14px;
  }

  /* An odd last card would leave an empty cell showing the line-colored gap background */
  .stat-card:last-child:nth-child(odd) {
    grid-column: 1 / -1;
  }

  .stat-value {
    font-size: 22px;
  }
}

.stat-card.warning .stat-value {
  color: var(--warning-strong);
}

.stat-card.success .stat-value {
  color: var(--pos);
}

.stat-card.danger .stat-value {
  color: var(--neg);
}

/* Header and .table-container run edge to edge; other direct children get 18px side margins. Add .flush to opt out (e.g. card is just a table or toolbar) */
.card {
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--line);
  margin-bottom: 16px;
}

.card:not(.flush) > :not(.card-header):not(.table-container) {
  margin-left: 18px;
  margin-right: 18px;
}

.card:not(.flush) > :not(.card-header):not(.table-container):last-child {
  margin-bottom: 18px;
}

.card:not(.flush) > .card-header + :not(.table-container) {
  margin-top: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  border-bottom: 1px solid var(--line);
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 0;
}

.table-container {
  overflow-x: auto;
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 10px 12px;
  font-weight: 500;
  color: var(--muted);
  font-size: 12.5px;
  border-bottom: 1px solid var(--line);
  white-space: nowrap;
}

td {
  padding: 0 12px;
  height: 48px;
  border-bottom: 1px solid var(--line);
  color: var(--text);
  font-size: 13.5px;
}

th:first-child,
td:first-child {
  padding-left: 18px;
}

th:last-child,
td:last-child {
  padding-right: 18px;
}

tbody tr:last-child td {
  border-bottom: 0;
}

tbody tr:hover td {
  background: var(--sunken);
}

th.num,
td.num {
  text-align: right;
}

/* Codes and figures must never break mid-token; narrow tables scroll instead */
td.num,
td .num {
  white-space: nowrap;
}

/* Headers stay in the UI font; only cell values are monospaced */
th.num {
  font-family: inherit;
}

td strong {
  font-weight: 500;
  color: var(--ink);
}

/* Status badge: dot + plain text; variant only sets the dot colour */
.badge {
  --badge-dot: var(--seg-gray);
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--text);
  font-size: inherit;
  font-weight: 400;
  white-space: nowrap;
}

.badge::before {
  content: '';
  width: 7px;
  height: 7px;
  flex-shrink: 0;
  border-radius: 999px;
  background: var(--badge-dot);
}

.badge.success,
.badge.increasing {
  --badge-dot: var(--dot-ok);
}

.badge.warning,
.badge.medium {
  --badge-dot: var(--dot-warn);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  --badge-dot: var(--dot-crit);
}

.badge.info,
.badge.low {
  --badge-dot: var(--accent);
}

.badge.stable {
  --badge-dot: var(--seg-gray);
}

/* Buttons */
.btn,
.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  padding: 0 14px;
  border-radius: 6px;
  font: inherit;
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--ink);
}

.btn:hover,
.btn-secondary:hover {
  border-color: var(--muted);
}

.btn-primary {
  background: var(--ink);
  border-color: var(--ink);
  color: var(--on-ink);
}

.btn-primary:hover {
  opacity: 0.88;
}

.btn-sm {
  height: 32px;
  padding: 0 12px;
  font-size: 13px;
}

a {
  color: var(--accent);
}

a:hover {
  color: var(--ink);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--muted);
  font-size: 14px;
}

.error {
  background: var(--danger-soft);
  border: 1px solid var(--danger-border);
  color: var(--danger-text);
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 14px;
}
</style>
