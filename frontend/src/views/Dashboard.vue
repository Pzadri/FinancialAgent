<template>
  <div class="dashboard">
    <h1 class="page-title">Dashboard Financiero</h1>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon"><i class="pi pi-wallet"></i></div>
        <div class="stat-info">
          <span class="stat-label">Balance Total</span>
          <span class="stat-value">$1,250,000</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon income"><i class="pi pi-arrow-up"></i></div>
        <div class="stat-info">
          <span class="stat-label">Ingresos (mes)</span>
          <span class="stat-value">$450,000</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon expense"><i class="pi pi-arrow-down"></i></div>
        <div class="stat-info">
          <span class="stat-label">Gastos (mes)</span>
          <span class="stat-value">$320,000</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon savings"><i class="pi pi-percentage"></i></div>
        <div class="stat-info">
          <span class="stat-label">Ahorro</span>
          <span class="stat-value">28.9%</span>
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <h3>Ingresos vs Gastos</h3>
        <Line :data="lineChartData" :options="chartOptions" />
      </div>
      <div class="chart-card">
        <h3>Distribución de Gastos</h3>
        <Doughnut :data="doughnutData" :options="doughnutOptions" />
      </div>
    </div>
  </div>
</template>

<script setup>
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

const lineChartData = {
  labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
  datasets: [
    {
      label: 'Ingresos',
      data: [400000, 420000, 450000, 430000, 460000, 450000],
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      fill: true,
      tension: 0.4
    },
    {
      label: 'Gastos',
      data: [300000, 310000, 290000, 340000, 320000, 320000],
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

const doughnutData = {
  labels: ['Vivienda', 'Alimentación', 'Transporte', 'Entretenimiento', 'Servicios', 'Otros'],
  datasets: [{
    data: [35, 20, 15, 12, 10, 8],
    backgroundColor: ['#1da1f2', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280']
  }]
}

const doughnutOptions = {
  responsive: true,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#8899a6' }
    }
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
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
  background-color: rgba(29, 161, 242, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1da1f2;
  font-size: 1.2rem;
}

.stat-icon.income {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.stat-icon.expense {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.stat-icon.savings {
  background-color: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
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

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
