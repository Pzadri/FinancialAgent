<template>
  <div class="aportaciones">
    <h1 class="page-title">Aportaciones Semanales</h1>

    <!-- Navegación de mes -->
    <div class="month-nav">
      <button class="btn-nav" @click="prevMonth"><i class="pi pi-chevron-left"></i></button>
      <span class="month-label">{{ monthLabel }}</span>
      <button class="btn-nav" @click="nextMonth"><i class="pi pi-chevron-right"></i></button>
    </div>

    <!-- Grid 3 columnas: GBM, Nu, Afore -->
    <div class="grid-3">
      <div v-for="cat in individualCategories" :key="cat.category" class="category-card">
        <div class="category-header">
          <div class="category-title">
            <span class="category-dot" :style="{ backgroundColor: getCategoryColor(cat.category) }"></span>
            <span>{{ cat.category }}</span>
          </div>
          <span class="category-amount">${{ cat.amount }}/sem</span>
        </div>

        <div class="weeks-table">
          <div class="week-row week-header">
            <span class="week-cell week-label-cell">Semana</span>
            <span class="week-cell">Estado</span>
            <span class="week-cell week-action-cell"></span>
          </div>
          <div v-for="week in cat.weeks" :key="week.id" class="week-row">
            <span class="week-cell week-label-cell">
              {{ formatWeekRange(week.weekStart, week.weekEnd) }}
            </span>
            <span class="week-cell">
              <span class="status-badge" :class="week.status">{{ statusLabel(week.status) }}</span>
            </span>
            <span class="week-cell week-action-cell">
              <button class="btn-edit" @click="openModal(week)">
                <i class="pi pi-pencil"></i>
              </button>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Grid 2 columnas: Ahorro Familiar -->
    <div class="grid-2">
      <div v-for="cat in familyCategories" :key="cat.category + cat.person" class="category-card">
        <div class="category-header">
          <div class="category-title">
            <span class="category-dot" :style="{ backgroundColor: getCategoryColor(cat.category) }"></span>
            <span>{{ cat.category }}</span>
            <span class="category-person">— {{ cat.person }}</span>
          </div>
          <span class="category-amount">${{ cat.amount }}/sem</span>
        </div>

        <div class="weeks-table">
          <div class="week-row week-header">
            <span class="week-cell week-label-cell">Semana</span>
            <span class="week-cell">Estado</span>
            <span class="week-cell week-action-cell"></span>
          </div>
          <div v-for="week in cat.weeks" :key="week.id" class="week-row">
            <span class="week-cell week-label-cell">
              {{ formatWeekRange(week.weekStart, week.weekEnd) }}
            </span>
            <span class="week-cell">
              <span class="status-badge" :class="week.status">{{ statusLabel(week.status) }}</span>
            </span>
            <span class="week-cell week-action-cell">
              <button class="btn-edit" @click="openModal(week)">
                <i class="pi pi-pencil"></i>
              </button>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de edición -->
    <div v-if="showModal" class="upload-overlay" @click.self="showModal = false">
      <div class="upload-modal modal-sm">
        <div class="upload-modal-header">
          <h3><i class="pi pi-pencil"></i> Actualizar Estado</h3>
          <button class="btn-close" @click="showModal = false"><i class="pi pi-times"></i></button>
        </div>

        <div class="upload-modal-body">
          <p class="upload-hint">
            Semana: <strong>{{ formatWeekRange(editingWeek.weekStart, editingWeek.weekEnd) }}</strong>
          </p>

          <div class="status-options">
            <button
              v-for="opt in statusOptions"
              :key="opt.value"
              class="status-option"
              :class="{ active: selectedStatus === opt.value, [opt.value]: true }"
              @click="selectedStatus = opt.value"
            >
              <i :class="opt.icon"></i>
              {{ opt.label }}
            </button>
          </div>
        </div>

        <div class="upload-modal-footer">
          <button class="btn-cancel" @click="showModal = false">Cancelar</button>
          <button class="btn-upload-confirm" :disabled="saving" @click="saveStatus">
            <i :class="saving ? 'pi pi-spin pi-spinner' : 'pi pi-check'"></i>
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const categories = ref([])
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)

const individualCategories = computed(() =>
  categories.value.filter(c => c.category !== 'Ahorro Familiar')
)
const familyCategories = computed(() =>
  categories.value.filter(c => c.category === 'Ahorro Familiar')
)

const showModal = ref(false)
const editingWeek = ref({})
const selectedStatus = ref('pendiente')
const saving = ref(false)

const statusOptions = [
  { value: 'realizada', label: 'Realizada', icon: 'pi pi-check-circle' },
  { value: 'pendiente', label: 'Pendiente', icon: 'pi pi-clock' },
]

const monthLabel = computed(() => {
  const d = new Date(currentYear.value, currentMonth.value - 1, 1)
  const label = d.toLocaleDateString('es-MX', { month: 'long', year: 'numeric' })
  return label.charAt(0).toUpperCase() + label.slice(1)
})

function getCategoryColor(category) {
  const colors = {
    'Ahorro Familiar': '#f59e0b',
    'Nu': '#8b5cf6',
    'GBM': '#1da1f2',
    'Afore': '#10b981',
  }
  return colors[category] || '#8899a6'
}

function statusLabel(status) {
  const labels = { realizada: 'Realizada', pendiente: 'Pendiente', atrasada: 'Atrasada' }
  return labels[status] || status
}

