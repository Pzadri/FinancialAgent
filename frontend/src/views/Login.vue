<template>
  <main class="app" aria-label="Inicio de sesión de finanzas personales">
    <canvas ref="sceneCanvas" id="scene" aria-hidden="true"></canvas>
    <div class="ambient-vignette" aria-hidden="true"></div>
    <div class="scanlines" aria-hidden="true"></div>

    <div class="hud-frame" aria-hidden="true">
      <span class="corner tl"></span>
      <span class="corner tr"></span>
      <span class="corner bl"></span>
      <span class="corner br"></span>
      <span class="micro-lines"></span>
    </div>

    <section class="login-shell" :class="{ entering }">
      <div class="login-card" :class="{ entering }">
        <div class="eye-emblem" aria-hidden="true">
          <svg viewBox="0 0 48 48" fill="none">
            <defs>
              <linearGradient id="eyeGradient" x1="5" y1="9" x2="42" y2="39" gradientUnits="userSpaceOnUse">
                <stop stop-color="#16D9FF" />
                <stop offset="0.55" stop-color="#2E7BFF" />
                <stop offset="1" stop-color="#A43BFF" />
              </linearGradient>
            </defs>
            <path d="M5 24C9.7 16.9 16.2 13 24 13C31.8 13 38.3 16.9 43 24C38.3 31.1 31.8 35 24 35C16.2 35 9.7 31.1 5 24Z"
              stroke="url(#eyeGradient)" stroke-width="2.5" />
            <circle class="iris" cx="24" cy="24" r="6.5" stroke="url(#eyeGradient)" stroke-width="2.5" />
            <circle cx="24" cy="24" r="2.4" fill="#D6F9FF" />
          </svg>
        </div>

        <h1 class="title">Bienvenido Adrian</h1>
        <p class="subtitle">Ingresa tu contraseña</p>

        <form class="form" @submit.prevent="handleLogin" autocomplete="on">
          <div class="field-wrap">
            <input
              class="password-input"
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              placeholder="Contraseña"
              autocomplete="current-password"
              aria-label="Contraseña"
            />
            <button
              class="visibility-toggle"
              type="button"
              :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              :aria-pressed="String(showPassword)"
              :data-visible="String(showPassword)"
              @click="showPassword = !showPassword"
              tabindex="-1"
            >
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M2.5 12S6 6.5 12 6.5S21.5 12 21.5 12S18 17.5 12 17.5S2.5 12 2.5 12Z"
                  stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" />
                <circle cx="12" cy="12" r="2.7" stroke="currentColor" stroke-width="1.7" />
                <path class="slash" d="M4 4L20 20" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" />
              </svg>
            </button>
          </div>

          <button class="submit-button" type="submit">Entrar</button>
        </form>

        <div class="status" :class="statusClass" aria-live="polite">{{ statusText }}</div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { login } from '../utils/auth.js'

const router = useRouter()
const route = useRoute()

const password = ref('')
const showPassword = ref(false)
const statusText = ref('')
const statusClass = ref('')
const entering = ref(false)

const sceneCanvas = ref(null)
let sceneController = null

async function handleLogin() {
  if (entering.value) return

  if (!password.value.trim()) {
    statusText.value = 'Ingresa tu contraseña.'
    statusClass.value = 'error'
    return
  }

  statusText.value = 'Validando…'
  statusClass.value = ''

  try {
    await login(password.value)
  } catch (e) {
    statusText.value = e.response?.data?.detail || 'Contraseña incorrecta.'
    statusClass.value = 'error'
    return
  }

  // Contraseña válida: dispara el zoom del globo y redirige al terminar (2 s).
  statusText.value = ''
  entering.value = true
  if (sceneController) sceneController.zoomIn()
  const redirect = route.query.redirect || '/'
  setTimeout(() => router.replace(redirect), 2000)
}

onMounted(() => {
  sceneController = startScene(sceneCanvas.value)
})

onUnmounted(() => {
  if (sceneController) sceneController.stop()
})

/* ─────────────────────────────────────────────────────────────────────
   Escena animada: globo de partículas, líneas, anillos orbitales,
   estrellas, escáner y pulsos de radar (canvas 2D).
   ───────────────────────────────────────────────────────────────────── */
