import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Inversiones from '../views/Inversiones.vue'
import Creditos from '../views/Creditos.vue'
import GastosIngresos from '../views/GastosIngresos.vue'
import Deudas from '../views/Deudas.vue'
import Aportaciones from '../views/Aportaciones.vue'
import Configuracion from '../views/Configuracion.vue'
import { isAuthenticated } from '../utils/auth.js'

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { public: true, hideChrome: true } },
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { icon: 'pi pi-home', label: 'Dashboard', shortLabel: 'Inicio' } },
  { path: '/inversiones', name: 'Inversiones', component: Inversiones, meta: { icon: 'pi pi-chart-bar', label: 'Inversiones', shortLabel: 'Inv.' } },
  { path: '/creditos', name: 'Creditos', component: Creditos, meta: { icon: 'pi pi-credit-card', label: 'Créditos', shortLabel: 'Créd.' } },
  { path: '/gastos-ingresos', name: 'GastosIngresos', component: GastosIngresos, meta: { icon: 'pi pi-list', label: 'Gastos / Ingresos', shortLabel: 'G/I' } },
  { path: '/deudas', name: 'Deudas', component: Deudas, meta: { icon: 'pi pi-money-bill', label: 'Deudas', shortLabel: 'Deudas' } },
  { path: '/aportaciones', name: 'Aportaciones', component: Aportaciones, meta: { icon: 'pi pi-calendar', label: 'Aportaciones', shortLabel: 'Aport.' } },
  { path: '/configuracion', name: 'Configuracion', component: Configuracion }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guard de autenticación: bloquea rutas privadas si no hay sesión.
router.beforeEach((to) => {
  const authed = isAuthenticated()

  if (!to.meta.public && !authed) {
    return { name: 'Login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : {} }
  }

  // Si ya está autenticado y va al login, redirigir al dashboard.
  if (to.name === 'Login' && authed) {
    return { path: '/' }
  }

  return true
})

export default router
