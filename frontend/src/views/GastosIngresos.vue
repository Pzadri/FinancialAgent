<template>
  <div class="gastos-ingresos">
    <h1 class="page-title">Gastos / Ingresos</h1>

    <!-- Filtros -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Desde</label>
        <input type="date" v-model="filters.dateFrom" class="filter-input" />
      </div>
      <div class="filter-group">
        <label>Hasta</label>
        <input type="date" v-model="filters.dateTo" class="filter-input" />
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
      <div class="filter-group">
        <label>Tipo de Gasto</label>
        <select v-model="filters.expenseType" class="filter-input">
          <option value="">Todos</option>
          <option value="fijo">Fijo</option>
          <option value="unico">Único</option>
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
            <th @click="sortBy('expenseType')" class="sortable">
              Tipo de Gasto
              <i :class="getSortIcon('expenseType')"></i>
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
            <td>
              <span class="type-badge" :class="item.expenseType">
                {{ item.expenseType === 'fijo' ? 'Fijo' : 'Único' }}
              </span>
            </td>
            <td :class="item.amount > 0 ? 'income' : 'expense'">
              {{ item.amount > 0 ? '+' : '' }}${{ Math.abs(item.amount).toLocaleString() }}
            </td>
          </tr>
          <tr v-if="filteredAndSorted.length === 0">
            <td colspan="5" class="empty-row">No hay registros que coincidan con los filtros</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Resumen -->
    <div class="summary-bar">
      <div class="summary-item">
        <span class="summary-label">Total Ingresos:</span>
        <span class="income">+${{ totalIncome.toLocaleString() }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Total Gastos:</span>
        <span class="expense">-${{ totalExpenses.toLocaleString() }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Balance:</span>
        <span :class="balance >= 0 ? 'income' : 'expense'">
          {{ balance >= 0 ? '+' : '' }}${{ Math.abs(balance).toLocaleString() }}
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
import { ref, computed } from 'vue'

const transactions = ref([
  { id: 1, date: '2026-05-20', description: 'Salario', category: 'Salario', expenseType: 'fijo', amount: 450000 },
  { id: 2, date: '2026-05-18', description: 'Alquiler', category: 'Vivienda', expenseType: 'fijo', amount: -120000 },
  { id: 3, date: '2026-05-17', description: 'Supermercado', category: 'Alimentación', expenseType: 'unico', amount: -35000 },
  { id: 4, date: '2026-05-15', description: 'Freelance proyecto web', category: 'Freelance', expenseType: 'unico', amount: 80000 },
  { id: 5, date: '2026-05-14', description: 'Netflix', category: 'Entretenimiento', expenseType: 'fijo', amount: -5000 },
  { id: 6, date: '2026-05-12', description: 'Combustible', category: 'Transporte', expenseType: 'unico', amount: -25000 },
  { id: 7, date: '2026-05-10', description: 'Electricidad', category: 'Servicios', expenseType: 'fijo', amount: -18000 },
  { id: 8, date: '2026-05-08', description: 'Restaurante', category: 'Alimentación', expenseType: 'unico', amount: -12000 },
  { id: 9, date: '2026-05-05', description: 'Internet', category: 'Servicios', expenseType: 'fijo', amount: -8000 },
  { id: 10, date: '2026-05-03', description: 'Gimnasio', category: 'Salud', expenseType: 'fijo', amount: -15000 },
  { id: 11, date: '2026-05-01', description: 'Venta Mercadolibre', category: 'Ventas', expenseType: 'unico', amount: 25000 },
  { id: 12, date: '2026-04-28', description: 'Seguro auto', category: 'Transporte', expenseType: 'fijo', amount: -35000 },
  { id: 13, date: '2026-04-25', description: 'Ropa', category: 'Personal', expenseType: 'unico', amount: -22000 },
  { id: 14, date: '2026-04-20', description: 'Salario', category: 'Salario', expenseType: 'fijo', amount: 450000 },
  { id: 15, date: '2026-04-18', description: 'Alquiler', category: 'Vivienda', expenseType: 'fijo', amount: -120000 }
])

const filters = ref({
  dateFrom: '',
  dateTo: '',
  category: '',
  type: '',
  expenseType: ''
})

const sort = ref({
  field: 'date',
  order: 'desc'
})

const categories = computed(() => {
  const cats = new Set(transactions.value.map(t => t.category))
  return [...cats].sort()
})

const filteredAndSorted = computed(() => {
  let result = [...transactions.value]

  // Filtro por fecha desde
  if (filters.value.dateFrom) {
    result = result.filter(t => t.date >= filters.value.dateFrom)
  }

  // Filtro por fecha hasta
  if (filters.value.dateTo) {
    result = result.filter(t => t.date <= filters.value.dateTo)
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

  // Filtro por tipo de gasto (fijo/unico)
  if (filters.value.expenseType) {
    result = result.filter(t => t.expenseType === filters.value.expenseType)
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
  filters.value = { dateFrom: '', dateTo: '', category: '', type: '', expenseType: '' }
}
</script>

<style scoped>
.gastos-ingresos {
  max-width: 1200px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #e1e8ed;
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