function startScene(canvas) {
  const ctx = canvas.getContext('2d', { alpha: false })

  let width = 0
  let height = 0
  let dpr = Math.min(window.devicePixelRatio || 1, 2)
  let animationFrame = 0
  let lastTime = performance.now()

  // Estado del zoom de entrada
  let zoomStart = null
  const ZOOM_DURATION = 2000
  let zoom = 1

  const stars = []
  const spherePoints = []
  const orbitRings = []
  const pulses = []
  const TAU = Math.PI * 2

  function rand(min, max) {
    return min + Math.random() * (max - min)
  }

  function resize() {
    width = canvas.clientWidth || window.innerWidth
    height = canvas.clientHeight || window.innerHeight
    dpr = Math.min(window.devicePixelRatio || 1, 2)
    canvas.width = Math.floor(width * dpr)
    canvas.height = Math.floor(height * dpr)
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    buildScene()
  }

  function buildScene() {
    stars.length = 0
    spherePoints.length = 0
    orbitRings.length = 0
    pulses.length = 0

    const starCount = Math.floor(Math.min(360, (width * height) / 5200))
    for (let i = 0; i < starCount; i++) {
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: rand(0.35, 1.25),
        alpha: rand(0.12, 0.72),
        speed: rand(0.08, 0.3),
        phase: rand(0, TAU)
      })
    }

    const mobile = width < 680
    const pointCount = mobile ? 1650 : 2600
    const golden = Math.PI * (3 - Math.sqrt(5))
    for (let i = 0; i < pointCount; i++) {
      const y = 1 - (i / (pointCount - 1)) * 2
      const sphereRadius = Math.sqrt(Math.max(0, 1 - y * y))
      const theta = golden * i
      const x = Math.cos(theta) * sphereRadius
      const z = Math.sin(theta) * sphereRadius
      const landSignal =
        Math.sin(theta * 2.7 + y * 7.5) +
        Math.cos(theta * 1.3 - y * 11.2) +
        Math.sin((x + z) * 8.4)
      spherePoints.push({
        x, y, z,
        size: landSignal > 0.7 ? rand(1.1, 2) : rand(0.45, 1.15),
        alpha: landSignal > 0.45 ? rand(0.58, 0.96) : rand(0.16, 0.46),
        hueShift: rand(-12, 18)
      })
    }

    const ringCount = mobile ? 6 : 9
    for (let i = 0; i < ringCount; i++) {
      orbitRings.push({
        tiltX: rand(-1.15, 1.15),
        tiltZ: rand(-1.15, 1.15),
        radius: rand(1.04, 1.33),
        speed: rand(-0.13, 0.13),
        phase: rand(0, TAU),
        alpha: rand(0.16, 0.42),
        violet: Math.random() > 0.55
      })
    }

    for (let i = 0; i < 5; i++) {
      pulses.push({
        phase: rand(0, 1),
        speed: rand(0.04, 0.08),
        alpha: rand(0.05, 0.14)
      })
    }
  }

  function rotatePoint(point, ax, ay, az = 0) {
    let { x, y, z } = point
    const cosY = Math.cos(ay)
    const sinY = Math.sin(ay)
    ;[x, z] = [x * cosY - z * sinY, x * sinY + z * cosY]
    const cosX = Math.cos(ax)
    const sinX = Math.sin(ax)
    ;[y, z] = [y * cosX - z * sinX, y * sinX + z * cosX]
    const cosZ = Math.cos(az)
    const sinZ = Math.sin(az)
    ;[x, y] = [x * cosZ - y * sinZ, x * sinZ + y * cosZ]
    return { x, y, z }
  }

  function project(point, radius, centerX, centerY) {
    const perspective = 3.3
    const scale = perspective / (perspective - point.z)
    return {
      x: centerX + point.x * radius * scale,
      y: centerY + point.y * radius * scale,
      scale,
      depth: point.z
    }
  }

  function drawBackground(time) {
    const gradient = ctx.createRadialGradient(
      width * 0.5, height * 0.46, 0,
      width * 0.5, height * 0.46, Math.max(width, height) * 0.78
    )
    gradient.addColorStop(0, '#07142f')
    gradient.addColorStop(0.42, '#030a1c')
    gradient.addColorStop(1, '#01030a')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, width, height)

    for (const star of stars) {
      const flicker = 0.55 + Math.sin(time * star.speed + star.phase) * 0.45
      ctx.globalAlpha = star.alpha * flicker
      ctx.fillStyle = Math.random() > 0.93 ? '#a77cff' : '#49ccff'
      ctx.beginPath()
      ctx.arc(star.x, star.y, star.radius, 0, TAU)
      ctx.fill()
    }
    ctx.globalAlpha = 1
  }

  function drawGrid(centerX, centerY, globeRadius, time) {
    ctx.save()
    ctx.globalCompositeOperation = 'screen'
    ctx.strokeStyle = 'rgba(40, 137, 255, 0.08)'
    ctx.lineWidth = 1
    const spacing = Math.max(38, Math.min(66, width / 24))
    const shiftX = (time * 2.2) % spacing
    const shiftY = (time * 1.1) % spacing
    for (let x = -spacing + shiftX; x < width + spacing; x += spacing) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()
    }
    for (let y = -spacing + shiftY; y < height + spacing; y += spacing) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y)
      ctx.stroke()
    }
    const glow = ctx.createRadialGradient(centerX, centerY, globeRadius * 0.3, centerX, centerY, globeRadius * 1.7)
    glow.addColorStop(0, 'rgba(0,0,0,0)')
    glow.addColorStop(0.55, 'rgba(5,25,75,0.08)')
    glow.addColorStop(1, 'rgba(0,0,0,0.34)')
    ctx.fillStyle = glow
    ctx.fillRect(0, 0, width, height)
    ctx.restore()
  }

  function drawGlobe(time) {
    const mobile = width < 680
    const centerX = width * 0.5
    const centerY = mobile ? height * 0.46 : height * 0.48
    const baseRadius = mobile
      ? Math.min(height * 0.46, width * 0.82)
      : Math.min(height * 0.46, width * 0.31)
    const globeRadius = baseRadius * zoom

    drawGrid(centerX, centerY, globeRadius, time)

    ctx.save()
    ctx.globalCompositeOperation = 'screen'

    const atmosphere = ctx.createRadialGradient(
      centerX - globeRadius * 0.22, centerY - globeRadius * 0.25, globeRadius * 0.1,
      centerX, centerY, globeRadius * 1.18
    )
    atmosphere.addColorStop(0, 'rgba(31, 204, 255, 0.11)')
    atmosphere.addColorStop(0.55, 'rgba(26, 92, 255, 0.045)')
    atmosphere.addColorStop(0.82, 'rgba(124, 44, 255, 0.08)')
    atmosphere.addColorStop(1, 'rgba(0, 0, 0, 0)')
    ctx.fillStyle = atmosphere
    ctx.beginPath()
    ctx.arc(centerX, centerY, globeRadius * 1.22, 0, TAU)
    ctx.fill()

    const rotationY = time * 0.12
    const rotationX = -0.15 + Math.sin(time * 0.17) * 0.035

    const projectedPoints = []
    for (const point of spherePoints) {
      const rotated = rotatePoint(point, rotationX, rotationY)
      const projected = project(rotated, globeRadius, centerX, centerY)
      projectedPoints.push({ ...projected, source: point })
    }
    projectedPoints.sort((a, b) => a.depth - b.depth)

    for (const p of projectedPoints) {
      const front = (p.depth + 1) * 0.5
      if (front < 0.035) continue
      const edge = Math.sqrt(
        Math.pow((p.x - centerX) / globeRadius, 2) +
        Math.pow((p.y - centerY) / globeRadius, 2)
      )
      const rimBoost = Math.max(0, (edge - 0.72) / 0.28)
      const alpha = p.source.alpha * (0.22 + front * 0.84) * (1 + rimBoost * 0.65)
      const hue = 194 + p.source.hueShift + Math.max(0, p.x - centerX) / globeRadius * 34
      ctx.globalAlpha = Math.min(1, alpha)
      ctx.fillStyle = `hsl(${hue} 100% ${58 + front * 12}%)`
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.source.size * p.scale, 0, TAU)
      ctx.fill()
    }

    // Latitudes
    ctx.lineWidth = 0.75
    for (let lat = -60; lat <= 60; lat += 20) {
      ctx.beginPath()
      for (let i = 0; i <= 120; i++) {
        const lon = (i / 120) * TAU
        const phi = (lat * Math.PI) / 180
        const point = {
          x: Math.cos(phi) * Math.cos(lon),
          y: Math.sin(phi),
          z: Math.cos(phi) * Math.sin(lon)
        }
        const rotated = rotatePoint(point, rotationX, rotationY)
        const p = project(rotated, globeRadius, centerX, centerY)
        if (rotated.z > -0.2) {
          if (i === 0) ctx.moveTo(p.x, p.y)
          else ctx.lineTo(p.x, p.y)
        }
      }
      ctx.strokeStyle = 'rgba(49, 181, 255, 0.11)'
      ctx.stroke()
    }

    // Longitudes
    for (let lonDeg = 0; lonDeg < 360; lonDeg += 24) {
      ctx.beginPath()
      let started = false
      for (let i = 0; i <= 120; i++) {
        const phi = -Math.PI / 2 + (i / 120) * Math.PI
        const lon = (lonDeg * Math.PI) / 180
        const point = {
          x: Math.cos(phi) * Math.cos(lon),
          y: Math.sin(phi),
          z: Math.cos(phi) * Math.sin(lon)
        }
        const rotated = rotatePoint(point, rotationX, rotationY)
        const p = project(rotated, globeRadius, centerX, centerY)
        if (rotated.z > -0.2) {
          if (!started) {
            ctx.moveTo(p.x, p.y)
            started = true
          } else {
            ctx.lineTo(p.x, p.y)
          }
        }
      }
      ctx.strokeStyle = 'rgba(104, 65, 255, 0.085)'
      ctx.stroke()
    }

    // Anillos orbitales
    for (const ring of orbitRings) {
      ctx.beginPath()
      let started = false
      const movingPhase = ring.phase + time * ring.speed
      for (let i = 0; i <= 160; i++) {
        const angle = (i / 160) * TAU + movingPhase
        let point = {
          x: Math.cos(angle) * ring.radius,
          y: 0,
          z: Math.sin(angle) * ring.radius
        }
        point = rotatePoint(point, ring.tiltX, 0, ring.tiltZ)
        const p = project(point, globeRadius, centerX, centerY)
        if (!started) {
          ctx.moveTo(p.x, p.y)
          started = true
        } else {
          ctx.lineTo(p.x, p.y)
        }
      }
      ctx.lineWidth = 1.05
      ctx.globalAlpha = ring.alpha
      ctx.strokeStyle = ring.violet ? '#9a43ff' : '#1ccfff'
      ctx.shadowBlur = 7
      ctx.shadowColor = ring.violet ? '#8038ff' : '#19bfff'
      ctx.stroke()
      ctx.shadowBlur = 0

      const nodeAngle = movingPhase + time * 0.35
      let node = {
        x: Math.cos(nodeAngle) * ring.radius,
        y: 0,
        z: Math.sin(nodeAngle) * ring.radius
      }
      node = rotatePoint(node, ring.tiltX, 0, ring.tiltZ)
      const np = project(node, globeRadius, centerX, centerY)
      ctx.globalAlpha = 0.9
      ctx.fillStyle = ring.violet ? '#ca7cff' : '#b7f8ff'
      ctx.shadowBlur = 14
      ctx.shadowColor = ring.violet ? '#8a3cff' : '#18d9ff'
      ctx.beginPath()
      ctx.arc(np.x, np.y, 1.5 + np.scale * 0.7, 0, TAU)
      ctx.fill()
      ctx.shadowBlur = 0
    }

    // Borde brillante
    const rim = ctx.createLinearGradient(centerX - globeRadius, centerY, centerX + globeRadius, centerY)
    rim.addColorStop(0, 'rgba(0,219,255,0.9)')
    rim.addColorStop(0.45, 'rgba(27,119,255,0.18)')
    rim.addColorStop(0.72, 'rgba(92,54,255,0.38)')
    rim.addColorStop(1, 'rgba(177,46,255,0.95)')
    ctx.globalAlpha = 0.8
    ctx.strokeStyle = rim
    ctx.lineWidth = mobile ? 1.2 : 1.6
    ctx.shadowBlur = 20
    ctx.shadowColor = '#1aaeff'
    ctx.beginPath()
    ctx.arc(centerX, centerY, globeRadius, 0, TAU)
    ctx.stroke()
    ctx.shadowBlur = 0

    // Pulsos de radar
    for (const pulse of pulses) {
      pulse.phase = (pulse.phase + pulse.speed * 0.016) % 1
      const radius = globeRadius * (0.28 + pulse.phase * 1.05)
      const alpha = (1 - pulse.phase) * pulse.alpha
      ctx.globalAlpha = alpha
      ctx.strokeStyle = pulse.phase > 0.55 ? '#9e4cff' : '#27dcff'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.arc(centerX, centerY, radius, 0, TAU)
      ctx.stroke()
    }

    // Escáner horizontal
    const scanY = centerY - globeRadius + ((time * 45) % (globeRadius * 2))
    const half = Math.sqrt(Math.max(0, globeRadius * globeRadius - Math.pow(scanY - centerY, 2)))
    const scanner = ctx.createLinearGradient(centerX - half, scanY, centerX + half, scanY)
    scanner.addColorStop(0, 'rgba(15,218,255,0)')
    scanner.addColorStop(0.5, 'rgba(61,231,255,0.45)')
    scanner.addColorStop(1, 'rgba(133,65,255,0)')
    ctx.globalAlpha = 0.5
    ctx.strokeStyle = scanner
    ctx.lineWidth = 1.3
    ctx.beginPath()
    ctx.moveTo(centerX - half, scanY)
    ctx.lineTo(centerX + half, scanY)
    ctx.stroke()

    ctx.restore()
  }

  function draw(timeMs) {
    lastTime = timeMs
    const time = timeMs / 1000

    // Calcula el factor de zoom de entrada (ease-in acelerado)
    if (zoomStart !== null) {
      const p = Math.min(1, (timeMs - zoomStart) / ZOOM_DURATION)
      const eased = p * p * p
      zoom = 1 + eased * 14
    }

    drawBackground(time)
    drawGlobe(time)
    animationFrame = requestAnimationFrame(draw)
  }

  window.addEventListener('resize', resize, { passive: true })
  resize()
  animationFrame = requestAnimationFrame(draw)

  return {
    stop() {
      cancelAnimationFrame(animationFrame)
      window.removeEventListener('resize', resize)
    },
    zoomIn() {
      if (zoomStart === null) zoomStart = performance.now()
    }
  }
}
</script>

