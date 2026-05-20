<template>
  <div class="app-container dark-mode">
    <Sidebar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
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
  padding: 24px;
  transition: margin-left 0.3s ease;
}
</style>
