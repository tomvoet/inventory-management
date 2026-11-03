<template>
  <BaseModal :open="isOpen" :title="t('tasks.title')" max-width="900px" @close="close">

          <div class="modal-body">
            <!-- Add Task Form -->
            <div class="task-form">
              <div class="form-row">
                <div class="form-group flex-1">
                  <label for="task-title">{{ t('tasks.taskTitle') }}</label>
                  <input
                    id="task-title"
                    v-model="newTask.title"
                    type="text"
                    :placeholder="t('tasks.taskTitlePlaceholder')"
                    class="task-input"
                    @keyup.enter="handleAddTask"
                  />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="task-priority">{{ t('tasks.priority') }}</label>
                  <select
                    id="task-priority"
                    v-model="newTask.priority"
                    class="task-select"
                  >
                    <option value="high">{{ t('priority.high') }}</option>
                    <option value="medium">{{ t('priority.medium') }}</option>
                    <option value="low">{{ t('priority.low') }}</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="task-due-date">{{ t('tasks.dueDate') }}</label>
                  <input
                    id="task-due-date"
                    v-model="newTask.dueDate"
                    type="date"
                    class="task-input"
                  />
                </div>

                <div class="form-group-btn">
                  <button type="button" @click="handleAddTask" class="btn-primary task-add-btn" :disabled="!newTask.title.trim() || !newTask.dueDate">
                    {{ t('tasks.addTask') }}
                  </button>
                </div>
              </div>
            </div>

            <div v-if="error" class="task-error" role="alert">{{ error }}</div>

            <div class="tasks-divider"></div>

            <!-- Tasks List -->
            <div v-if="sortedTasks.length === 0" class="no-tasks">
              {{ t('tasks.noTasks') }}
            </div>

            <div v-else class="tasks-list">
              <div
                v-for="task in sortedTasks"
                :key="task.id"
                class="task-item"
                :class="[`priority-${task.priority}`, { completed: task.status === 'completed' }]"
              >
                <div class="task-header">
                  <div class="task-check-title">
                    <input
                      :id="`task-check-${task.id}`"
                      type="checkbox"
                      :checked="task.status === 'completed'"
                      @change="$emit('toggle-task', task.id)"
                      class="task-checkbox"
                    />
                    <label :for="`task-check-${task.id}`" class="task-title">{{ task.title }}</label>
                  </div>
                  <button type="button" @click="$emit('delete-task', task.id)" class="task-delete-btn" :title="t('tasks.deleteTask')" :aria-label="t('tasks.deleteTask')">
                    <svg width="14" height="14" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/></svg>
                  </button>
                </div>

                <div class="task-footer">
                  <span class="badge" :class="task.priority">
                    {{ translatePriority(task.priority) }}
                  </span>
                  <div class="task-due-date">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                      <rect x="2" y="3" width="10" height="9" rx="1" stroke="currentColor" stroke-width="1.2"/>
                      <path d="M4.5 1.5V4.5M9.5 1.5V4.5M2 6H12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                    </svg>
                    {{ formatDueDate(task.dueDate) }}
                  </div>
                  <span class="badge task-status" :class="statusBadgeClass(task.dueDate, task.status)">
                    {{ getStatusText(task.dueDate, task.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="close">{{ t('profileDetails.close') }}</button>
          </div>
  </BaseModal>
</template>

<script>
import BaseModal from './BaseModal.vue'
import { ref, computed, watch } from 'vue'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'TasksModal',
  components: { BaseModal },
  props: {
    isOpen: {
      type: Boolean,
      required: true
    },
    tasks: {
      type: Array,
      default: () => []
    },
    error: {
      type: String,
      default: ''
    }
  },
  emits: ['close', 'add-task', 'delete-task', 'toggle-task'],
  setup(props, { emit }) {
    const { t, currentLocale } = useI18n()
    const newTask = ref({
      title: '',
      priority: 'medium',
      dueDate: ''
    })

    const sortedTasks = computed(() => {
      // Don't sort - just return tasks in their current order (newest first)
      return [...props.tasks]
    })

    const close = () => {
      emit('close')
    }

    const handleAddTask = () => {
      if (newTask.value.title.trim() && newTask.value.dueDate) {
        emit('add-task', {
          title: newTask.value.title.trim(),
          priority: newTask.value.priority,
          dueDate: newTask.value.dueDate
        })
      }
    }

    // Reset the form only once the new task actually appears, so a failed add keeps the input
    watch(() => props.tasks.length, (len, prev) => {
      if (len > prev) newTask.value = { title: '', priority: 'medium', dueDate: '' }
    })

    const formatDueDate = (dateString) => {
      const date = new Date(dateString)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const dueDate = new Date(date)
      dueDate.setHours(0, 0, 0, 0)

      const diffTime = dueDate - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

      const isJapanese = currentLocale.value === 'ja'

      if (diffDays === 0) return isJapanese ? '今日' : 'today'
      if (diffDays === 1) return isJapanese ? '明日' : 'tomorrow'
      if (diffDays === -1) return isJapanese ? '昨日' : 'yesterday'
      if (diffDays < 0) return isJapanese ? `${Math.abs(diffDays)}日前` : `${Math.abs(diffDays)} days ago`
      if (diffDays < 7) return isJapanese ? `${diffDays}日後` : `in ${diffDays} days`

      const locale = isJapanese ? 'ja-JP' : 'en-US'
      return date.toLocaleDateString(locale, {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
      })
    }

    const getStatusClass = (dueDate, status) => {
      if (status === 'completed') return 'completed'

      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const due = new Date(dueDate)
      due.setHours(0, 0, 0, 0)

      const diffTime = due - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

      if (diffDays < 0) return 'overdue'
      if (diffDays <= 1) return 'urgent'
      return 'upcoming'
    }

    // Map task states onto the global badge dot colours
    const statusBadgeClass = (dueDate, status) => {
      const map = { completed: 'success', overdue: 'danger', urgent: 'warning', upcoming: 'info' }
      return map[getStatusClass(dueDate, status)]
    }

    const getStatusText = (dueDate, status) => {
      const isJapanese = currentLocale.value === 'ja'

      if (status === 'completed') return isJapanese ? '完了' : 'Completed'

      const statusClass = getStatusClass(dueDate, status)
      if (statusClass === 'overdue') return isJapanese ? '期限超過' : 'Overdue'
      if (statusClass === 'urgent') return isJapanese ? 'もうすぐ期限' : 'Due Soon'
      return isJapanese ? '予定' : 'Upcoming'
    }

    const translatePriority = (priority) => {
      const priorityMap = {
        'high': t('priority.high'),
        'medium': t('priority.medium'),
        'low': t('priority.low')
      }
      return priorityMap[priority] || priority
    }

    return {
      t,
      newTask,
      sortedTasks,
      close,
      handleAddTask,
      formatDueDate,
      getStatusClass,
      statusBadgeClass,
      getStatusText,
      translatePriority
    }
  }
}
</script>

<style scoped>
.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--line);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.task-error {
  margin-bottom: 12px;
  padding: 10px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  color: var(--neg);
  font-size: 13.5px;
}

.task-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.form-group-btn {
  display: flex;
  align-items: flex-end;
}

label {
  font-size: 13px;
  color: var(--muted);
}

.task-input,
.task-select {
  height: 36px;
  padding: 0 10px;
  border: 1px solid var(--line-strong);
  border-radius: 6px;
  background: var(--surface);
  color: var(--ink);
  font: inherit;
  font-size: 13.5px;
  width: 100%;
}

.task-input::placeholder {
  color: var(--muted);
}

.task-input:focus-visible,
.task-select:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -1px;
}

