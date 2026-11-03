<template>
  <div class="app">
    <header class="top-nav">
      <div class="nav-container">
        <div class="logo">
          <h1>{{ t('nav.companyName') }}</h1>
          <span class="subtitle">{{ t('nav.subtitle') }}</span>
        </div>
        <nav class="nav-tabs">
          <router-link to="/" :class="{ active: $route.path === '/' }">
            {{ t('nav.overview') }}
          </router-link>
          <router-link to="/inventory" :class="{ active: $route.path === '/inventory' }">
            {{ t('nav.inventory') }}
          </router-link>
          <router-link to="/orders" :class="{ active: $route.path === '/orders' }">
            {{ t('nav.orders') }}
          </router-link>
          <router-link to="/spending" :class="{ active: $route.path === '/spending' }">
            {{ t('nav.finance') }}
          </router-link>
          <router-link to="/demand" :class="{ active: $route.path === '/demand' }">
            {{ t('nav.demandForecast') }}
          </router-link>
          <router-link to="/restocking" :class="{ active: $route.path === '/restocking' }">
            {{ t('nav.restocking') }}
          </router-link>
          <router-link to="/reports" :class="{ active: $route.path === '/reports' }">
            {{ t('nav.reports') }}
          </router-link>
        </nav>
        <div class="nav-actions">
          <button
            type="button"
            class="theme-toggle"
            :aria-label="themeLabel"
            :title="themeLabel"
            @click="toggleTheme"
          >
            <svg v-if="isDark" width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <circle cx="10" cy="10" r="3.5" stroke="currentColor" stroke-width="1.5"/>
              <path d="M10 2.5V4.5M10 15.5V17.5M2.5 10H4.5M15.5 10H17.5M4.7 4.7L6.1 6.1M13.9 13.9L15.3 15.3M4.7 15.3L6.1 13.9M13.9 6.1L15.3 4.7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path d="M16.5 11.5A6.5 6.5 0 1 1 8.5 3.5A5.5 5.5 0 0 0 16.5 11.5Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            </svg>
          </button>
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </div>
      </div>
    </header>
    <FilterBar />
    <main class="main-content">
      <router-view />
    </main>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
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

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
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
      }
    }

    const toggleTask = async (taskId) => {
      try {
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
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    // Tabs scroll horizontally on narrow widths, so keep the active one visible after navigation
    const scrollActiveTabIntoView = () => {
      nextTick(() => {
        document.querySelector('.nav-tabs a.active')?.scrollIntoView({ inline: 'nearest', block: 'nearest' })
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
      tasks,
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
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface-muted: #f8fafc;
  --surface-subtle: #f1f5f9;
  --border: #e2e8f0;
  --border-strong: #cbd5e1;
  --text: #0f172a;
  --text-body: #1e293b;
  --text-secondary: #334155;
  --text-soft: #475569;
  --text-muted: #64748b;
  --text-faint: #94a3b8;
  --chart-ink: #0f172a;
  --solid: #0f172a;
  --solid-hover: #1e293b;
  --on-accent: #ffffff;
  --btn-secondary: #64748b;
  --btn-secondary-hover: #475569;

  --accent: #2563eb;
  --accent-deep: #1e40af;
  --accent-bright: #3b82f6;
  --accent-light: #60a5fa;
  --accent-soft: #eff6ff;
  --info-bg: #dbeafe;
  --info-border: #bfdbfe;
  --info-text: #1e40af;

  --success: #10b981;
  --success-strong: #059669;
  --success-bg: #d1fae5;
  --success-soft: #f0fdf4;
  --success-border: #a7f3d0;
  --success-text: #065f46;

  --warning: #f59e0b;
  --warning-strong: #ea580c;
  --warning-bg: #fed7aa;
  --warning-tint: #fef3c7;
  --warning-soft: #fffbeb;
  --warning-border: #fed7aa;
  --warning-text: #92400e;

  --danger: #ef4444;
  --danger-strong: #dc2626;
  --danger-bg: #fecaca;
  --danger-tint: #fee2e2;
  --danger-soft: #fef2f2;
  --danger-border: #fecaca;
  --danger-text: #991b1b;

  --purple: #8b5cf6;
  --purple-soft: #f5f3ff;
  --purple-border: #c4b5fd;
  --indigo-bg: #e0e7ff;
  --indigo-text: #3730a3;

  --overlay: rgba(0, 0, 0, 0.5);
  --shadow-xs: rgba(0, 0, 0, 0.05);
  --shadow-sm: rgba(0, 0, 0, 0.06);
  --shadow-md: rgba(0, 0, 0, 0.1);
  --shadow-lg: rgba(0, 0, 0, 0.15);
  --shadow-xl: rgba(0, 0, 0, 0.3);
  --focus-ring: rgba(59, 130, 246, 0.1);
  --accent-shadow: rgba(59, 130, 246, 0.3);
  --accent-shadow-sm: rgba(37, 99, 235, 0.2);
  --slate-shadow: rgba(100, 116, 139, 0.3);
}

:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #0f172a;
  --surface: #1e293b;
  --surface-muted: #172236;
  --surface-subtle: #273449;
  --border: #334155;
  --border-strong: #475569;
  --text: #f1f5f9;
  --text-body: #e2e8f0;
  --text-secondary: #cbd5e1;
  --text-soft: #94a3b8;
  --text-muted: #94a3b8;
  --text-faint: #64748b;
  --chart-ink: #e2e8f0;
  --solid: #2563eb;
  --solid-hover: #3b82f6;
  --on-accent: #0f172a;
  --btn-secondary: #475569;
  --btn-secondary-hover: #64748b;

  --accent: #3b82f6;
  --accent-deep: #2563eb;
  --accent-bright: #60a5fa;
  --accent-light: #93c5fd;
  --accent-soft: rgba(59, 130, 246, 0.16);
  --info-bg: rgba(59, 130, 246, 0.2);
  --info-border: rgba(96, 165, 250, 0.4);
  --info-text: #93c5fd;

  --success: #34d399;
  --success-strong: #34d399;
  --success-bg: rgba(16, 185, 129, 0.2);
  --success-soft: rgba(16, 185, 129, 0.1);
  --success-border: rgba(52, 211, 153, 0.4);
  --success-text: #6ee7b7;

  --warning: #fbbf24;
  --warning-strong: #fb923c;
  --warning-bg: rgba(245, 158, 11, 0.2);
  --warning-tint: rgba(245, 158, 11, 0.16);
  --warning-soft: rgba(245, 158, 11, 0.1);
  --warning-border: rgba(251, 191, 36, 0.4);
  --warning-text: #fcd34d;

  --danger: #f87171;
  --danger-strong: #f87171;
  --danger-bg: rgba(239, 68, 68, 0.2);
  --danger-tint: rgba(239, 68, 68, 0.16);
  --danger-soft: rgba(239, 68, 68, 0.1);
  --danger-border: rgba(248, 113, 113, 0.4);
  --danger-text: #fca5a5;

  --purple: #a78bfa;
  --purple-soft: rgba(139, 92, 246, 0.12);
  --purple-border: rgba(167, 139, 250, 0.4);
  --indigo-bg: rgba(99, 102, 241, 0.22);
  --indigo-text: #a5b4fc;

  --overlay: rgba(2, 6, 23, 0.7);
  --shadow-xs: rgba(0, 0, 0, 0.3);
  --shadow-sm: rgba(0, 0, 0, 0.35);
  --shadow-md: rgba(0, 0, 0, 0.4);
  --shadow-lg: rgba(0, 0, 0, 0.5);
  --shadow-xl: rgba(0, 0, 0, 0.6);
  --focus-ring: rgba(96, 165, 250, 0.25);
  --accent-shadow: rgba(59, 130, 246, 0.4);
  --accent-shadow-sm: rgba(59, 130, 246, 0.35);
  --slate-shadow: rgba(0, 0, 0, 0.4);
}
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: var(--bg);
  color: var(--text-body);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.top-nav {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 1px 3px 0 var(--shadow-xs);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 1.5rem;
  height: 70px;
}

.logo {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  flex-shrink: 0;
  white-space: nowrap;
}

.logo h1 {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.025em;
}

.subtitle {
  font-size: 0.813rem;
  color: var(--text-muted);
  font-weight: 400;
  padding-left: 0.75rem;
  border-left: 1px solid var(--border);
}

/* Tabs take the leftover space and scroll instead of squeezing the right-hand controls */
.nav-tabs {
  display: flex;
  gap: 0.125rem;
  flex: 1 1 0;
  min-width: 0;
  /* Not flex-end: overflowing tabs would spill left, where scrolling can't reach them */
  justify-content: safe flex-end;
  overflow-x: auto;
  scrollbar-width: none;
}

.nav-tabs::-webkit-scrollbar {
  display: none;
}

.nav-tabs a {
  padding: 0.625rem 0.875rem;
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.938rem;
  white-space: nowrap;
  flex-shrink: 0;
  border-radius: 6px;
  transition: all 0.2s ease;
  position: relative;
}

.nav-tabs a:hover {
  color: var(--text);
  background: var(--surface-subtle);
}

.nav-tabs a.active {
  color: var(--accent);
  background: var(--accent-soft);
}

.nav-tabs a.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--accent);
}

.nav-tabs a:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-toggle:hover {
  background: var(--surface-muted);
  border-color: var(--border-strong);
  color: var(--text);
}

.theme-toggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

@media (max-width: 1440px) {
  .subtitle {
    display: none;
  }
}

@media (max-width: 1280px) {
  .nav-container {
    gap: 0.75rem;
    padding: 0 1rem;
  }

  .nav-tabs a {
    padding: 0.625rem 0.625rem;
    font-size: 0.875rem;
  }

  .logo h1 {
    font-size: 1.25rem;
  }
}

@media (max-width: 1100px) {
  .top-nav .nav-container .profile-name,
  .top-nav .nav-container .profile-button .chevron {
    display: none;
  }
}

@media (max-width: 720px) {
  .logo h1 {
    font-size: 1.125rem;
  }

  .top-nav .nav-container .language-label {
    display: none;
  }
}

.main-content {
  flex: 1;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.375rem;
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--text-muted);
  font-size: 0.938rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--surface);
  padding: 1.25rem;
  border-radius: 10px;
  border: 1px solid var(--border);
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 4px 12px var(--shadow-sm);
}

