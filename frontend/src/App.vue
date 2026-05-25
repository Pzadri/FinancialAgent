<template>
  <div class="app-container dark-mode">
    <Sidebar :mobileOpen="mobileMenuOpen" @close="mobileMenuOpen = false" />

    <!-- Overlay para cerrar el menú en móvil -->
    <div v-if="mobileMenuOpen" class="mobile-overlay" @click="mobileMenuOpen = false"></div>

    <main class="main-content">
      <!-- Botón hamburguesa (solo móvil) -->
      <button class="hamburger" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="Menú">
        <i class="pi pi-bars"></i>
      </button>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'

const mobileMenuOpen = ref(false)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: #0f1419;
  color: #e1e8ed;
}

.app-container {
  display: flex;
  min-height: 100vh;
  background-color: #0f1419;
}

.main-content {
  flex: 1;
  margin-left: 60px;
  padding: 24px 40px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
}

.main-content > *:not(.hamburger) {
  width: 100%;
  max-width: 1200px;
}

/* Hamburger — oculto en desktop */
.hamburger {
  display: none;
  align-self: flex-start;
  background: transparent;
  border: 1px solid #2d3741;
  color: #8899a6;
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  margin-bottom: 16px;
  transition: all 0.2s;
}
.hamburger:hover { color: #e1e8ed; border-color: #1da1f2; }

/* Overlay oscuro detrás del sidebar en móvil */
.mobile-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 999;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding: 16px;
  }

  .hamburger {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .mobile-overlay {
    display: block;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .main-content {
    padding: 20px 24px;
  }
}
</style>
