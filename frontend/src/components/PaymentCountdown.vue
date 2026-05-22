<template>
  <div class="payment-countdown">
    <i class="pi pi-clock" :style="{ color: clockColor }"></i>
    <span>{{ days }} días para el pago</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  days: { type: Number, required: true }
})

const clockColor = computed(() => {
  if (props.days <= 5) return '#ef4444'
  if (props.days < 15) return '#f59e0b'
  return '#10b981'
})
</script>

<style scoped>
.payment-countdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background-color: #192734;
  border-radius: 8px;
  color: #8899a6;
  font-size: 0.8rem;
}

.payment-countdown i {
  font-size: 0.9rem;
  transition: color 0.2s;
}
</style>