function formatWeekRange(start, end) {
  const s = new Date(start + 'T00:00:00')
  const e = new Date(end + 'T00:00:00')
  const opts = { day: '2-digit', month: 'short' }
  return `${s.toLocaleDateString('es-MX', opts)} - ${e.toLocaleDateString('es-MX', opts)}`
}

function prevMonth() {
  // Solo permitir un mes atrás del mes corriente (ventana de 3 meses)
  const now = new Date()
  const minYear = now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear()
  const minMonth = now.getMonth() === 0 ? 12 : now.getMonth() // getMonth() is 0-indexed, so this is prev month

  // Also enforce May 2026 minimum
  if (currentYear.value === 2026 && currentMonth.value <= 5) return
  if (currentYear.value < minYear || (currentYear.value === minYear && currentMonth.value <= minMonth)) return

  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  loadData()
}

function nextMonth() {
  // Solo permitir un mes adelante del mes corriente (ventana de 3 meses)
  const now = new Date()
  const maxYear = now.getMonth() === 11 ? now.getFullYear() + 1 : now.getFullYear()
  const maxMonth = now.getMonth() === 11 ? 1 : now.getMonth() + 2 // next month (1-indexed)

  if (currentYear.value > maxYear || (currentYear.value === maxYear && currentMonth.value >= maxMonth)) return

  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  loadData()
}

function openModal(week) {
  editingWeek.value = week
  selectedStatus.value = week.status
  showModal.value = true
}

async function saveStatus() {
  saving.value = true
  try {
    await axios.post('/api/aportaciones/update-status', {
      id: editingWeek.value.id,
      status: selectedStatus.value
    })
    // Update local state
    editingWeek.value.status = selectedStatus.value
    showModal.value = false
  } catch (e) {
    console.error('Error updating status:', e)
  } finally {
    saving.value = false
  }
}

async function loadData() {
  try {
    const res = await axios.get('/api/aportaciones', {
      params: { year: currentYear.value, month: currentMonth.value }
    })
    categories.value = res.data.categories
  } catch (e) {
    console.error('Error loading aportaciones:', e)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.aportaciones {
  max-width: 1200px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #e1e8ed;
}

/* Month navigation */
.month-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-nav {
  background-color: #192734;
  border: 1px solid #2d3741;
  border-radius: 8px;
  padding: 8px 12px;
  color: #e1e8ed;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-nav:hover {
  border-color: #1da1f2;
  color: #1da1f2;
}

.month-label {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e1e8ed;
  min-width: 180px;
  text-align: center;
}

/* Category cards */
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.category-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.category-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: #e1e8ed;
}

.category-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.category-person {
  font-weight: 400;
  color: #8899a6;
  font-size: 0.9rem;
}

.category-amount {
  font-size: 0.85rem;
  color: #8899a6;
  background-color: #192734;
  padding: 4px 10px;
  border-radius: 20px;
}

/* Weeks table */
.weeks-table {
  display: flex;
  flex-direction: column;
}

.week-row {
  display: grid;
  grid-template-columns: 1fr auto 50px;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #2d3741;
  gap: 12px;
}

.week-row:last-child {
  border-bottom: none;
}

.week-row.week-header {
  background-color: #192734;
  border-radius: 8px 8px 0 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #8899a6;
  font-weight: 600;
}

.week-cell {
  font-size: 0.85rem;
  color: #e1e8ed;
}

.week-label-cell {
  white-space: nowrap;
}

.week-action-cell {
  text-align: center;
}

/* Status badges */
.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.realizada {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.status-badge.pendiente {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.status-badge.atrasada {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Edit button */
.btn-edit {
  background: none;
  border: none;
  color: #8899a6;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-edit:hover {
  color: #1da1f2;
  background-color: rgba(29, 161, 242, 0.1);
}

/* Modal */
.upload-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.upload-modal {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-sm {
  max-width: 380px;
}

.upload-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #2d3741;
}

.upload-modal-header h3 {
  color: #e1e8ed;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-close {
  background: none;
  border: none;
  color: #8899a6;
  cursor: pointer;
  font-size: 1rem;
  padding: 4px;
}

.upload-modal-body {
  padding: 20px 24px;
}

.upload-hint {
  color: #8899a6;
  font-size: 0.85rem;
  margin-bottom: 16px;
}

.upload-hint strong {
  color: #e1e8ed;
}

.upload-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid #2d3741;
}

.btn-cancel {
  background-color: #192734;
  border: 1px solid #2d3741;
  border-radius: 8px;
  padding: 10px 18px;
  color: #8899a6;
  font-size: 0.85rem;
  cursor: pointer;
}

.btn-upload-confirm {
  background-color: #1da1f2;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-upload-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Status options in modal */
.status-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #2d3741;
  background-color: #192734;
  color: #8899a6;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.status-option:hover {
  border-color: #1da1f2;
}

.status-option.active.realizada {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-option.active.pendiente {
  border-color: #f59e0b;
  background-color: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-option.active.atrasada {
  border-color: #ef4444;
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Responsive */
@media (max-width: 1024px) {
  .grid-3 {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .grid-3,
  .grid-2 {
    grid-template-columns: 1fr;
  }

  .category-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .week-row {
    grid-template-columns: 1fr auto 40px;
    gap: 8px;
    padding: 8px 8px;
  }

  .week-cell {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.4rem;
  }

  .month-label {
    font-size: 0.95rem;
    min-width: 140px;
  }

  .category-card {
    padding: 14px;
  }

  .upload-modal {
    max-width: 95vw;
  }

  .status-options {
    gap: 6px;
  }

  .status-option {
    padding: 10px 12px;
    font-size: 0.85rem;
  }
}
</style>
