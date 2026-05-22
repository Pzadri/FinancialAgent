<template>
  <div class="gastos-ingresos">
    <div class="page-header">
      <h1 class="page-title">Gastos / Ingresos</h1>
      <router-link to="/gastos-ingresos/registro" class="btn-register">
        <i class="pi pi-plus"></i> Registrar
      </router-link>
    </div>

    <!-- Filtros -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Mes</label>
        <select v-model="filters.month" class="filter-input">
          <option value="">Todos</option>
          <option v-for="m in monthOptions" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Categoría</label>
        <select v-model="filters.category" class="filter-input">
          <option value="">Todas</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Tipo</label>
        <select v-model="filters.type" class="filter-input">
          <option value="">Todos</option>
          <option value="ingreso">Ingreso</option>
          <option value="gasto">Gasto</option>
        </select>
      </div>
      <button class="btn-clear" @click="clearFilters">
        <i class="pi pi-filter-slash"></i> Limpiar
      </button>
    </div>

    <!-- Tabla -->
    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="sortBy('date')" class="sortable">
              Fecha
              <i :class="getSortIcon('date')"></i>
            </th>
            <th @click="sortBy('description')" class="sortable">
              Descripción
              <i :class="getSortIcon('description')"></i>
            </th>
            <th @click="sortBy('category')" class="sortable">
              Categoría
              <i :class="getSortIcon('category')"></i>
            </th>
            <th @click="sortBy('amount')" class="sortable">
              Monto
              <i :class="getSortIcon('amount')"></i>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredAndSorted" :key="item.id">
            <td>{{ formatDate(item.date) }}</td>
            <td>{{ item.description }}</td>
            <td><span class="category-badge">{{ item.category }}</span></td>
            <td :class="item.amount > 0 ? 'income' : 'expense'">
              {{ item.amount > 0 ? '+' : '' }}${{ Math.abs(item.amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </td>
          </tr>
          <tr v-if="filteredAndSorted.length === 0">
            <td colspan="4" class="empty-row">No hay registros que coincidan con los filtros</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Resumen -->
    <div class="summary-bar">
      <div class="summary-item">
        <span class="summary-label">Total Ingresos:</span>
        <span class="income">+${{ totalIncome.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Total Gastos:</span>
        <span class="expense">-${{ totalExpenses.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Balance:</span>
        <span :class="balance >= 0 ? 'income' : 'expense'">
          {{ balance >= 0 ? '+' : '' }}${{ Math.abs(balance).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Registros:</span>
        <span class="summary-count">{{ filteredAndSorted.length }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const transactions = ref([])
const loading = ref(true)

async function loadRecords() {
  try {
    const response = await axios.get('/api/gi/records')
    transactions.value = response.data.records
  } catch (error) {
    console.error('Error loading records:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRecords()
})

const filters = ref({
  month: '',
  category: '',
  type: ''
})

const sort = ref({
  field: 'date',
  order: 'desc'
})

// Generate last 6 months options
const monthOptions = computed(() => {
  const options = []
  const now = new Date()
  for (let i = 0; i < 6; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    const label = d.toLocaleDateString('es-AR', { month: 'long', year: 'numeric' })
    options.push({ value, label: label.charAt(0).toUpperCase() + label.slice(1) })
  }
  return options
})

const categories = computed(() => {
  const cats = new Set(transactions.value.map(t => t.category))
  return [...cats].sort()
})

const filteredAndSorted = computed(() => {
  let result = [...transactions.value]

  // Filtro por mes
  if (filters.value.month) {
    result = result.filter(t => t.date && t.date.startsWith(filters.value.month))
  }

  // Filtro por categoría
  if (filters.value.category) {
    result = result.filter(t => t.category === filters.value.category)
  }

  // Filtro por tipo (ingreso/gasto)
  if (filters.value.type) {
    if (filters.value.type === 'ingreso') {
      result = result.filter(t => t.amount > 0)
    } else {
      result = result.filter(t => t.amount < 0)
    }
  }

  // Ordenamiento
  result.sort((a, b) => {
    let valA = a[sort.value.field]
    let valB = b[sort.value.field]

    if (typeof valA === 'string') {
      valA = valA.toLowerCase()
      valB = valB.toLowerCase()
    }

    if (valA < valB) return sort.value.order === 'asc' ? -1 : 1
    if (valA > valB) return sort.value.order === 'asc' ? 1 : -1
    return 0
  })

  return result
})

const totalIncome = computed(() => {
  return filteredAndSorted.value
    .filter(t => t.amount > 0)
    .reduce((sum, t) => sum + t.amount, 0)
})

const totalExpenses = computed(() => {
  return filteredAndSorted.value
    .filter(t => t.amount < 0)
    .reduce((sum, t) => sum + Math.abs(t.amount), 0)
})

const balance = computed(() => {
  return totalIncome.value - totalExpenses.value
})

function sortBy(field) {
  if (sort.value.field === field) {
    sort.value.order = sort.value.order === 'asc' ? 'desc' : 'asc'
  } else {
    sort.value.field = field
    sort.value.order = 'asc'
  }
}

function getSortIcon(field) {
  if (sort.value.field !== field) return 'pi pi-sort-alt'
  return sort.value.order === 'asc' ? 'pi pi-sort-amount-up' : 'pi pi-sort-amount-down'
}

function formatDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function clearFilters() {
  filters.value = { month: '', category: '', type: '' }
}
</script>

<style scoped>
.gastos-ingresos {
  max-width: 1200px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0;
  color: #e1e8ed;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.btn-register {
  background-color: #1da1f2;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  transition: background-color 0.2s;
}

.btn-register:hover {
  background-color: #1a91da;
}

/* Filtros */
.filters-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-end;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: #8899a6;
  font-weight: 600;
}

.filter-input {
  background-color: #192734;
  border: 1px solid #2d3741;
  border-radius: 6px;
  padding: 8px 12px;
  color: #e1e8ed;
  font-size: 0.85rem;
  min-width: 140px;
}

.filter-input:focus {
  outline: none;
  border-color: #1da1f2;
}

.btn-clear {
  background-color: #192734;
  border: 1px solid #2d3741;
  border-radius: 6px;
  padding: 8px 14px;
  color: #8899a6;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-clear:hover {
  color: #e1e8ed;
  border-color: #1da1f2;
}

/* Tabla */
.table-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  overflow: hidden;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 14px 20px;
  font-size: 0.8rem;
  text-transform: uppercase;
  color: #8899a6;
  border-bottom: 1px solid #2d3741;
  background-color: #192734;
  user-select: none;
}

.data-table th.sortable {
  cursor: pointer;
  transition: color 0.2s;
}

.data-table th.sortable:hover {
  color: #1da1f2;
}

.data-table th i {
  font-size: 0.7rem;
  margin-left: 6px;
}

.data-table td {
  padding: 14px 20px;
  border-bottom: 1px solid #2d3741;
  color: #e1e8ed;
  font-size: 0.9rem;
}

.data-table td.income {
  color: #10b981;
  font-weight: 600;
}

.data-table td.expense {
  color: #ef4444;
  font-weight: 600;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover td {
  background-color: #1c2b3a;
}

.empty-row {
  text-align: center;
  color: #8899a6;
  padding: 40px 20px !important;
}

.category-badge {
  background-color: rgba(29, 161, 242, 0.15);
  color: #1da1f2;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
}

.type-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-badge.fijo {
  background-color: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.type-badge.unico {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.income {
  color: #10b981;
  font-weight: 600;
}

.expense {
  color: #ef4444;
  font-weight: 600;
}

/* Resumen */
.summary-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-top: 16px;
  padding: 16px 20px;
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  color: #8899a6;
  font-size: 0.85rem;
}

.summary-count {
  color: #e1e8ed;
  font-weight: 600;
}

@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
  }

  .filter-input {
    min-width: 100%;
  }
}
</style>
