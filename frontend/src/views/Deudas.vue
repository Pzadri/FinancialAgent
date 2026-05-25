<template>
  <div class="deudas">
    <div class="page-header">
      <h1 class="page-title">Deudas</h1>
      <router-link to="/deudas/nuevo" class="btn-primary">
        <i class="pi pi-plus"></i> Nuevo Préstamo
      </router-link>
    </div>

    <!-- Mensaje -->
    <div v-if="message" class="alert-message" :class="messageType">
      {{ message }}
    </div>

    <!-- Resumen -->
    <div class="stats-grid" v-if="deudas.length > 0">
      <div class="stat-card">
        <div class="stat-icon debt"><i class="pi pi-exclamation-triangle"></i></div>
        <div class="stat-info">
          <span class="stat-label">Deuda Total</span>
          <span class="stat-value">${{ formatMoney(totalDebt) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon count"><i class="pi pi-list"></i></div>
        <div class="stat-info">
          <span class="stat-label">Préstamos Activos</span>
          <span class="stat-value">{{ deudas.length }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon next"><i class="pi pi-clock"></i></div>
        <div class="stat-info">
          <span class="stat-label">Próximo Pago</span>
          <span class="stat-value">{{ nextPaymentInfo }}</span>
        </div>
      </div>
    </div>

    <!-- Cards de deudas -->
    <div class="deudas-grid">
      <div v-for="deuda in deudas" :key="deuda.id" class="deuda-card">
        <div class="deuda-header">
          <div class="deuda-name">
            <i class="pi pi-money-bill"></i>
            <h3>{{ deuda.name }}</h3>
          </div>
          <span class="frequency-badge" :class="deuda.frequency">
            {{ deuda.frequencyLabel }}
          </span>
        </div>

        <div class="deuda-details">
          <div class="detail-row">
            <span class="detail-label">Deuda Total</span>
            <span class="detail-value debt-color">${{ formatMoney(deuda.totalDebt) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Cantidad a Pagar</span>
            <span class="detail-value highlight">${{ formatMoney(deuda.paymentAmount) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Pagos Restantes</span>
            <span class="detail-value">{{ deuda.paymentsRemaining }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Próxima Fecha de Pago</span>
            <span class="detail-value highlight">{{ formatDate(deuda.nextPaymentDate) }}</span>
          </div>
        </div>

        <PaymentCountdown :days="deuda.daysUntilPayment" />
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="deudas.length === 0" class="empty-state">
      <i class="pi pi-check-circle"></i>
      <p>No tienes deudas registradas</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PaymentCountdown from '../components/PaymentCountdown.vue'
import { formatMoney } from '../utils/format.js'
import { mockDeudas } from '../data/mockData.js'

const deudas = ref([])
const totalDebt = ref(0)
const message = ref('')
const messageType = ref('')

const nextPaymentInfo = computed(() => {
  if (deudas.value.length === 0) return 'N/A'
  const sorted = [...deudas.value].sort((a, b) => a.daysUntilPayment - b.daysUntilPayment)
  const next = sorted[0]
  return `${next.daysUntilPayment}d - $${formatMoney(next.paymentAmount)}`
})

onMounted(() => {
  deudas.value = mockDeudas.deudas
  totalDebt.value = mockDeudas.totalDebt
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.deudas { max-width: 1000px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title { font-size: 1.8rem; font-weight: 700; color: #e1e8ed; }

.btn-primary {
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
  transition: background-color 0.2s;
}
.btn-primary:hover { background-color: #1a91da; }

/* Form */
.form-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}
.form-card h3 { color: #e1e8ed; margin-bottom: 16px; }

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

.form-actions { margin-top: 8px; }

/* Message */
.alert-message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.9rem;
}
.alert-message.success { background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.alert-message.error { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.stat-icon.debt { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; }
.stat-icon.count { background-color: rgba(29, 161, 242, 0.15); color: #1da1f2; }
.stat-icon.next { background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; }

.stat-info { display: flex; flex-direction: column; }
.stat-label { font-size: 0.8rem; color: #8899a6; margin-bottom: 4px; }
.stat-value { font-size: 1.3rem; font-weight: 700; color: #e1e8ed; }

/* Deudas Grid */
.deudas-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.deuda-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-top: 3px solid #ef4444;
  border-radius: 12px;
  padding: 20px;
}

.deuda-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.deuda-name { display: flex; align-items: center; gap: 10px; }
.deuda-name i { color: #ef4444; font-size: 1.1rem; }
.deuda-name h3 { color: #e1e8ed; font-size: 1rem; margin: 0; }

.frequency-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
}
.frequency-badge.mensual { background-color: rgba(29, 161, 242, 0.15); color: #1da1f2; }
.frequency-badge.quincenal { background-color: rgba(139, 92, 246, 0.15); color: #8b5cf6; }

.deuda-details { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}
.detail-label { color: #8899a6; font-size: 0.82rem; }
.detail-value { color: #e1e8ed; font-size: 0.9rem; font-weight: 600; }
.debt-color { color: #ef4444; }
.highlight { color: #f59e0b; }

/* countdown handled by PaymentCountdown component */

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #8899a6;
}
.empty-state i { font-size: 3rem; margin-bottom: 12px; color: #10b981; display: block; }
.empty-state p { font-size: 1rem; }

@media (max-width: 768px) {
  .page-title { font-size: 1.4rem; }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .deudas-grid { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

</style>