<style scoped>
.app {
  --bg: #020713;
  --cyan: #16d9ff;
  --blue: #146cff;
  --violet: #8c39ff;
  --text: #f7fbff;
  --muted: #b7bfd2;
  --field: rgba(2, 8, 24, 0.55);
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100svh;
  min-height: 560px;
  isolation: isolate;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 45%, rgba(18, 80, 180, 0.14), transparent 42%),
    radial-gradient(circle at 75% 35%, rgba(132, 42, 255, 0.08), transparent 34%),
    linear-gradient(180deg, #03091a 0%, #01040d 100%);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

#scene {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.ambient-vignette {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(0, 3, 10, 0.6), transparent 20%, transparent 80%, rgba(0, 3, 10, 0.6)),
    linear-gradient(180deg, rgba(0, 3, 10, 0.25), transparent 32%, transparent 74%, rgba(0, 3, 10, 0.62));
  mix-blend-mode: multiply;
}

.scanlines {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  opacity: 0.08;
  background-image: repeating-linear-gradient(to bottom,
    rgba(255, 255, 255, 0.09) 0,
    rgba(255, 255, 255, 0.09) 1px,
    transparent 1px,
    transparent 4px);
}

.hud-frame {
  position: absolute;
  inset: clamp(18px, 3.6vw, 52px);
  z-index: 3;
  pointer-events: none;
  opacity: 0.68;
}