.task-select {
  cursor: pointer;
}

.task-add-btn {
  white-space: nowrap;
}

.task-add-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tasks-divider {
  height: 1px;
  background: var(--line);
  margin: 20px -20px;
}

.no-tasks {
  text-align: center;
  padding: 32px 0;
  color: var(--muted);
  font-size: 13.5px;
}

.tasks-list {
  display: flex;
  flex-direction: column;
}

.task-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}

.task-item:first-child {
  padding-top: 0;
}

.task-item:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.task-item.completed .task-footer {
  opacity: 0.6;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 12px;
}

.task-check-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.task-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--accent);
  flex-shrink: 0;
}

.task-checkbox:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.task-title {
  flex: 1;
  cursor: pointer;
  user-select: none;
  color: var(--ink);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.task-item.completed .task-title {
  text-decoration: line-through;
  color: var(--muted);
}

.task-delete-btn {
  width: 28px;
  height: 28px;
  background: transparent;
  color: var(--muted);
  border: 0;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
}

.task-delete-btn:hover {
  background: var(--sunken);
  color: var(--neg);
}

.task-delete-btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.task-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 16px;
  padding-left: 26px;
  font-size: 12.5px;
}

.task-due-date {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
}

.task-status {
  margin-left: auto;
}

@media (max-width: 600px) {
  .form-row {
    flex-wrap: wrap;
  }

  .form-group-btn {
    width: 100%;
  }

  .task-add-btn {
    width: 100%;
  }
}
</style>
