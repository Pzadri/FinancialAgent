import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Inversiones from '../views/Inversiones.vue'
import Creditos from '../views/Creditos.vue'
import GastosIngresos from '../views/GastosIngresos.vue'
import RegistroGI from '../views/RegistroGI.vue'
import Alerts from '../views/Alerts.vue'
import Settings from '../views/Settings.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { icon: 'pi pi-home', label: 'Dashboard' } },
  { path: '/inversiones', name: 'Inversiones', component: Inversiones, meta: { icon: 'pi pi-chart-bar', label: 'Inversiones' } },
  { path: '/creditos', name: 'Creditos', component: Creditos, meta: { icon: 'pi pi-credit-card', label: 'Créditos' } },
  { path: '/gastos-ingresos', name: 'GastosIngresos', component: GastosIngresos, meta: { icon: 'pi pi-list', label: 'Gastos / Ingresos' } },
  { path: '/gastos-ingresos/registro', name: 'RegistroGI', component: RegistroGI },
  { path: '/alerts', name: 'Alerts', component: Alerts, meta: { icon: 'pi pi-bell', label: 'Alertas' } },
  { path: '/settings', name: 'Settings', component: Settings, meta: { icon: 'pi pi-cog', label: 'Configuración' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
