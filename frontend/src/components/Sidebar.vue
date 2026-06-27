<template>
  <!-- Desktop Sidebar -->
  <nav
    class="sidebar desktop-sidebar"
    :class="{ expanded: isExpanded }"
    @mouseenter="isExpanded = true"
    @mouseleave="isExpanded = false"
  >
    <div class="sidebar-header">
      <i class="pi pi-chart-line sidebar-logo"></i>
      <span v-if="isExpanded" class="sidebar-title">FinARG</span>
    </div>

    <ul class="sidebar-menu">
      <li v-for="route in routes" :key="route.path">
        <router-link :to="route.path" class="sidebar-link" active-class="active">
          <i :class="route.meta.icon"></i>
          <span v-if="isExpanded" class="link-label">{{ route.meta.label }}</span>
        </router-link>
      </li>
    </ul>

    <div class="sidebar-footer">
      <router-link to="/configuracion" class="sidebar-link" active-class="active">
        <i class="pi pi-cog"></i>
        <span v-if="isExpanded" class="link-label">Configuración</span>
      </router-link>
      <button type="button" class="sidebar-link logout-link" title="Cerrar sesión" @click="handleLogout">
        <i class="pi pi-sign-out"></i>
        <span v-if="isExpanded" class="link-label">Cerrar sesión</span>
      </button>
    </div>
  </nav>

  <!-- Mobile Bottom Nav -->
  <nav class="mobile-nav">
    <router-link
      v-for="route in mobileRoutes"
      :key="route.path"
      :to="route.path"
      class="mobile-nav-item"
      active-class="active"
      :exact="route.path === '/'"
    >
      <i :class="route.meta.icon"></i>
      <span>{{ route.meta.shortLabel || route.meta.label }}</span>
    </router-link>
    <router-link to="/configuracion" class="mobile-nav-item" active-class="active">
      <i class="pi pi-cog"></i>
      <span>Config</span>
    </router-link>
    <button type="button" class="mobile-nav-item logout-mobile" @click="handleLogout">
      <i class="pi pi-sign-out"></i>
      <span>Salir</span>
    </button>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { logout } from '../utils/auth.js'

const router = useRouter()
const isExpanded = ref(false)

const routes = router.getRoutes().filter(r => r.meta && r.meta.label)
const mobileRoutes = routes // Show all routes + config in mobile nav

function handleLogout() {
  logout()
  router.push({ name: 'Login' })
}
</script>

<style scoped>
/* ===== DESKTOP SIDEBAR ===== */
.desktop-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 60px;
  background-color: #15202b;
  border-right: 1px solid #2d3741;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 1000;
  overflow: hidden;
}

.desktop-sidebar.expanded {
  width: 240px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 20px 16px;
  gap: 12px;
  border-bottom: 1px solid #2d3741;
}

.sidebar-logo {
  font-size: 1.5rem;
  color: #1da1f2;
  min-width: 28px;
  text-align: center;
}

.sidebar-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #e1e8ed;
  white-space: nowrap;
}

.sidebar-menu {
  list-style: none;
  padding: 12px 0;
  flex: 1;
}

.sidebar-link {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
  color: #8899a6;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.sidebar-link:hover {
  color: #e1e8ed;
  background-color: #1c2b3a;
}

.sidebar-link.active {
  color: #1da1f2;
  background-color: #1c2b3a;
  border-right: 3px solid #1da1f2;
}

.sidebar-link i {
  font-size: 1.2rem;
  min-width: 28px;
  text-align: center;
}

.link-label {
  white-space: nowrap;
  font-size: 0.9rem;
}

.sidebar-footer {
  border-top: 1px solid #2d3741;
  padding: 12px 0;
}

.logout-link {
  width: 100%;
  background: none;
  border: none;
  font-family: inherit;
  font-size: inherit;
  text-align: left;
}

.logout-link:hover {
  color: #f4212e;
  background-color: #1c2b3a;
}

/* ===== MOBILE BOTTOM NAV ===== */
.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background-color: #15202b;
  border-top: 1px solid #2d3741;
  z-index: 1000;
  justify-content: space-around;
  align-items: center;
  padding: 0 4px;
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  color: #8899a6;
  text-decoration: none;
  font-size: 0.58rem;
  padding: 6px 2px;
  border-radius: 8px;
  transition: color 0.2s;
  min-width: 0;
  flex: 1;
}

.mobile-nav-item i {
  font-size: 1.15rem;
}

.mobile-nav-item span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  text-align: center;
}

.mobile-nav-item.active {
  color: #1da1f2;
}

.logout-mobile {
  background: none;
  border: none;
  font-family: inherit;
  cursor: pointer;
}

.logout-mobile:active,
.logout-mobile:hover {
  color: #f4212e;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .desktop-sidebar {
    display: none;
  }

  .mobile-nav {
    display: flex;
  }
}
</style>
