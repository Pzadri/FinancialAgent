<template>
  <div class="dashboard">
    <h1 class="page-title">Dashboard Financiero</h1>

    <!-- Resumen Principal -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon patrimony"><i class="pi pi-building"></i></div>
        <div class="stat-info">
          <span class="stat-label">Patrimonio Neto</span>
          <span class="stat-value">${{ patrimony.toLocaleString() }}</span>
          <span class="stat-sub income">Activos - Deudas</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon income-icon"><i class="pi pi-arrow-up"></i></div>
        <div class="stat-info">
          <span class="stat-label">Ingresos (mes)</span>
          <span class="stat-value">${{ monthlyIncome.toLocaleString() }}</span>
          <span class="stat-sub income">+12% vs mes anterior</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon expense-icon"><i class="pi pi-arrow-down"></i></div>
        <div class="stat-info">
          <span class="stat-label">Gastos (mes)</span>
          <span class="stat-value">${{ monthlyExpenses.toLocaleString() }}</span>
          <span class="stat-sub expense">+5% vs mes anterior</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon savings-icon"><i class="pi pi-percentage"></i></div>
        <div class="stat-info">
          <span class="stat-label">Tasa de Ahorro</span>
          <span class="stat-value">{{ savingsRate }}%</span>
          <span class="stat-sub">Meta: 30%</span>
        </div>
      </div>
    </div>

    <!-- Fila 2: Créditos + Inversiones resumen -->
    <div class="row-2">
      <div class="card credit-summary">
        <div class="card-header">
          <h3>Tarjetas de Crédito</h3>
          <router-link to="/creditos" class="card-link">Ver detalle →</router-link>
        </div>
        <div class="credit-bars">
          <div v-for="card in creditCards" :key="card.name" class="credit-bar-item">
            <div class="credit-bar-info">
              <span class="credit-bar-name" :style="{ color: card.color }">{{ card.name }}</span>
              <span class="credit-bar-amount">${{ card.debt.toLocaleString() }} / ${{ card.limit.toLocaleString() }}</span>
            </div>
            <div class="credit-bar-bg">
              <div class="credit-bar-fill" :style="{ width: card.usage + '%', backgroundColor: card.color }"></div>
            </div>
          </div>
        </div>
        <div class="credit-totals">
          <div class="credit-total-item">
            <span class="ct-label">Deuda Total</span>
            <span class="ct-value expense">${{ totalCreditDebt.toLocaleString() }}</span>
          </div>
          <div class="credit-total-item">
            <span class="ct-label">Disponible</span>
            <span class="ct-value income">${{ totalCreditAvailable.toLocaleString() }}</span>
          </div>
        </div>

        <div class="payments-section">
          <h4>Próximos Pagos</h4>
          <div class="payments-list">
            <div v-for="payment in upcomingPayments" :key="payment.name" class="payment-item">
              <div class="payment-icon" :style="{ backgroundColor: payment.color + '20', color: payment.color }">
                <i class="pi pi-credit-card"></i>
              </div>
              <div class="payment-info">
                <span class="payment-name">{{ payment.name }}</span>
                <span class="payment-date">{{ payment.date }}</span>
              </div>
              <div class="payment-right">
                <span class="payment-amount">${{ payment.amount.toLocaleString() }}</span>
                <span class="payment-days">{{ payment.daysLeft }} días</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card investments-summary">
        <div class="card-header">
          <h3>Inversiones</h3>
          <router-link to="/inversiones" class="card-link">Ver detalle →</router-link>
        </div>
        <div class="inv-breakdown">
          <div class="inv-item">
            <div class="inv-icon" style="background-color: rgba(0, 117, 235, 0.15); color: #0075eb;">
              <i class="pi pi-wallet"></i>
            </div>
            <div class="inv-info">
              <span class="inv-name">Ahorro (Revolut + Didi + Nu)</span>
              <span class="inv-amount">${{ totalSavings.toLocaleString() }}</span>
            </div>
            <span class="inv-rate income">~14.3% anual</span>
          </div>
          <div class="inv-item">
            <div class="inv-icon" style="background-color: rgba(245, 158, 11, 0.15); color: #f59e0b;">
              <i class="pi pi-users"></i>
            </div>
            <div class="inv-info">
              <span class="inv-name">Préstamos (Yo Te Presto)</span>
              <span class="inv-amount">${{ totalLoans.toLocaleString() }}</span>
            </div>
            <span class="inv-rate income">~11.3% prom</span>
          </div>
          <div class="inv-item">
            <div class="inv-icon" style="background-color: rgba(139, 92, 246, 0.15); color: #8b5cf6;">
              <i class="pi pi-chart-line"></i>
            </div>
            <div class="inv-info">
              <span class="inv-name">GBM (Acciones + ETFs)</span>
              <span class="inv-amount">${{ gbmTotal.toLocaleString() }}</span>
            </div>
            <span class="inv-rate income">+9.2%</span>
          </div>
          <div class="inv-item">
            <div class="inv-icon" style="background-color: rgba(29, 161, 242, 0.15); color: #1da1f2;">
              <i class="pi pi-shield"></i>
            </div>
            <div class="inv-info">
              <span class="inv-name">Afore</span>
              <span class="inv-amount">${{ afore.toLocaleString() }}</span>
            </div>
            <span class="inv-rate">9.5% anual</span>
          </div>
        </div>
        <div class="inv-total">
          <span>Portafolio Total</span>
          <strong>${{ totalPortfolio.toLocaleString() }}</strong>
        </div>

        <div class="daily-earnings">
          <h4>Ganancias Diarias por Intereses</h4>
          <div class="earnings-row">
            <span>Revolut</span><span class="income">+${{ (28500 * 0.15 / 365).toFixed(2) }}</span>
          </div>
          <div class="earnings-row">
            <span>Didi</span><span class="income">+${{ (42000 * 0.15 / 365).toFixed(2) }}</span>
          </div>
          <div class="earnings-row">
            <span>Cajita Nu</span><span class="income">+${{ (18700 * 0.13 / 365).toFixed(2) }}</span>
          </div>
          <div class="earnings-row total">
            <span>Total diario</span><span class="income">+${{ dailyEarnings.toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Fila 3: Gráficas -->
    <div class="row-3">
      <div class="card">
        <h3>Ingresos vs Gastos (6 meses)</h3>
        <Line :data="lineChartData" :options="chartOptions" />
      </div>
      <div class="card">
        <h3>Distribución de Gastos</h3>
        <Doughnut :data="doughnutData" :options="doughnutOptions" />
      </div>
    </div>

    <!-- Fila 4: Últimos movimientos -->
    <div class="row-4">
      <div class="card full-width">
        <div class="card-header">
          <h3>Últimos Movimientos</h3>
          <router-link to="/gastos-ingresos" class="card-link">Ver todos →</router-link>
        </div>
        <div class="movements-list">
          <div v-for="tx in recentTransactions" :key="tx.id" class="movement-item">
            <div class="movement-icon" :class="tx.amount > 0 ? 'mov-income' : 'mov-expense'">
              <i :class="tx.amount > 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down'"></i>
            </div>
            <div class="movement-info">
              <span class="movement-desc">{{ tx.description }}</span>
              <span class="movement-meta">{{ tx.category }} · {{ tx.date }}</span>
            </div>
            <span class="movement-amount" :class="tx.amount > 0 ? 'income' : 'expense'">
              {{ tx.amount > 0 ? '+' : '' }}${{ Math.abs(tx.amount).toLocaleString() }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler)

// Datos financieros
const monthlyIncome = 530000
const monthlyExpenses = 320000
const savingsRate = computed(() => Math.round(((monthlyIncome - monthlyExpenses) / monthlyIncome) * 100))

// Créditos
const creditCards = [
  { name: 'Nu', color: '#820ad1', debt: 18500, limit: 45000, usage: 41 },
  { name: 'Didi', color: '#ff6600', debt: 12800, limit: 32000, usage: 40 },
  { name: 'Stori', color: '#00c389', debt: 9200, limit: 25000, usage: 37 }
]
const totalCreditDebt = computed(() => creditCards.reduce((s, c) => s + c.debt, 0))
const totalCreditAvailable = computed(() => creditCards.reduce((s, c) => s + (c.limit - c.debt), 0))

// Inversiones
const totalSavings = 89200
const totalLoans = 28000
const gbmTotal = 92525
const afore = 85000
const totalPortfolio = computed(() => totalSavings + totalLoans + gbmTotal + afore)

// Patrimonio neto = inversiones - deudas
const patrimony = computed(() => totalPortfolio.value - totalCreditDebt.value)

// Ganancias diarias
const dailyEarnings = (28500 * 0.15 / 365) + (42000 * 0.15 / 365) + (18700 * 0.13 / 365)

// Últimos movimientos
const recentTransactions = [
  { id: 1, description: 'Salario', category: 'Ingreso', date: '20 May', amount: 450000 },
  { id: 2, description: 'Alquiler', category: 'Vivienda', date: '18 May', amount: -120000 },
  { id: 3, description: 'Supermercado', category: 'Alimentación', date: '17 May', amount: -35000 },
  { id: 4, description: 'Freelance', category: 'Ingreso', date: '15 May', amount: 80000 },
  { id: 5, description: 'Netflix', category: 'Entretenimiento', date: '14 May', amount: -5000 }
]

// Próximos pagos
const upcomingPayments = [
  { name: 'Didi Card', color: '#ff6600', date: '12 Jun 2026', amount: 12800, daysLeft: 23 },
  { name: 'Stori Card', color: '#00c389', date: '16 Jun 2026', amount: 9200, daysLeft: 27 },
  { name: 'Nu Card', color: '#820ad1', date: '18 Jun 2026', amount: 18500, daysLeft: 29 }
]

// Gráfica Ingresos vs Gastos
const lineChartData = {
  labels: ['Dic', 'Ene', 'Feb', 'Mar', 'Abr', 'May'],
  datasets: [
    {
      label: 'Ingresos',
      data: [420000, 450000, 470000, 460000, 490000, 530000],
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      fill: true,
      tension: 0.4
    },
    {
      label: 'Gastos',
      data: [290000, 310000, 300000, 330000, 305000, 320000],
      borderColor: '#ef4444',
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
      fill: true,
      tension: 0.4
    }
  ]
}

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { labels: { color: '#8899a6' } }
  },
  scales: {
    x: { ticks: { color: '#8899a6' }, grid: { color: '#2d3741' } },
    y: { ticks: { color: '#8899a6' }, grid: { color: '#2d3741' } }
  }
}

