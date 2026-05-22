<template>
  <div class="inversiones">
    <h1 class="page-title">Inversiones</h1>

    <!-- Resumen Total -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon portfolio"><i class="pi pi-briefcase"></i></div>
        <div class="stat-info">
          <span class="stat-label">Portafolio Total</span>
          <span class="stat-value">${{ totalPortfolio.toLocaleString() }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon savings"><i class="pi pi-wallet"></i></div>
        <div class="stat-info">
          <span class="stat-label">Liquidez</span>
          <span class="stat-value">${{ liquidez.toLocaleString() }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon savings"><i class="pi pi-wallet"></i></div>
        <div class="stat-info">
          <span class="stat-label">Ingreso Diario</span>
          <span class="stat-value">+${{ dailyIncomeRevolutNu.toFixed(2) }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon market"><i class="pi pi-chart-line"></i></div>
        <div class="stat-info">
          <span class="stat-label">Ingreso Congelado</span>
          <span class="stat-value">${{ frozenIncome.toLocaleString() }}</span>
        </div>
      </div>
    </div>

    <!-- Tabs de secciones -->
    <div class="section-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <i :class="tab.icon"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- SECCIÓN: CUENTAS DE AHORRO -->
    <div v-if="activeTab === 'savings'" class="section-content">
      <div class="savings-cards">
        <div v-for="account in savingsAccounts" :key="account.name" class="savings-card" :style="{ borderTopColor: account.color }">
          <div class="savings-header">
            <div class="savings-brand" :style="{ backgroundColor: account.color + '20', color: account.color }">
              <i class="pi pi-wallet"></i>
            </div>
            <div>
              <h3>{{ account.name }}</h3>
              <span class="savings-subtitle">{{ account.description }}</span>
            </div>
          </div>

          <div class="savings-balance">
            <span class="balance-label">Saldo Actual</span>
            <span class="balance-value">${{ account.balance.toLocaleString() }}</span>
          </div>

          <div class="savings-rate">
            <span class="rate-badge" :style="{ backgroundColor: account.color + '20', color: account.color }">
              {{ account.annualRate }}% anual
            </span>
            <span class="daily-gain">+${{ account.dailyGain.toFixed(2) }}/día</span>
          </div>

          <!-- Selector de periodo -->
          <div class="period-selector">
            <button
              v-for="period in periods"
              :key="period.key"
              class="period-btn"
              :class="{ active: account.selectedPeriod === period.key }"
              @click="account.selectedPeriod = period.key"
            >
              {{ period.label }}
            </button>
          </div>

          <!-- Gráfica de interés compuesto -->
          <div class="chart-container">
            <Line :data="getCompoundChart(account)" :options="lineOptions" />
          </div>

          <div class="projection-summary">
            <div class="proj-item">
              <span class="proj-label">Proyección</span>
              <span class="proj-value income">${{ getProjection(account).toLocaleString(undefined, { maximumFractionDigits: 0 }) }}</span>
            </div>
            <div class="proj-item">
              <span class="proj-label">Ganancia</span>
              <span class="proj-value income">+${{ (getProjection(account) - account.balance).toLocaleString(undefined, { maximumFractionDigits: 0 }) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- SECCIÓN: PRÉSTAMOS -->
    <div v-if="activeTab === 'loans'" class="section-content">
      <div class="loans-header-info">
        <h2>Yo Te Presto</h2>
        <p class="section-desc">Préstamos activos con diferentes tasas de retorno</p>
      </div>

      <div class="loans-summary">
        <div class="loan-stat">
          <span class="loan-stat-label">Capital Prestado</span>
          <span class="loan-stat-value">${{ totalLoans.toLocaleString() }}</span>
        </div>
        <div class="loan-stat">
          <span class="loan-stat-label">Intereses Esperados</span>
          <span class="loan-stat-value income">+${{ totalLoanInterest.toLocaleString() }}</span>
        </div>
        <div class="loan-stat">
          <span class="loan-stat-label">Retorno Promedio</span>
          <span class="loan-stat-value">{{ avgLoanRate }}%</span>
        </div>
      </div>

      <div class="table-card">
        <table class="data-table">
          <thead>
            <tr>
              <th>Capital</th>
              <th>Tasa</th>
              <th>Plazo</th>
              <th>Interés Esperado</th>
              <th>Retorno Total</th>
              <th>Estado</th>
              <th>Vencimiento</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="loan in loans" :key="loan.id">
              <td>${{ loan.principal.toLocaleString() }}</td>
              <td><span class="rate-badge-sm">{{ loan.rate }}%</span></td>
              <td>{{ loan.term }}</td>
              <td class="income">+${{ loan.expectedInterest.toLocaleString() }}</td>
              <td>${{ loan.totalReturn.toLocaleString() }}</td>
              <td><span class="status-badge" :class="loan.status">{{ loan.statusLabel }}</span></td>
              <td>{{ formatDate(loan.dueDate) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- SECCIÓN: AFORE -->
    <div v-if="activeTab === 'afore'" class="section-content">
      <div class="afore-card">
        <div class="afore-header">
          <div class="afore-brand"><i class="pi pi-shield"></i></div>
          <div>
            <h2>Afore</h2>
            <span class="section-desc">Cuenta de retiro</span>
          </div>
        </div>

        <div class="afore-stats">
          <div class="afore-stat">
            <span class="afore-stat-label">Saldo Acumulado</span>
            <span class="afore-stat-value">${{ afore.balance.toLocaleString() }}</span>
          </div>
          <div class="afore-stat">
            <span class="afore-stat-label">Rendimiento Anual</span>
            <span class="afore-stat-value income">{{ afore.annualReturn }}%</span>
          </div>
          <div class="afore-stat">
            <span class="afore-stat-label">Aportación Bimestral</span>
            <span class="afore-stat-value">${{ afore.bimonthlyContribution.toLocaleString() }}</span>
          </div>
          <div class="afore-stat">
            <span class="afore-stat-label">Aportación Voluntaria</span>
            <span class="afore-stat-value">${{ afore.voluntaryContribution.toLocaleString() }}/semana</span>
          </div>
        </div>

        <div class="chart-container">
          <Line :data="aforeChartData" :options="lineOptions" />
        </div>

        <div class="afore-projection">
          <p>Proyección a 30 años con aportaciones actuales: <strong class="income">${{ aforeProjection30.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}</strong></p>
        </div>
      </div>
    </div>

    <!-- SECCIÓN: GBM -->
    <div v-if="activeTab === 'gbm'" class="section-content">
      <div class="gbm-header-info">
        <h2>GBM - Inversiones</h2>
        <p class="section-desc">Portafolio de inversiones nacionales e internacionales (datos desde Excel)</p>
      </div>

      <div v-if="gbmLoading" class="loading-state">
        <i class="pi pi-spin pi-spinner"></i> Cargando portafolio...
      </div>

      <div v-else>
        <div class="gbm-summary">
          <div class="gbm-stat">
            <span class="gbm-stat-label">Valor Total (MXN)</span>
            <span class="gbm-stat-value">${{ gbmSummary.totalValueMXN.toLocaleString(undefined, { maximumFractionDigits: 2 }) }}</span>
          </div>
          <div class="gbm-stat">
            <span class="gbm-stat-label">Nacional (MXN)</span>
            <span class="gbm-stat-value">${{ gbmSummary.nacionalValueMXN.toLocaleString(undefined, { maximumFractionDigits: 2 }) }}</span>
          </div>
          <div class="gbm-stat">
            <span class="gbm-stat-label">USA (USD)</span>
            <span class="gbm-stat-value">${{ gbmSummary.usaValueUSD.toLocaleString(undefined, { maximumFractionDigits: 2 }) }}</span>
          </div>
          <div class="gbm-stat">
            <span class="gbm-stat-label">Rendimiento Total</span>
            <span class="gbm-stat-value" :class="gbmSummary.totalReturnPct >= 0 ? 'income' : 'expense'">
              {{ gbmSummary.totalReturnPct >= 0 ? '+' : '' }}{{ gbmSummary.totalReturnPct.toFixed(2) }}%
            </span>
          </div>
          <div class="gbm-stat">
            <span class="gbm-stat-label">TC USD/MXN</span>
            <span class="gbm-stat-value">${{ gbmSummary.usdMxnRate }}</span>
          </div>
        </div>

        <!-- Gráficas -->
        <div class="charts-grid">
          <div class="chart-card">
            <h3>Distribución del Portafolio</h3>
            <Doughnut :data="gbmDistributionData" :options="doughnutOptions" />
          </div>
          <div class="chart-card">
            <h3>Rendimiento por Instrumento (%)</h3>
            <Bar :data="gbmPerformanceData" :options="barOptions" />
            <div class="performance-cash-chart">
              <h4>Rendimiento en Efectivo ($)</h4>
              <Bar :data="gbmCashPerformanceData" :options="barOptions" />
            </div>
          </div>
        </div>

        <!-- Tabla Nacional -->
        <div class="table-card">
          <h3>Mercado Nacional (MXN)</h3>
          <table class="data-table">
            <thead>
              <tr>
                <th>Emisora</th>
                <th>Títulos</th>
                <th>Costo Prom.</th>
                <th>Precio Mercado</th>
                <th>Valor Mercado</th>
                <th>+/- $</th>
                <th>Rendimiento %</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inv in gbmNacional" :key="inv.ticker">
                <td><span class="ticker-name">{{ inv.ticker }}</span></td>
                <td>{{ inv.shares }}</td>
                <td>${{ inv.avgCost.toFixed(2) }}</td>
                <td>${{ inv.marketPrice.toFixed(2) }}</td>
                <td>${{ inv.marketValue.toFixed(2) }}</td>
                <td :class="inv.gainLoss >= 0 ? 'income' : 'expense'">
                  {{ inv.gainLoss >= 0 ? '+' : '' }}${{ inv.gainLoss.toFixed(2) }}
                </td>
                <td :class="inv.returnPct >= 0 ? 'income' : 'expense'">
                  {{ inv.returnPct >= 0 ? '+' : '' }}{{ inv.returnPct.toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Tabla USA -->
        <div class="table-card">
          <h3>Mercado USA (USD)</h3>
          <table class="data-table">
            <thead>
              <tr>
                <th>Emisora</th>
                <th>Títulos</th>
                <th>Costo Prom.</th>
                <th>Precio Mercado</th>
                <th>Valor (USD)</th>
                <th>+/- $</th>
                <th>Rendimiento %</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inv in gbmUSA" :key="inv.ticker">
                <td><span class="ticker-name">{{ inv.ticker }}</span></td>
                <td>{{ inv.shares.toFixed(8) }}</td>
                <td>${{ inv.avgCost.toFixed(2) }}</td>
                <td>${{ inv.marketPrice.toFixed(2) }}</td>
                <td>${{ inv.marketValue.toFixed(2) }}</td>
                <td :class="inv.gainLoss >= 0 ? 'income' : 'expense'">
                  {{ inv.gainLoss >= 0 ? '+' : '' }}${{ inv.gainLoss.toFixed(2) }}
                </td>
                <td :class="inv.returnPct >= 0 ? 'income' : 'expense'">
                  {{ inv.returnPct >= 0 ? '+' : '' }}{{ inv.returnPct.toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { Line, Doughnut, Bar } from 'vue-chartjs'
import axios from 'axios'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler)

const activeTab = ref('savings')

const tabs = [
  { id: 'savings', label: 'Ahorro', icon: 'pi pi-wallet' },
  { id: 'loans', label: 'Préstamos', icon: 'pi pi-users' },
  { id: 'afore', label: 'Afore', icon: 'pi pi-shield' },
  { id: 'gbm', label: 'GBM', icon: 'pi pi-chart-line' }
]

const periods = [
  { key: '1w', label: '1S', days: 7 },
  { key: '1m', label: '1M', days: 30 },
  { key: '3m', label: '3M', days: 90 },
  { key: '6m', label: '6M', days: 180 },
  { key: '1y', label: '1A', days: 365 },
  { key: '5y', label: '5A', days: 1825 },
  { key: '10y', label: '10A', days: 3650 }
]

// ===== CUENTAS DE AHORRO =====
const savingsAccounts = reactive([])

// ===== PRÉSTAMOS =====
const loans = ref([])
const totalLoans = ref(0)
const totalLoanInterest = ref(0)
const avgLoanRate = ref(0)

// ===== AFORE =====
const afore = reactive({
  balance: 0,
  annualReturn: 0,
  bimonthlyContribution: 0,
  voluntaryContribution: 0
})

function getCompoundData(balance, annualRate, periodKey) {
  const period = periods.find(p => p.key === periodKey)
  const days = period.days
  const dailyRate = annualRate / 100 / 365
  const points = []
  const labels = []

  let numPoints
  if (days <= 7) numPoints = 7
  else if (days <= 30) numPoints = 30
  else if (days <= 90) numPoints = 12
  else if (days <= 180) numPoints = 12
  else if (days <= 365) numPoints = 12
  else numPoints = 20

  for (let i = 0; i <= numPoints; i++) {
    const dayAt = Math.round((days / numPoints) * i)
    const value = balance * Math.pow(1 + dailyRate, dayAt)
    points.push(Math.round(value * 100) / 100)

    if (days <= 7) labels.push(`Día ${i}`)
    else if (days <= 30) labels.push(`Día ${dayAt}`)
    else if (days <= 365) labels.push(`Mes ${Math.round(dayAt / 30)}`)
    else labels.push(`Año ${(dayAt / 365).toFixed(1)}`)
  }

  return { points, labels }
}

function getCompoundChart(account) {
  const data = getCompoundData(account.balance, account.annualRate, account.selectedPeriod)
  return {
    labels: data.labels,
    datasets: [{
      label: 'Saldo Proyectado',
      data: data.points,
      borderColor: account.color,
      backgroundColor: account.color + '20',
      fill: true,
      tension: 0.4,
      pointRadius: 2
    }]
  }
}

function getProjection(account) {
  const period = periods.find(p => p.key === account.selectedPeriod)
  const dailyRate = account.annualRate / 100 / 365
  return account.balance * Math.pow(1 + dailyRate, period.days)
}

const lineOptions = {
  responsive: true,
  plugins: {
    legend: { display: false }
  },
  scales: {
    x: {
      ticks: { color: '#8899a6', maxTicksLimit: 8 },
      grid: { color: '#2d3741' }
    },
    y: {
      ticks: { color: '#8899a6' },
      grid: { color: '#2d3741' }
    }
  }
}

// (loans loaded from API)

// ===== AFORE (chart computeds) =====

const aforeChartData = computed(() => {
  const labels = []
  const data = []
  let balance = afore.balance
  const monthlyRate = afore.annualReturn / 100 / 12
  const monthlyContrib = afore.bimonthlyContribution / 2 + (afore.voluntaryContribution * 4.33)

  for (let year = 0; year <= 30; year += 5) {
    labels.push(`Año ${year}`)
    data.push(Math.round(balance))
    for (let m = 0; m < 60 && year < 30; m++) {
      balance = balance * (1 + monthlyRate) + monthlyContrib
    }
  }

  return {
    labels,
    datasets: [{
      label: 'Saldo Afore',
      data,
      borderColor: '#1da1f2',
      backgroundColor: 'rgba(29, 161, 242, 0.1)',
      fill: true,
      tension: 0.4
    }]
  }
})

const aforeProjection30 = computed(() => {
  let balance = afore.balance
  const monthlyRate = afore.annualReturn / 100 / 12
  const monthlyContrib = afore.bimonthlyContribution / 2 + (afore.voluntaryContribution * 4.33)
  for (let m = 0; m < 360; m++) {
    balance = balance * (1 + monthlyRate) + monthlyContrib
  }
  return balance
})

// ===== GBM (from API) =====
const gbmLoading = ref(true)
const gbmNacional = ref([])
const gbmUSA = ref([])
const gbmSummary = ref({
  nacionalValueMXN: 0,
  usaValueUSD: 0,
  usaValueMXN: 0,
  totalValueMXN: 0,
  totalGainMXN: 0,
  totalReturnPct: 0,
  usdMxnRate: 19.45
})

const gbmColors = ['#1da1f2', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1', '#14b8a6', '#e11d48', '#a855f7']

const gbmDistributionData = computed(() => {
  const allInstruments = [...gbmNacional.value, ...gbmUSA.value]
  return {
    labels: allInstruments.map(i => i.ticker),
    datasets: [{
      data: allInstruments.map(i => i.marketValue),
      backgroundColor: allInstruments.map((_, idx) => gbmColors[idx % gbmColors.length]),
      borderWidth: 0
    }]
  }
})

const gbmPerformanceData = computed(() => {
  const allInstruments = [...gbmNacional.value, ...gbmUSA.value].filter(i => i.returnPct !== 0)
  return {
    labels: allInstruments.map(i => i.ticker),
    datasets: [{
      label: 'Rendimiento %',
      data: allInstruments.map(i => i.returnPct),
      backgroundColor: allInstruments.map(i => i.returnPct >= 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'),
      borderRadius: 4
    }]
  }
})

const allGbmInstruments = computed(() => [...gbmNacional.value, ...gbmUSA.value].filter(i => i.gainLoss !== 0))

const gbmCashPerformanceData = computed(() => {
  const instruments = allGbmInstruments.value
  return {
    labels: instruments.map(i => i.ticker),
    datasets: [{
      label: 'Rendimiento $',
      data: instruments.map(i => i.gainLoss),
      backgroundColor: instruments.map(i => i.gainLoss >= 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'),
      borderRadius: 4
    }]
  }
})

async function loadGBMData() {
  try {
    const response = await axios.get('/api/gbm/portfolio')
    gbmNacional.value = response.data.nacional
    gbmUSA.value = response.data.usa
    gbmSummary.value = response.data.summary
  } catch (error) {
    console.error('Error loading GBM data:', error)
  } finally {
    gbmLoading.value = false
  }
}

async function loadInversiones() {
  try {
    const response = await axios.get('/api/inversiones')
    const data = response.data

    // Ahorro
    data.ahorro.forEach(a => {
      savingsAccounts.push({ ...a, selectedPeriod: '1m' })
    })

    // Préstamos
    loans.value = data.prestamos
    totalLoans.value = data.summary.totalLoans
    totalLoanInterest.value = data.summary.totalLoanInterest
    avgLoanRate.value = data.summary.avgLoanRate

    // Afore
    Object.assign(afore, data.afore)
  } catch (error) {
    console.error('Error loading inversiones data:', error)
  }
}

onMounted(() => {
  loadGBMData()
  loadInversiones()
})

const doughnutOptions = {
  responsive: true,
  plugins: {
    legend: { position: 'bottom', labels: { color: '#8899a6', padding: 12 } }
  }
}

const barOptions = {
  responsive: true,
  plugins: {
    legend: { display: false }
  },
  scales: {
    x: { ticks: { color: '#8899a6' }, grid: { color: '#2d3741' } },
    y: { ticks: { color: '#8899a6' }, grid: { color: '#2d3741' } }
  }
}

// ===== TOTALES =====
const dailyIncomeRevolutNu = computed(() => {
  const revolut = savingsAccounts.find(a => a.name === 'Revolut')
  const nu = savingsAccounts.find(a => a.name === 'Cajita Nu')
  return (revolut ? revolut.dailyGain : 0) + (nu ? nu.dailyGain : 0)
})
const liquidez = computed(() => {
  const revolut = savingsAccounts.find(a => a.name === 'Revolut')
  const nu = savingsAccounts.find(a => a.name === 'Cajita Nu')
  return (revolut ? revolut.balance : 0) + (nu ? nu.balance : 0)
})
const totalSavings = computed(() => savingsAccounts.reduce((s, a) => s + a.balance, 0))
const totalMarket = computed(() => gbmSummary.value.totalValueMXN + afore.balance)
const frozenIncome = computed(() => gbmSummary.value.totalValueMXN + afore.balance + totalLoans.value)
const totalPortfolio = computed(() => totalSavings.value + totalLoans.value + totalMarket.value)

function formatDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.inversiones {
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

.stat-icon.portfolio { background-color: rgba(29, 161, 242, 0.15); color: #1da1f2; }
.stat-icon.savings { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }
.stat-icon.loans { background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.stat-icon.market { background-color: rgba(139, 92, 246, 0.15); color: #8b5cf6; }

.stat-info { display: flex; flex-direction: column; }
.stat-label { font-size: 0.8rem; color: #8899a6; margin-bottom: 4px; }
.stat-value { font-size: 1.3rem; font-weight: 700; color: #e1e8ed; }

/* Tabs */
.section-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 10px;
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: #8899a6;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.tab-btn:hover { color: #e1e8ed; }
.tab-btn.active { background-color: #1da1f2; color: white; }

/* Savings Cards */
.savings-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
}

.savings-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-top: 3px solid;
  border-radius: 12px;
  padding: 20px;
}

.savings-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.savings-brand {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.savings-header h3 { color: #e1e8ed; margin: 0; font-size: 1.1rem; }
.savings-subtitle { color: #8899a6; font-size: 0.75rem; }

.savings-balance { margin-bottom: 12px; }
.balance-label { display: block; font-size: 0.75rem; color: #8899a6; margin-bottom: 4px; }
.balance-value { font-size: 1.5rem; font-weight: 700; color: #e1e8ed; }

.savings-rate {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.rate-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.daily-gain { color: #10b981; font-size: 0.8rem; }

.period-selector {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  background-color: #192734;
  border-radius: 8px;
  padding: 3px;
}

.period-btn {
  flex: 1;
  padding: 6px 8px;
  border: none;
  background: transparent;
  color: #8899a6;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.period-btn:hover { color: #e1e8ed; }
.period-btn.active { background-color: #1da1f2; color: white; }

.chart-container { margin-bottom: 12px; }

.projection-summary {
  display: flex;
  gap: 24px;
  padding: 12px;
  background-color: #192734;
  border-radius: 8px;
}

.proj-item { display: flex; flex-direction: column; gap: 2px; }
.proj-label { font-size: 0.7rem; color: #8899a6; }
.proj-value { font-size: 0.95rem; font-weight: 700; }

/* Loans */
.loans-header-info, .gbm-header-info { margin-bottom: 20px; }

.loading-state {
  text-align: center;
  padding: 40px;
  color: #8899a6;
  font-size: 1rem;
}

.loading-state i {
  font-size: 1.5rem;
  margin-right: 8px;
}

.loans-header-info h2, .gbm-header-info h2 { color: #e1e8ed; font-size: 1.3rem; margin-bottom: 4px; }
.section-desc { color: #8899a6; font-size: 0.85rem; }

.loans-summary, .gbm-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
}

.loan-stat, .gbm-stat { display: flex; flex-direction: column; gap: 4px; }
.loan-stat-label, .gbm-stat-label { font-size: 0.75rem; color: #8899a6; }
.loan-stat-value, .gbm-stat-value { font-size: 1.2rem; font-weight: 700; color: #e1e8ed; }

/* Table */
.table-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 20px;
  overflow-x: auto;
  margin-bottom: 20px;
}

.table-card h3 { color: #e1e8ed; margin-bottom: 16px; font-size: 1rem; }

.data-table { width: 100%; border-collapse: collapse; }

.data-table th {
  text-align: left;
  padding: 12px 14px;
  font-size: 0.72rem;
  text-transform: uppercase;
  color: #8899a6;
  border-bottom: 1px solid #2d3741;
  background-color: #192734;
}

.data-table td {
  padding: 12px 14px;
  border-bottom: 1px solid #2d3741;
  color: #e1e8ed;
  font-size: 0.83rem;
}

.data-table tr:hover td { background-color: #1c2b3a; }

.rate-badge-sm {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 600;
}

.status-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.status-badge.active { background-color: rgba(29, 161, 242, 0.15); color: #1da1f2; }
.status-badge.paid { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }

.income { color: #10b981; font-weight: 600; }
.expense { color: #ef4444; font-weight: 600; }

/* GBM */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.chart-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 20px;
}

.chart-card h3 { color: #e1e8ed; margin-bottom: 12px; font-size: 0.95rem; }

.performance-cash-chart {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #2d3741;
}

.performance-cash-chart h4 {
  color: #8899a6;
  font-size: 0.8rem;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.ticker-cell { display: flex; flex-direction: column; }
.ticker-name { font-weight: 700; color: #e1e8ed; }
.ticker-desc { font-size: 0.7rem; color: #8899a6; }

.type-badge-inv {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.type-badge-inv.etf { background-color: rgba(29, 161, 242, 0.15); color: #1da1f2; }
.type-badge-inv.stock { background-color: rgba(139, 92, 246, 0.15); color: #8b5cf6; }
.type-badge-inv.fibra { background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; }

.recommendation {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.recommendation.buy { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }
.recommendation.hold { background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.recommendation.sell { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; }

/* Analysis */
.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 12px;
}

.analysis-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 10px;
  padding: 16px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.ticker-tag {
  font-weight: 700;
  color: #1da1f2;
  font-size: 0.9rem;
}

.analysis-text {
  color: #8899a6;
  font-size: 0.8rem;
  line-height: 1.5;
  margin-bottom: 10px;
}

.analysis-metrics {
  display: flex;
  gap: 16px;
  font-size: 0.72rem;
  color: #8899a6;
}

/* Afore */
.afore-card {
  background-color: #15202b;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 24px;
}

.afore-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.afore-brand {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: rgba(29, 161, 242, 0.15);
  color: #1da1f2;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
}

.afore-header h2 { color: #e1e8ed; margin: 0; }

.afore-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.afore-stat { display: flex; flex-direction: column; gap: 4px; }
.afore-stat-label { font-size: 0.75rem; color: #8899a6; }
.afore-stat-value { font-size: 1.1rem; font-weight: 700; color: #e1e8ed; }

.afore-projection {
  margin-top: 16px;
  padding: 12px 16px;
  background-color: #192734;
  border-radius: 8px;
  color: #8899a6;
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .charts-grid { grid-template-columns: 1fr; }
  .savings-cards { grid-template-columns: 1fr; }
  .loans-summary, .gbm-summary { flex-direction: column; }
  .section-tabs { flex-wrap: wrap; }
}
</style>
