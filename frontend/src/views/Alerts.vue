<template>
  <div class="alerts">
    <h1 class="page-title">Alertas Telegram</h1>

    <div class="alert-actions">
      <button class="btn-primary" @click="sendTestAlert">
        <i class="pi pi-send"></i> Enviar Alerta de Prueba
      </button>
    </div>

    <div v-if="message" class="alert-message" :class="messageType">
      {{ message }}
    </div>

    <div class="alerts-card">
      <h3>Historial de Alertas</h3>
      <div class="alert-list">
        <div v-for="alert in alerts" :key="alert.id" class="alert-item">
          <div class="alert-icon">
            <i class="pi pi-bell"></i>
          </div>
          <div class="alert-content">
            <p class="alert-text">{{ alert.text }}</p>
            <span class="alert-time">{{ alert.time }}</span>
          </div>
          <span class="alert-status" :class="alert.status">{{ alert.status }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const message = ref('')
const messageType = ref('')

const alerts = ref([
  { id: 1, text: 'Gasto elevado detectado: $120,000 en Vivienda', time: 'Hace 2 horas', status: 'enviado' },
  { id: 2, text: 'Balance mensual actualizado: +$130,000', time: 'Hace 1 día', status: 'enviado' },
  { id: 3, text: 'Nuevo ingreso registrado: $80,000', time: 'Hace 3 días', status: 'enviado' }
])

async function sendTestAlert() {
  try {
    const response = await axios.post('/api/telegram/send', {
      message: '🔔 Alerta de prueba desde Financial Dashboard\n\n💰 Balance: $1,250,000\n📈 Ingresos del mes: $450,000\n📉 Gastos del mes: $320,000'
    })
    message.value = '✅ Alerta enviada exitosamente a Telegram'
    messageType.value = 'success'
    alerts.value.unshift({
      id: Date.now(),
      text: 'Alerta de prueba enviada',
      time: 'Ahora',
      status: 'enviado'
    })
  } catch (error) {
    message.value = '❌ Error al enviar alerta: ' + (error.response?.data?.detail || error.message)
    messageType.value = 'error'
  }
}
</script>

<style scoped>
.alerts {
  max-width: 800px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #e1e8ed;
}

.alert-actions {
  margin-bottom: 20px;
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

.alert-message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.alert-message.success {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.alert-message.error {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.alerts-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 24px;
}

.alerts-card h3 {
  color: #e1e8ed;
  margin-bottom: 16px;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background-color: #192734;
}

.alert-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background-color: rgba(245, 158, 11, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f59e0b;
}

.alert-content {
  flex: 1;
}

.alert-text {
  color: #e1e8ed;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.alert-time {
  color: #8899a6;
  font-size: 0.75rem;
}

.alert-status {
  font-size: 0.7rem;
  padding: 4px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  font-weight: 600;
}

.alert-status.enviado {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}
</style>
