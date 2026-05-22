<template>
  <div class="registro">
    <div class="page-header">
      <button class="btn-back" @click="$router.push('/gastos-ingresos')">
        <i class="pi pi-arrow-left"></i> Regresar
      </button>
      <h1 class="page-title">Registro G/I</h1>
    </div>

    <div class="form-card">
      <h3>Nuevo Registro</h3>

      <form @submit.prevent="submitRecord" class="registro-form">
        <div class="form-row">
          <div class="form-group">
            <label>Tipo</label>
            <select v-model="form.type" class="form-input" required>
              <option value="">Seleccionar...</option>
              <option value="ingreso">Ingreso</option>
              <option value="gasto">Gasto</option>
            </select>
          </div>

          <div class="form-group">
            <label>Fecha</label>
            <input type="date" v-model="form.date" class="form-input" required />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group flex-2">
            <label>Descripción</label>
            <input type="text" v-model="form.description" class="form-input" placeholder="Ej: Salario mensual" required />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Categoría</label>
            <select v-model="form.category" class="form-input" required>
              <option value="">Seleccionar...</option>
              <option v-for="cat in categoriesForType" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>Monto ($)</label>
            <input type="number" v-model.number="form.amount" class="form-input" placeholder="0.00" min="0.01" step="0.01" required />
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-primary">
            <i class="pi pi-plus"></i> Registrar
          </button>
          <button type="button" class="btn-secondary" @click="resetForm">
            <i class="pi pi-refresh"></i> Limpiar
          </button>
        </div>
      </form>
    </div>

    <!-- Mensaje de éxito -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <!-- Últimos registros -->
    <div class="recent-card">
      <h3>Últimos Registros</h3>
      <div class="recent-list">
        <div v-for="record in recentRecords" :key="record.id" class="recent-item">
          <div class="recent-icon" :class="record.amount > 0 ? 'income-icon' : 'expense-icon'">
            <i :class="record.amount > 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down'"></i>
          </div>
          <div class="recent-info">
            <span class="recent-desc">{{ record.description }}</span>
            <span class="recent-meta">{{ record.category }} · {{ formatDate(record.date) }}</span>
          </div>
          <span :class="record.amount > 0 ? 'income' : 'expense'" class="recent-amount">
            {{ record.amount > 0 ? '+' : '-' }}${{ Math.abs(record.amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </span>
        </div>
        <div v-if="recentRecords.length === 0" class="empty-state">
          No hay registros aún. Agrega tu primer gasto o ingreso.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const categories = ['Freelance', 'Delivery', 'Sueldo', 'Creditos', 'Prestamos']

const form = ref({
  type: '',
  date: new Date().toISOString().split('T')[0],
  description: '',
  category: '',
  amount: null
})

const recentRecords = ref([])
const successMessage = ref('')
const errorMessage = ref('')

const categoriesForType = computed(() => categories)

async function submitRecord() {
  try {
    const response = await axios.post('/api/gi/records', {
      date: form.value.date,
      description: form.value.description,
      category: form.value.category,
      type: form.value.type,
      amount: form.value.amount
    })

    const record = response.data.record
    recentRecords.value.unshift(record)
    successMessage.value = `✅ ${form.value.type === 'ingreso' ? 'Ingreso' : 'Gasto'} registrado: $${Math.abs(record.amount).toLocaleString()}`
    errorMessage.value = ''

    setTimeout(() => { successMessage.value = '' }, 3000)
    resetForm()
  } catch (error) {
    errorMessage.value = '❌ Error al registrar: ' + (error.response?.data?.detail || error.message)
    setTimeout(() => { errorMessage.value = '' }, 4000)
  }
}

function resetForm() {
  form.value = {
    type: '',
    date: new Date().toISOString().split('T')[0],
    description: '',
    category: '',
    amount: null
  }
}

function formatDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<style scoped>
.registro {
  max-width: 800px;
}

.page-header {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #e1e8ed;
}

.btn-back {
  position: absolute;
  left: 0;
  background: transparent;
  border: 1px solid #2d3741;
  color: #8899a6;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}
.btn-back:hover { color: #e1e8ed; border-color: #1da1f2; }

.form-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
}

.form-card h3 {
  color: #e1e8ed;
  margin-bottom: 20px;
  font-size: 1rem;
}

.registro-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.form-group.flex-2 {
  flex: 2;
}

.form-group label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #8899a6;
  font-weight: 600;
}

.form-input {
  background-color: #192734;
  border: 1px solid #2d3741;
  border-radius: 8px;
  padding: 10px 14px;
  color: #e1e8ed;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #1da1f2;
}

.form-input::placeholder {
  color: #5c6e7e;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn-primary {
  background-color: #1da1f2;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #1a91da;
}

.btn-secondary {
  background-color: #192734;
  color: #8899a6;
  border: 1px solid #2d3741;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-secondary:hover {
  color: #e1e8ed;
  border-color: #1da1f2;
}

.success-message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
  font-size: 0.9rem;
}

/* Últimos registros */
.recent-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 24px;
}

.recent-card h3 {
  color: #e1e8ed;
  margin-bottom: 16px;
  font-size: 1rem;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background-color: #192734;
}

.recent-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.recent-icon.income-icon {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.recent-icon.expense-icon {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.recent-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.recent-desc {
  color: #e1e8ed;
  font-size: 0.9rem;
}

.recent-meta {
  color: #8899a6;
  font-size: 0.75rem;
}

.recent-amount {
  font-weight: 700;
  font-size: 0.95rem;
}

.income {
  color: #10b981;
}

.expense {
  color: #ef4444;
}

.empty-state {
  text-align: center;
  color: #8899a6;
  padding: 24px;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
  }
}
</style>
