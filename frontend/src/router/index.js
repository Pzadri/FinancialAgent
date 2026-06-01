import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Inversiones from '../views/Inversiones.vue'
import Creditos from '../views/Creditos.vue'
import GastosIngresos from '../views/GastosIngresos.vue'
import RegistroGI from '../views/RegistroGI.vue'
import Deudas from '../views/Deudas.vue'
import NuevaDeuda from '../views/NuevaDeuda.vue'
import Aportaciones from '../views/Aportaciones.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { icon: 'pi pi-home', label: 'Dashboard' } },
  { path: '/inversiones', name: 'Inversiones', component: Inversiones, meta: { icon: 'pi pi-chart-bar', label: 'Inversiones' } },
  { path: '/creditos', name: 'Creditos', component: Creditos, meta: { icon: 'pi pi-credit-card', label: 'Créditos' } },
  { path: '/gastos-ingresos', name: 'GastosIngresos', component: GastosIngresos, meta: { icon: 'pi pi-list', label: 'Gastos / Ingresos' } },
  { path: '/gastos-ingresos/registro', name: 'RegistroGI', component: RegistroGI },
  { path: '/deudas', name: 'Deudas', component: Deudas, meta: { icon: 'pi pi-money-bill', label: 'Deudas' } },
  { path: '/deudas/nuevo', name: 'NuevaDeuda', component: NuevaDeuda },
  { path: '/aportaciones', name: 'Aportaciones', component: Aportaciones, meta: { icon: 'pi pi-calendar', label: 'Aportaciones' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