.hud-frame::before,
.hud-frame::after {
  content: '';
  position: absolute;
  inset: 0;
  border: 1px solid rgba(24, 190, 255, 0.16);
  clip-path: polygon(0 0, 12% 0, 12% 1px, 88% 1px, 88% 0, 100% 0, 100% 16%,
    calc(100% - 1px) 16%, calc(100% - 1px) 84%, 100% 84%, 100% 100%, 88% 100%,
    88% calc(100% - 1px), 12% calc(100% - 1px), 12% 100%, 0 100%, 0 84%, 1px 84%, 1px 16%, 0 16%);
}

.hud-frame::after {
  inset: 12px;
  opacity: 0.34;
  border-color: rgba(139, 52, 255, 0.18);
}

.corner {
  position: absolute;
  width: 74px;
  height: 74px;
  filter: drop-shadow(0 0 8px rgba(22, 217, 255, 0.16));
}

.corner::before,
.corner::after {
  content: '';
  position: absolute;
  background: linear-gradient(90deg, rgba(22, 217, 255, 0.92), rgba(140, 57, 255, 0.18));
}

.corner::before { width: 100%; height: 1px; }
.corner::after { width: 1px; height: 100%; }
.corner.tl { left: 0; top: 0; }
.corner.tr { right: 0; top: 0; transform: scaleX(-1); }
.corner.bl { left: 0; bottom: 0; transform: scaleY(-1); }
.corner.br { right: 0; bottom: 0; transform: scale(-1); }

