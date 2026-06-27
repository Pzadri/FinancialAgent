<template>
  <div class="app-container dark-mode">
    <template v-if="hideChrome">
      <router-view />
    </template>
    <template v-else>
      <Sidebar />
      <main class="main-content">
        <router-view />
      </main>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()
const hideChrome = computed(() => route.meta.hideChrome === true)
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
  -webkit-tap-highlight-color: transparent;
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
  justify-content: center;
  overflow-x: hidden;
  min-width: 0;
}

.main-content > * {
  width: 100%;
  max-width: 1200px;
}

@media (max-width: 1024px) {
  .main-content {
    padding: 24px 24px;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding: 16px 12px;
    padding-bottom: 80px;
  }
}
</style>
