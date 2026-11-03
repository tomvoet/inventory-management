<template>
  <div class="filters-bar">
    <div class="filters-container">
        <label class="chip">
          <span class="chip-label">{{ t('filters.timePeriod') }}</span>
          <select v-model="selectedPeriod" class="chip-select">
            <option value="all">{{ t('filters.allMonths') }}</option>
            <option value="2025-01">{{ t('months.january') }}</option>
            <option value="2025-02">{{ t('months.february') }}</option>
            <option value="2025-03">{{ t('months.march') }}</option>
            <option value="2025-04">{{ t('months.april') }}</option>
            <option value="2025-05">{{ t('months.may') }}</option>
            <option value="2025-06">{{ t('months.june') }}</option>
            <option value="2025-07">{{ t('months.july') }}</option>
            <option value="2025-08">{{ t('months.august') }}</option>
            <option value="2025-09">{{ t('months.september') }}</option>
            <option value="2025-10">{{ t('months.october') }}</option>
            <option value="2025-11">{{ t('months.november') }}</option>
            <option value="2025-12">{{ t('months.december') }}</option>
          </select>
          <svg class="chip-chevron" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5"/></svg>
        </label>

        <label class="chip">
          <span class="chip-label">{{ t('filters.location') }}</span>
          <select v-model="selectedLocation" class="chip-select">
            <option value="all">{{ t('filters.all') }}</option>
            <option value="San Francisco">{{ t('warehouses.sanFrancisco') }}</option>
            <option value="London">{{ t('warehouses.london') }}</option>
            <option value="Tokyo">{{ t('warehouses.tokyo') }}</option>
          </select>
          <svg class="chip-chevron" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5"/></svg>
        </label>

        <label class="chip">
          <span class="chip-label">{{ t('filters.category') }}</span>
          <select v-model="selectedCategory" class="chip-select">
            <option value="all">{{ t('filters.all') }}</option>
            <option value="circuit boards">{{ t('categories.circuitBoards') }}</option>
            <option value="sensors">{{ t('categories.sensors') }}</option>
            <option value="actuators">{{ t('categories.actuators') }}</option>
            <option value="controllers">{{ t('categories.controllers') }}</option>
            <option value="power supplies">{{ t('categories.powerSupplies') }}</option>
          </select>
          <svg class="chip-chevron" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5"/></svg>
        </label>

        <label class="chip">
          <span class="chip-label">{{ t('filters.orderStatus') }}</span>
          <select v-model="selectedStatus" class="chip-select">
            <option value="all">{{ t('filters.all') }}</option>
            <option value="delivered">{{ t('status.delivered') }}</option>
            <option value="shipped">{{ t('status.shipped') }}</option>
            <option value="processing">{{ t('status.processing') }}</option>
            <option value="backordered">{{ t('status.backordered') }}</option>
          </select>
          <svg class="chip-chevron" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5"/></svg>
        </label>
      <span class="filters-spacer"></span>
      <button
        class="reset-filters-btn"
        @click="resetFilters"
        :disabled="!hasActiveFilters"
        :title="t('filters.reset')"
        :aria-label="t('filters.reset')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'FilterBar',
  setup() {
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      hasActiveFilters,
      resetFilters
    } = useFilters()

    const { t } = useI18n()

    return {
      t,
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      hasActiveFilters,
      resetFilters
    }
  }
}
</script>

<style scoped>
.filters-bar {
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 90;
}

.filters-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 10px 32px;
  min-height: 56px;
}

.chip {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--surface);
  font-size: 13px;
  cursor: pointer;
}

.chip:hover {
  border-color: var(--muted);
}

.chip:focus-within {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.chip-label {
  color: var(--muted);
  white-space: nowrap;
}

/* Native select keeps keyboard and screen reader behaviour; the chevron is drawn separately */
.chip-select {
  appearance: none;
  -webkit-appearance: none;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--ink);
  font: inherit;
  font-weight: 500;
  cursor: pointer;
  padding: 0 16px 0 0;
  margin-right: -16px;
  height: 100%;
}

.chip-select option {
  background: var(--surface);
  color: var(--ink);
}

.chip-chevron {
  position: relative;
  left: 0;
  color: var(--muted);
  pointer-events: none;
  flex-shrink: 0;
}

.filters-spacer {
  flex: 1;
}

.reset-filters-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--muted);
  cursor: pointer;
  flex-shrink: 0;
}

.reset-filters-btn:hover:not(:disabled) {
  background: var(--sunken);
  color: var(--ink);
}

.reset-filters-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.reset-filters-btn svg {
  width: 16px;
  height: 16px;
}

@media (max-width: 900px) {
  /* Chips in 2 columns; reset button spans both rows in a third column so the bar stays two rows tall */
  .filters-container {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 32px;
    padding: 10px 16px;
  }

  .chip {
    min-width: 0;
  }

  .reset-filters-btn {
    grid-column: 3;
    grid-row: 1 / span 2;
    align-self: center;
  }

  .chip-select {
    flex: 1;
    min-width: 0;
    text-overflow: ellipsis;
  }

  .chip-label {
    font-size: 12.5px;
  }

  .filters-spacer {
    display: none;
  }
}
</style>