.micro-lines {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.micro-lines::before,
.micro-lines::after {
  content: '';
  position: absolute;
  left: 50%;
  width: min(68vw, 900px);
  height: 1px;
  transform: translateX(-50%);
  background: linear-gradient(90deg, transparent, rgba(22, 217, 255, 0.28), transparent);
  animation: linePulse 4.8s ease-in-out infinite;
}

.micro-lines::before { top: 8%; }
.micro-lines::after { bottom: 8%; animation-delay: -2.4s; }

@keyframes linePulse {
  0%, 100% { opacity: 0.18; transform: translateX(-50%) scaleX(0.72); }
  50% { opacity: 0.8; transform: translateX(-50%) scaleX(1); }
}

.login-shell {
  position: relative;
  z-index: 5;
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  padding:
    max(24px, env(safe-area-inset-top))
    max(20px, env(safe-area-inset-right))
    max(24px, env(safe-area-inset-bottom))
    max(20px, env(safe-area-inset-left));
}

.login-card {
  width: min(420px, calc(100vw - 40px));
  padding: 24px 26px 26px;
  border: 1px solid rgba(86, 173, 255, 0.12);
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(7, 15, 37, 0.22), rgba(3, 8, 24, 0.34));
  box-shadow:
    0 26px 90px rgba(0, 0, 0, 0.42),
    inset 0 1px 0 rgba(255, 255, 255, 0.03),
    0 0 55px rgba(38, 123, 255, 0.05);
  backdrop-filter: blur(8px) saturate(120%);
  -webkit-backdrop-filter: blur(8px) saturate(120%);
  text-align: center;
  animation: cardFloat 6s ease-in-out infinite;
}

