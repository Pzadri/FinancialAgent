<template>
  <nav
    class="sidebar"
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
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isExpanded = ref(false)

const routes = router.getRoutes().filter(r => r.meta && r.meta.label)
</script>

<style scoped>
.sidebar {
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

.sidebar.expanded {
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
</style>
