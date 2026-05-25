<template>
  <div class="settings">
    <h1 class="page-title">Configuración</h1>

    <div class="settings-card">
      <h3>Bot de Telegram</h3>
      <div class="setting-item">
        <label>Estado del Bot</label>
        <span class="status-badge" :class="botConnected ? 'online' : 'offline'">
          {{ botConnected ? 'Conectado' : 'Desconectado' }}
        </span>
      </div>
      <div class="setting-item">
        <label>Bot</label>
        <span class="setting-value">{{ botUsername || '@finARG_bot' }}</span>
      </div>
      <div class="setting-item">
        <label>Chat ID</label>
        <span class="setting-value">{{ chatId || 'No configurado' }}</span>
      </div>
    </div>

    <div class="settings-card">
      <h3>Notificaciones</h3>
      <div class="setting-item">
        <label>Alertas de gastos elevados</label>
        <span class="setting-value">Activado</span>
      </div>
      <div class="setting-item">
        <label>Resumen diario</label>
        <span class="setting-value">Activado</span>
      </div>
      <div class="setting-item">
        <label>Alertas de ingresos</label>
        <span class="setting-value">Activado</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { mockTelegramStatus } from '../data/mockData.js'

const chatId = ref('')
const botUsername = ref('')
const botConnected = ref(false)

onMounted(() => {
  botConnected.value = mockTelegramStatus.connected
  chatId.value = mockTelegramStatus.chat_id
  botUsername.value = mockTelegramStatus.bot_username ? '@' + mockTelegramStatus.bot_username : ''
})
</script>

<style scoped>
.settings {
  max-width: 600px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #e1e8ed;
}

.settings-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
}

.settings-card h3 {
  color: #e1e8ed;
  margin-bottom: 16px;
  font-size: 1rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #2d3741;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item label {
  color: #8899a6;
  font-size: 0.9rem;
}

.setting-value {
  color: #e1e8ed;
  font-size: 0.9rem;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.online {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.status-badge.offline {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

@media (max-width: 480px) {
  .page-title { font-size: 1.4rem; }

  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}
</style>
