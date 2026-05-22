<template>
  <div class="nueva-deuda">
    <div class="page-header">
      <button class="btn-back" @click="$router.push('/deudas')">
        <i class="pi pi-arrow-left"></i> Regresar
      </button>
      <h1 class="page-title">Nuevo Préstamo</h1>
    </div>

    <div class="form-card">
      <form @submit.prevent="submitDeuda" class="deuda-form">
        <div class="form-row">
          <div class="form-group flex-2">
            <label>Nombre del Préstamo</label>
            <input type="text" v-model="form.name" class="form-input" placeholder="Ej: Préstamo Banco X" required />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Deuda Total</label>
            <input type="number" v-model.number="form.totalDebt" class="form-input" placeholder="0.00" step="0.01" min="0.01" required />
          </div>
          <div class="form-group">
            <label>Temporalidad</label>
            <select v-model="form.frequency" class="form-input" required>
              <option value="">Seleccionar...</option>
              <option value="mensual">Mensual</option>
              <option value="quincenal">Quincenal</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Cantidad a Pagar (por periodo)</label>
            <input type="number" v-model.number="form.paymentAmount" class="form-input" placeholder="0.00" step="0.01" min="0.01" required />
          </div>
          <div class="form-group">
            <label>{{ form.frequency === 'quincenal' ? 'Primera fecha de pago' : 'Fecha de pago' }}</label>
            <input type="date" v-model="form.payDate1" class="form-input" required />
          </div>
          <div class="form-group" v-if="form.frequency === 'quincenal'">
            <label>Segunda fecha de pago</label>
            <input type="date" v-model="form.payDate2" class="form-input" required />
          </div>
        </div>

        <div v-if="errorMessage" class="alert-message error">{{ errorMessage }}</div>

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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const errorMessage = ref('')

const form = ref({
  name: '',
  totalDebt: null,
  paymentAmount: null,
  frequency: '',
  payDate1: '',
  payDate2: ''
})

async function submitDeuda() {
  try {
    const payDay1 = form.value.payDate1 ? new Date(form.value.payDate1 + 'T00:00:00').getDate() : 1
    const payDay2 = form.value.frequency === 'quincenal' && form.value.payDate2
      ? new Date(form.value.payDate2 + 'T00:00:00').getDate() : 0

    await axios.post('/api/deudas', {
      name: form.value.name,
      totalDebt: form.value.totalDebt,
      paymentAmount: form.value.paymentAmount,
      frequency: form.value.frequency,
      payDay1,
      payDay2,
      startDate1: form.value.payDate1,
      startDate2: form.value.frequency === 'quincenal' ? form.value.payDate2 : ''
    })

    router.push('/deudas')
  } catch (error) {
    errorMessage.value = '❌ Error: ' + (error.response?.data?.detail || error.message)
    setTimeout(() => { errorMessage.value = '' }, 4000)
  }
}

function resetForm() {
  form.value = { name: '', totalDebt: null, paymentAmount: null, frequency: '', payDate1: '', payDate2: '' }
}
</script>

<style scoped>
.nueva-deuda { max-width: 700px; }

.page-header {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 24px;
}

.page-title { font-size: 1.8rem; font-weight: 700; color: #e1e8ed; margin: 0; }

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
}

.deuda-form { display: flex; flex-direction: column; gap: 14px; }
.form-row { display: flex; gap: 12px; }
.form-group { display: flex; flex-direction: column; gap: 6px; flex: 1; }
.form-group.flex-2 { flex: 2; }
.form-group label { font-size: 0.75rem; text-transform: uppercase; color: #8899a6; font-weight: 600; }

.form-input {
  background-color: #192734;
  border: 1px solid #2d3741;
  border-radius: 8px;
  padding: 10px 14px;
  color: #e1e8ed;
  font-size: 0.9rem;
}
.form-input:focus { outline: none; border-color: #1da1f2; }

.alert-message.error {
  padding: 12px 16px;
  border-radius: 8px;
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  font-size: 0.9rem;
}

.form-actions { display: flex; gap: 12px; margin-top: 8px; }

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
.btn-primary:hover { background-color: #1a91da; }

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
.btn-secondary:hover { color: #e1e8ed; border-color: #1da1f2; }

@media (max-width: 768px) {
  .form-row { flex-direction: column; }
}
</style>