@keyframes cardFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

/* Transición de entrada: la tarjeta se desvanece y escala mientras el globo hace zoom */
.login-card.entering {
  animation: none;
  transform: scale(1.18);
  opacity: 0;
  filter: blur(6px);
  transition: opacity 1.1s ease-in, transform 1.6s cubic-bezier(0.6, 0, 0.9, 0.4), filter 1.1s ease-in;
  pointer-events: none;
}

.login-shell.entering {
  pointer-events: none;
}

.eye-emblem {
  position: relative;
  width: 78px;
  height: 78px;
  margin: 0 auto 10px;
  display: grid;
  place-items: center;
  filter: drop-shadow(0 0 18px rgba(19, 202, 255, 0.28));
}

.eye-emblem::before,
.eye-emblem::after {
  content: '';
  position: absolute;
  inset: 8px;
  border: 2px solid transparent;
  border-radius: 22px;
  transform: rotate(30deg);
  background:
    linear-gradient(#071025, #071025) padding-box,
    linear-gradient(135deg, var(--cyan), var(--blue) 52%, var(--violet)) border-box;
  box-shadow:
    0 0 20px rgba(22, 217, 255, 0.16),
    inset 0 0 16px rgba(91, 70, 255, 0.09);
}

.eye-emblem::after {
  inset: 3px;
  opacity: 0.26;
  animation: emblemSpin 12s linear infinite;
}

@keyframes emblemSpin {
  to { transform: rotate(390deg); }
}

.eye-emblem svg {
  position: relative;
  z-index: 2;
  width: 42px;
  height: 42px;
  overflow: visible;
}

.eye-emblem .iris {
  transform-origin: 24px 24px;
  animation: irisPulse 2.8s ease-in-out infinite;
}

@keyframes irisPulse {
  0%, 100% { transform: scale(0.88); opacity: 0.78; }
  50% { transform: scale(1.08); opacity: 1; }
}

.title {
  margin: 0;
  font-size: clamp(1.55rem, 2.2vw, 2rem);
  line-height: 1.15;
  letter-spacing: -0.025em;
  font-weight: 650;
  text-shadow: 0 0 22px rgba(66, 154, 255, 0.14);
}

.subtitle {
  margin: 10px 0 22px;
  color: var(--muted);
  font-size: 0.96rem;
  font-weight: 400;
}

.form {
  display: grid;
  gap: 14px;
}

.field-wrap {
  position: relative;
}

.password-input {
  width: 100%;
  height: 54px;
  border: 1px solid rgba(133, 160, 230, 0.34);
  border-radius: 12px;
  outline: none;
  padding: 0 54px 0 17px;
  color: white;
  background: var(--field);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  transition: border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
}

.password-input::placeholder {
  color: rgba(205, 215, 240, 0.54);
}

.password-input:focus {
  border-color: rgba(37, 206, 255, 0.78);
  background: rgba(3, 10, 29, 0.72);
  box-shadow:
    0 0 0 3px rgba(22, 217, 255, 0.08),
    0 0 28px rgba(35, 155, 255, 0.12);
}

.visibility-toggle {
  position: absolute;
  top: 50%;
  right: 8px;
  width: 42px;
  height: 42px;
  transform: translateY(-50%);
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 10px;
  color: #a8b5ff;
  background: transparent;
  cursor: pointer;
  transition: color 160ms ease, background 160ms ease, transform 160ms ease;
}

.visibility-toggle:hover {
  color: white;
  background: rgba(109, 90, 255, 0.08);
}

.visibility-toggle:active {
  transform: translateY(-50%) scale(0.92);
}

.visibility-toggle svg {
  width: 22px;
  height: 22px;
}

.visibility-toggle .slash {
  transform-origin: center;
  transition: opacity 160ms ease, transform 160ms ease;
}

.visibility-toggle[data-visible='true'] .slash {
  opacity: 0;
  transform: scale(0.5);
}

.submit-button {
  position: relative;
  isolation: isolate;
  height: 54px;
  border: 0;
  border-radius: 12px;
  color: white;
  font-weight: 650;
  letter-spacing: 0.01em;
  cursor: pointer;
  overflow: hidden;
  background: linear-gradient(90deg, #11d6f5 0%, #2378ff 50%, #963cff 100%);
  box-shadow:
    0 12px 32px rgba(37, 104, 255, 0.22),
    0 0 22px rgba(126, 57, 255, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.25);
  transition: transform 160ms ease, filter 160ms ease, box-shadow 160ms ease;
}

.submit-button::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: linear-gradient(110deg,
    transparent 15%,
    rgba(255, 255, 255, 0.34) 42%,
    transparent 67%);
  transform: translateX(-130%);
  animation: buttonSweep 3.8s ease-in-out infinite;
}

@keyframes buttonSweep {
  0%, 56% { transform: translateX(-130%); }
  78%, 100% { transform: translateX(130%); }
}

.submit-button:hover {
  filter: brightness(1.08) saturate(1.12);
  box-shadow:
    0 16px 38px rgba(37, 104, 255, 0.3),
    0 0 34px rgba(126, 57, 255, 0.26),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.submit-button:active {
  transform: scale(0.985);
}

.status {
  min-height: 18px;
  margin-top: 14px;
  color: rgba(187, 207, 235, 0.65);
  font-size: 0.78rem;
  letter-spacing: 0.02em;
}

.status.success { color: #5dffc7; }
.status.error { color: #ff7da8; }

@media (max-width: 680px) {
  .app { min-height: 520px; }
  .hud-frame { inset: 16px 12px 18px; }
  .corner { width: 44px; height: 44px; }
  .login-card {
    width: min(88vw, 360px);
    padding: 20px 18px 22px;
    border-radius: 20px;
    background: linear-gradient(180deg, rgba(3, 9, 27, 0.2), rgba(3, 8, 24, 0.4));
    backdrop-filter: blur(6px) saturate(115%);
  }
  .eye-emblem { width: 66px; height: 66px; margin-bottom: 8px; }
  .eye-emblem svg { width: 36px; height: 36px; }
  .subtitle { margin-bottom: 18px; }
  .password-input,
  .submit-button { height: 52px; }
}

@media (max-height: 650px) {
  .login-card { transform: scale(0.9); animation: none; }
}
</style>
