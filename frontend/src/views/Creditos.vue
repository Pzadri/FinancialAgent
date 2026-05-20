<template>
  <div class="creditos">
    <h1 class="page-title">Créditos</h1>

    <!-- Resumen Total -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon credit"><i class="pi pi-credit-card"></i></div>
        <div class="stat-info">
          <span class="stat-label">Crédito Total</span>
          <span class="stat-value">${{ totalCredit.toLocaleString() }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon debt"><i class="pi pi-exclamation-triangle"></i></div>
        <div class="stat-info">
          <span class="stat-label">Deuda Total</span>
          <span class="stat-value">${{ totalDebt.toLocaleString() }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon available"><i class="pi pi-check-circle"></i></div>
        <div class="stat-info">
          <span class="stat-label">Disponible Total</span>
          <span class="stat-value">${{ totalAvailable.toLocaleString() }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon usage"><i class="pi pi-percentage"></i></div>
        <div class="stat-info">
          <span class="stat-label">Uso Total</span>
          <span class="stat-value">{{ usagePercent }}%</span>
        </div>
      </div>
    </div>

    <!-- Tarjetas individuales -->
    <div class="cards-grid">
      <div v-for="card in cards" :key="card.name" class="credit-card-item" :style="{ borderTopColor: card.color }">
        <div class="card-header">
          <div class="card-brand" :style="{ backgroundColor: card.color + '20', color: card.color }">
            <i class="pi pi-credit-card"></i>
          </div>
          <div class="card-name-section">
            <h3>{{ card.name }}</h3>
            <span class="card-subtitle">Tarjeta de Crédito</span>
          </div>
        </div>

        <div class="card-usage-bar">
          <div class="usage-bar-bg">
            <div class="usage-bar-fill" :style="{ width: card.usagePercent + '%', backgroundColor: card.color }"></div>
          </div>
          <span class="usage-text">{{ card.usagePercent }}% utilizado</span>
        </div>

        <div class="card-details">
          <div class="detail-row">
            <span class="detail-label">Crédito Total</span>
            <span class="detail-value">${{ card.creditLimit.toLocaleString() }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Saldo a Deber</span>
            <span class="detail-value debt-color">${{ card.debt.toLocaleString() }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Disponible</span>
            <span class="detail-value available-color">${{ card.available.toLocaleString() }}</span>
          </div>
          <div class="detail-row separator">
            <span class="detail-label">Fecha de Corte</span>
            <span class="detail-value">{{ formatDate(card.cutoffDate) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Fecha de Pago</span>
            <span class="detail-value highlight">{{ formatDate(card.paymentDate) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Pago Mínimo</span>
            <span class="detail-value">${{ card.minimumPayment.toLocaleString() }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Pago para No Generar Intereses</span>
            <span class="detail-value highlight">${{ card.fullPayment.toLocaleString() }}</span>
          </div>
        </div>

        <div class="card-countdown">
          <i class="pi pi-clock"></i>
          <span>{{ daysUntilPayment(card.paymentDate) }} días para el pago</span>
        </div>
      </div>
    </div>

    <!-- Gráficas -->
    <div class="charts-grid">
      <div class="chart-card">
        <h3>Distribución de Deuda por Tarjeta</h3>
        <Doughnut :data="debtDistributionData" :options="doughnutOptions" />
      </div>
      <div class="chart-card">
        <h3>Crédito vs Deuda por Tarjeta</h3>
        <Bar :data="creditVsDebtData" :options="barOptions" />
      </div>
    </div>

    <!-- Tabla resumen -->
    <div class="table-card">
      <h3>Resumen de Tarjetas</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>Tarjeta</th>
            <th>Crédito</th>
            <th>Deuda</th>
            <th>Disponible</th>
            <th>Uso %</th>
            <th>Fecha Corte</th>
            <th>Fecha Pago</th>
            <th>Pago Requerido</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="card in cards" :key="card.name">
            <td>
              <span class="table-card-name" :style="{ color: card.color }">
                <i class="pi pi-credit-card"></i> {{ card.name }}
              </span>
            </td>
            <td>${{ card.creditLimit.toLocaleString() }}</td>
            <td class="debt-color">${{ card.debt.toLocaleString() }}</td>
            <td class="available-color">${{ card.available.toLocaleString() }}</td>
            <td>
              <span class="usage-badge" :class="getUsageClass(card.usagePercent)">
                {{ card.usagePercent }}%
              </span>
            </td>
            <td>{{ formatDate(card.cutoffDate) }}</td>
            <td>{{ formatDate(card.paymentDate) }}</td>
            <td class="highlight">${{ card.fullPayment.toLocaleString() }}</td>
          </tr>
          <tr class="totals-row">
            <td><strong>TOTAL</strong></td>
            <td><strong>${{ totalCredit.toLocaleString() }}</strong></td>
            <td class="debt-color"><strong>${{ totalDebt.toLocaleString() }}</strong></td>
            <td class="available-color"><strong>${{ totalAvailable.toLocaleString() }}</strong></td>
            <td><strong>{{ usagePercent }}%</strong></td>
            <td>—</td>
            <td>—</td>
            <td class="highlight"><strong>${{ totalPayment.toLocaleString() }}</strong></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

// Datos simulados de las 3 tarjetas
const cards = [
  {
    name: 'Nu',
    color: '#820ad1',
    creditLimit: 45000,
    debt: 18500,
    available: 26500,
    usagePercent: 41,
    cutoffDate: '2026-06-03',
    paymentDate: '2026-06-18',
    minimumPayment: 1850,
    fullPayment: 18500
  },
  {
    name: 'Didi',
    color: '#ff6600',
    creditLimit: 32000,
    debt: 12800,
    available: 19200,
    usagePercent: 40,
    cutoffDate: '2026-05-28',
    paymentDate: '2026-06-12',
    minimumPayment: 1280,
    fullPayment: 12800
  },
  {
    name: 'Stori',
    color: '#00c389',
    creditLimit: 25000,
    debt: 9200,
    available: 15800,
    usagePercent: 37,
    cutoffDate: '2026-06-01',
    paymentDate: '2026-06-16',
    minimumPayment: 920,
    fullPayment: 9200
  }
]

const totalCredit = computed(() => cards.reduce((sum, c) => sum + c.creditLimit, 0))
const totalDebt = computed(() => cards.reduce((sum, c) => sum + c.debt, 0))
const totalAvailable = computed(() => cards.reduce((sum, c) => sum + c.available, 0))
const totalPayment = computed(() => cards.reduce((sum, c) => sum + c.fullPayment, 0))
const usagePercent = computed(() => Math.round((totalDebt.value / totalCredit.value) * 100))

// Gráfica de distribución de deuda
const debtDistributionData = {
  labels: cards.map(c => c.name),
  datasets: [{
    data: cards.map(c => c.debt),
    backgroundColor: cards.map(c => c.color),
    borderWidth: 0
  }]
}

const doughnutOptions = {
  responsive: true,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#8899a6', padding: 16 }
    }
  }
}

// Gráfica de barras crédito vs deuda
const creditVsDebtData = {
  labels: cards.map(c => c.name),
  datasets: [
    {
      label: 'Crédito Total',
      data: cards.map(c => c.creditLimit),
      backgroundColor: 'rgba(29, 161, 242, 0.6)',
      borderRadius: 4
    },
    {
      label: 'Deuda',
      data: cards.map(c => c.debt),
      backgroundColor: 'rgba(239, 68, 68, 0.6)',
      borderRadius: 4
    },
    {
      label: 'Disponible',
      data: cards.map(c => c.available),
      backgroundColor: 'rgba(16, 185, 129, 0.6)',
      borderRadius: 4
    }
  ]
}

const barOptions = {
  responsive: true,
  plugins: {
    legend: {
      labels: { color: '#8899a6' }
    }
  },
  scales: {
    x: {
      ticks: { color: '#8899a6' },
      grid: { color: '#2d3741' }
    },
    y: {
      ticks: { color: '#8899a6' },
      grid: { color: '#2d3741' }
    }
  }
}

function formatDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function daysUntilPayment(dateStr) {
  const today = new Date()
  const payment = new Date(dateStr + 'T00:00:00')
  const diff = Math.ceil((payment - today) / (1000 * 60 * 60 * 24))
  return diff > 0 ? diff : 0
}

function getUsageClass(percent) {
  if (percent >= 70) return 'high'
  if (percent >= 40) return 'medium'
  return 'low'
}
</script>

<style scoped>
.creditos {
  max-width: 1200px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #e1e8ed;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.stat-icon.credit {
  background-color: rgba(29, 161, 242, 0.15);
  color: #1da1f2;
}

.stat-icon.debt {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.stat-icon.available {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.stat-icon.usage {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.8rem;
  color: #8899a6;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #e1e8ed;
}

/* Charts */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.chart-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 24px;
}

.chart-card h3 {
  font-size: 1rem;
  color: #e1e8ed;
  margin-bottom: 16px;
}

/* Cards Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.credit-card-item {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-top: 3px solid;
  border-radius: 12px;
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-brand {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.card-name-section h3 {
  color: #e1e8ed;
  font-size: 1.1rem;
  margin: 0;
}

.card-subtitle {
  color: #8899a6;
  font-size: 0.75rem;
}

.card-usage-bar {
  margin-bottom: 16px;
}

.usage-bar-bg {
  height: 6px;
  background-color: #2d3741;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.usage-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.usage-text {
  font-size: 0.7rem;
  color: #8899a6;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.detail-row.separator {
  border-top: 1px solid #2d3741;
  margin-top: 4px;
  padding-top: 12px;
}

.detail-label {
  color: #8899a6;
  font-size: 0.82rem;
}

.detail-value {
  color: #e1e8ed;
  font-size: 0.9rem;
  font-weight: 600;
}

.debt-color {
  color: #ef4444;
}

.available-color {
  color: #10b981;
}

.highlight {
  color: #f59e0b;
}

.card-countdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background-color: #192734;
  border-radius: 8px;
  color: #8899a6;
  font-size: 0.8rem;
}

.card-countdown i {
  color: #f59e0b;
}

/* Tabla */
.table-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 24px;
  overflow-x: auto;
}

.table-card h3 {
  color: #e1e8ed;
  margin-bottom: 16px;
  font-size: 1rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #8899a6;
  border-bottom: 1px solid #2d3741;
  background-color: #192734;
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #2d3741;
  color: #e1e8ed;
  font-size: 0.85rem;
}

.data-table tr:hover td {
  background-color: #1c2b3a;
}

.totals-row td {
  background-color: #192734;
  border-top: 2px solid #2d3741;
}

.table-card-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.usage-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.usage-badge.low {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.usage-badge.medium {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.usage-badge.high {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