.stat-label {
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.625rem;
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: var(--warning-strong);
}

.stat-card.success .stat-value {
  color: var(--success-strong);
}

.stat-card.danger .stat-value {
  color: var(--danger-strong);
}

.stat-card.info .stat-value {
  color: var(--accent);
}

.card {
  background: var(--surface);
  border-radius: 10px;
  padding: 1.25rem;
  border: 1px solid var(--border);
  margin-bottom: 1.25rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--surface-muted);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-weight: 600;
  color: var(--text-soft);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: 0.5rem 0.75rem;
  border-top: 1px solid var(--surface-subtle);
  color: var(--text-secondary);
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--surface-muted);
}

.badge {
  display: inline-block;
  padding: 0.313rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success {
  background: var(--success-bg);
  color: var(--success-text);
}

.badge.warning {
  background: var(--warning-bg);
  color: var(--warning-text);
}

.badge.danger {
  background: var(--danger-bg);
  color: var(--danger-text);
}

.badge.info {
  background: var(--info-bg);
  color: var(--info-text);
}

.badge.increasing {
  background: var(--success-bg);
  color: var(--success-text);
}

.badge.decreasing {
  background: var(--danger-bg);
  color: var(--danger-text);
}

.badge.stable {
  background: var(--indigo-bg);
  color: var(--indigo-text);
}

.badge.high {
  background: var(--danger-bg);
  color: var(--danger-text);
}

.badge.medium {
  background: var(--warning-bg);
  color: var(--warning-text);
}

.badge.low {
  background: var(--info-bg);
  color: var(--info-text);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
  font-size: 0.938rem;
}

.error {
  background: var(--danger-soft);
  border: 1px solid var(--danger-border);
  color: var(--danger-text);
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.938rem;
}
</style>