const doughnutData = {
  labels: ['Vivienda', 'Alimentación', 'Transporte', 'Entretenimiento', 'Servicios', 'Otros'],
  datasets: [{
    data: [120000, 47000, 60000, 17000, 26000, 50000],
    backgroundColor: ['#1da1f2', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280']
  }]
}

const doughnutOptions = {
  responsive: true,
  plugins: {
    legend: { position: 'bottom', labels: { color: '#8899a6' } }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #e1e8ed;
}

/* Stats Grid */
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

.stat-icon.patrimony { background-color: rgba(29, 161, 242, 0.15); color: #1da1f2; }
.stat-icon.income-icon { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }
.stat-icon.expense-icon { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; }
.stat-icon.savings-icon { background-color: rgba(139, 92, 246, 0.15); color: #8b5cf6; }

.stat-info { display: flex; flex-direction: column; }
.stat-label { font-size: 0.8rem; color: #8899a6; margin-bottom: 4px; }
.stat-value { font-size: 1.3rem; font-weight: 700; color: #e1e8ed; }
.stat-sub { font-size: 0.7rem; color: #8899a6; margin-top: 2px; }
.stat-sub.income { color: #10b981; }
.stat-sub.expense { color: #ef4444; }

/* Cards */
.card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 20px;
}

.card h3 {
  color: #e1e8ed;
  font-size: 1rem;
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 { margin-bottom: 0; }

.card-link {
  color: #1da1f2;
  font-size: 0.8rem;
  text-decoration: none;
  font-weight: 600;
}

.card-link:hover { text-decoration: underline; }

/* Row 2 */
.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

/* Credit Summary */
.credit-bars { margin-bottom: 16px; }

.credit-bar-item { margin-bottom: 12px; }

.credit-bar-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.credit-bar-name { font-size: 0.85rem; font-weight: 600; }
.credit-bar-amount { font-size: 0.75rem; color: #8899a6; }

.credit-bar-bg {
  height: 6px;
  background-color: #2d3741;
  border-radius: 3px;
  overflow: hidden;
}

.credit-bar-fill {
  height: 100%;
  border-radius: 3px;
}

.credit-totals {
  display: flex;
  gap: 20px;
  padding-top: 12px;
  border-top: 1px solid #2d3741;
}

.credit-total-item { display: flex; flex-direction: column; gap: 2px; }
.ct-label { font-size: 0.7rem; color: #8899a6; }
.ct-value { font-size: 0.9rem; font-weight: 700; color: #e1e8ed; }
.ct-value.expense { color: #ef4444; }
.ct-value.income { color: #10b981; }
.ct-value.highlight { color: #f59e0b; }

/* Investments Summary */
.inv-breakdown { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }

.inv-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 8px;
  background-color: #192734;
}

.inv-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.inv-info { flex: 1; display: flex; flex-direction: column; }
.inv-name { font-size: 0.8rem; color: #8899a6; }
.inv-amount { font-size: 0.9rem; font-weight: 600; color: #e1e8ed; }
.inv-rate { font-size: 0.75rem; font-weight: 600; }

.inv-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background-color: #192734;
  border-radius: 8px;
  color: #8899a6;
  font-size: 0.85rem;
}

.inv-total strong { color: #e1e8ed; font-size: 1.1rem; }

/* Row 3 */
.row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

/* Row 4 */
.row-4 {
  margin-top: 0;
}

.full-width {
  width: 100%;
}

/* Movements */
.movements-list { display: flex; flex-direction: column; gap: 8px; }

.movement-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 8px;
  background-color: #192734;
}

.movement-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.mov-income { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }
.mov-expense { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; }

.movement-info { flex: 1; display: flex; flex-direction: column; }
.movement-desc { font-size: 0.85rem; color: #e1e8ed; }
.movement-meta { font-size: 0.7rem; color: #8899a6; }
.movement-amount { font-size: 0.9rem; font-weight: 700; }

/* Payments section inside credit card */
.payments-section {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #2d3741;
}

.payments-section h4 {
  color: #8899a6;
  font-size: 0.8rem;
  text-transform: uppercase;
  margin-bottom: 10px;
}

/* Payments */
.payments-list { display: flex; flex-direction: column; gap: 8px; }

.payment-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 8px;
  background-color: #192734;
}

.payment-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
}

.payment-info { flex: 1; display: flex; flex-direction: column; }
.payment-name { font-size: 0.85rem; color: #e1e8ed; font-weight: 600; }
.payment-date { font-size: 0.7rem; color: #8899a6; }

.payment-right { display: flex; flex-direction: column; align-items: flex-end; }
.payment-amount { font-size: 0.9rem; font-weight: 700; color: #f59e0b; }
.payment-days { font-size: 0.7rem; color: #8899a6; }

/* Daily Earnings */
.daily-earnings {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #2d3741;
}

.daily-earnings h4 {
  color: #8899a6;
  font-size: 0.8rem;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.earnings-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 0.82rem;
  color: #8899a6;
}

.earnings-row.total {
  border-top: 1px solid #2d3741;
  margin-top: 4px;
  padding-top: 8px;
  color: #e1e8ed;
  font-weight: 600;
}

.income { color: #10b981; font-weight: 600; }
.expense { color: #ef4444; font-weight: 600; }
.highlight { color: #f59e0b; }

@media (max-width: 768px) {
  .row-2, .row-3, .row-4 {
    grid-template-columns: 1fr;
  }
}
</style>
