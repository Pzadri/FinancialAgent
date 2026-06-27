<template>
  <div class="configuracion">
    <h1 class="page-title">Configuración</h1>

    <!-- Tabs -->
    <div class="config-tabs">
      <button class="tab-btn" :class="{ active: activeTab === 'ahorro' }" @click="activeTab = 'ahorro'">
        <i class="pi pi-wallet"></i> Cuentas de Ahorro
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'creditos' }" @click="activeTab = 'creditos'">
        <i class="pi pi-credit-card"></i> Créditos
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'aportaciones' }" @click="activeTab = 'aportaciones'">
        <i class="pi pi-calendar"></i> Aportaciones
      </button>
    </div>

    <!-- AHORRO -->
    <div v-if="activeTab === 'ahorro'" class="config-section">
      <div class="section-header">
        <h2>Cuentas de Ahorro</h2>
        <button class="btn-add" @click="openAhorroModal(null)">
          <i class="pi pi-plus"></i> Agregar
        </button>
      </div>

      <div class="config-list">
        <div v-for="item in ahorroList" :key="item.id" class="config-item" :style="{ borderLeftColor: item.color }">
          <div class="config-item-info">
            <span class="config-item-dot" :style="{ backgroundColor: item.color }"></span>
            <div>
              <span class="config-item-name">{{ item.name }}</span>
              <span class="config-item-desc">{{ item.description }} — {{ item.annual_rate }}% anual{{ item.rate_cap ? ' (tope $' + item.rate_cap + ', excedente ' + item.excess_rate + '%)' : '' }}</span>
            </div>
          </div>
          <div class="config-item-actions">
            <button class="btn-edit" @click="openAhorroModal(item)"><i class="pi pi-pencil"></i></button>
            <button class="btn-delete" @click="deleteAhorro(item.id)"><i class="pi pi-trash"></i></button>
          </div>
        </div>
        <div v-if="!ahorroList.length" class="config-empty">No hay cuentas de ahorro configuradas.</div>
      </div>
    </div>

    <!-- CREDITOS -->
    <div v-if="activeTab === 'creditos'" class="config-section">
      <div class="section-header">
        <h2>Tarjetas de Crédito</h2>
        <button class="btn-add" @click="openCreditoModal(null)">
          <i class="pi pi-plus"></i> Agregar
        </button>
      </div>

      <div class="config-list">
        <div v-for="item in creditosList" :key="item.id" class="config-item" :style="{ borderLeftColor: item.color }">
          <div class="config-item-info">
            <span class="config-item-dot" :style="{ backgroundColor: item.color }"></span>
            <div>
              <span class="config-item-name">{{ item.name }}</span>
            </div>
          </div>
          <div class="config-item-actions">
            <button class="btn-edit" @click="openCreditoModal(item)"><i class="pi pi-pencil"></i></button>
            <button class="btn-delete" @click="deleteCredito(item.id)"><i class="pi pi-trash"></i></button>
          </div>
        </div>
        <div v-if="!creditosList.length" class="config-empty">No hay tarjetas de crédito configuradas.</div>
      </div>
    </div>

    <!-- APORTACIONES -->
    <div v-if="activeTab === 'aportaciones'" class="config-section">
      <div class="section-header">
        <h2>Aportaciones Semanales</h2>
        <button class="btn-add" @click="openAportacionModal(null)">
          <i class="pi pi-plus"></i> Agregar
        </button>
      </div>

      <div class="config-list">
        <div v-for="item in aportacionesList" :key="item.id" class="config-item" :style="{ borderLeftColor: item.color }">
          <div class="config-item-info">
            <span class="config-item-dot" :style="{ backgroundColor: item.color }"></span>
            <div>
              <span class="config-item-name">{{ item.category }}{{ item.person ? ' — ' + item.person : '' }}</span>
              <span class="config-item-desc">${{ item.amount }}/semana</span>
            </div>
          </div>
          <div class="config-item-actions">
            <button class="btn-edit" @click="openAportacionModal(item)"><i class="pi pi-pencil"></i></button>
            <button class="btn-delete" @click="deleteAportacion(item.id)"><i class="pi pi-trash"></i></button>
          </div>
        </div>
        <div v-if="!aportacionesList.length" class="config-empty">No hay aportaciones configuradas.</div>
      </div>
    </div>

    <!-- MODAL AHORRO -->
    <div v-if="showAhorroModal" class="modal-overlay" @click.self="showAhorroModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ editingAhorro ? 'Editar' : 'Nueva' }} Cuenta de Ahorro</h3>
          <button class="btn-close" @click="showAhorroModal = false"><i class="pi pi-times"></i></button>
        </div>
        <div class="modal-body">
          <div class="form-field">
            <label>Banco / Nombre</label>
            <input type="text" v-model="ahorroForm.name" placeholder="Ej: Revolut, Nu..." />
          </div>
          <div class="form-field">
            <label>Descripción</label>
            <input type="text" v-model="ahorroForm.description" placeholder="Ej: Cuenta principal" />
          </div>
          <div class="form-field">
            <label>Tasa Anual (%)</label>
            <input type="number" step="0.01" min="0" v-model.number="ahorroForm.annualRate" placeholder="0.00" />
          </div>
          <div class="form-field">
            <label>Tope para tasa preferente ($)</label>
            <input type="number" step="0.01" min="0" v-model.number="ahorroForm.rateCap" placeholder="0 = sin tope" />
          </div>
          <div class="form-field">
            <label>Tasa sobre excedente (%)</label>
            <input type="number" step="0.01" min="0" v-model.number="ahorroForm.excessRate" placeholder="0.00" />
          </div>
          <div class="form-field">
            <label>Color</label>
            <div class="color-picker">
              <input type="color" v-model="ahorroForm.color" />
              <span class="color-preview" :style="{ backgroundColor: ahorroForm.color }">{{ ahorroForm.color }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showAhorroModal = false">Cancelar</button>
          <button class="btn-save" :disabled="!ahorroForm.name || saving" @click="saveAhorro">
            <i :class="saving ? 'pi pi-spin pi-spinner' : 'pi pi-check'"></i>
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL CREDITO -->
    <div v-if="showCreditoModal" class="modal-overlay" @click.self="showCreditoModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ editingCredito ? 'Editar' : 'Nueva' }} Tarjeta de Crédito</h3>
          <button class="btn-close" @click="showCreditoModal = false"><i class="pi pi-times"></i></button>
        </div>
        <div class="modal-body">
          <div class="form-field">
            <label>Nombre del Banco</label>
            <input type="text" v-model="creditoForm.name" placeholder="Ej: BBVA, Nu..." />
          </div>
          <div class="form-field">
            <label>Color</label>
            <div class="color-picker">
              <input type="color" v-model="creditoForm.color" />
              <span class="color-preview" :style="{ backgroundColor: creditoForm.color }">{{ creditoForm.color }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showCreditoModal = false">Cancelar</button>
          <button class="btn-save" :disabled="!creditoForm.name || saving" @click="saveCredito">
            <i :class="saving ? 'pi pi-spin pi-spinner' : 'pi pi-check'"></i>
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL APORTACION -->
    <div v-if="showAportacionModal" class="modal-overlay" @click.self="showAportacionModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ editingAportacion ? 'Editar' : 'Nueva' }} Aportación</h3>
          <button class="btn-close" @click="showAportacionModal = false"><i class="pi pi-times"></i></button>
        </div>
        <div class="modal-body">
          <div class="form-field">
            <label>Nombre / Categoría</label>
            <input type="text" v-model="aportacionForm.category" placeholder="Ej: GBM, Afore..." />
          </div>
          <div class="form-field">
            <label>Persona (opcional)</label>
            <input type="text" v-model="aportacionForm.person" placeholder="Ej: Adrian, Karime..." />
          </div>
          <div class="form-field">
            <label>Cantidad semanal ($)</label>
            <input type="number" step="1" min="1" v-model.number="aportacionForm.amount" placeholder="50" />
          </div>
          <div class="form-field">
            <label>Color</label>
            <div class="color-picker">
              <input type="color" v-model="aportacionForm.color" />
              <span class="color-preview" :style="{ backgroundColor: aportacionForm.color }">{{ aportacionForm.color }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showAportacionModal = false">Cancelar</button>
          <button class="btn-save" :disabled="!aportacionForm.category || !aportacionForm.amount || saving" @click="saveAportacion">
            <i :class="saving ? 'pi pi-spin pi-spinner' : 'pi pi-check'"></i>
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const activeTab = ref('ahorro')
const saving = ref(false)

// --- Ahorro ---
const ahorroList = ref([])
const showAhorroModal = ref(false)
const editingAhorro = ref(null)
const ahorroForm = ref({ name: '', description: '', annualRate: 0, color: '#1da1f2', rateCap: 0, excessRate: 0 })

async function loadAhorro() {
  const { data } = await axios.get('/api/config/ahorro')
  ahorroList.value = data
}

function openAhorroModal(item) {
  if (item) {
    editingAhorro.value = item
    ahorroForm.value = { name: item.name, description: item.description, annualRate: item.annual_rate, color: item.color, rateCap: item.rate_cap || 0, excessRate: item.excess_rate || 0 }
  } else {
    editingAhorro.value = null
    ahorroForm.value = { name: '', description: '', annualRate: 0, color: '#1da1f2', rateCap: 0, excessRate: 0 }
  }
  showAhorroModal.value = true
}

async function saveAhorro() {
  saving.value = true
  try {
    if (editingAhorro.value) {
      await axios.put(`/api/config/ahorro/${editingAhorro.value.id}`, ahorroForm.value)
    } else {
      await axios.post('/api/config/ahorro', ahorroForm.value)
    }
    showAhorroModal.value = false
    await loadAhorro()
  } catch (e) { console.error(e) }
  saving.value = false
}

async function deleteAhorro(id) {
  if (!confirm('¿Eliminar esta cuenta de ahorro?')) return
  await axios.delete(`/api/config/ahorro/${id}`)
  await loadAhorro()
}

// --- Creditos ---
const creditosList = ref([])
const showCreditoModal = ref(false)
const editingCredito = ref(null)
const creditoForm = ref({ name: '', color: '#1da1f2' })

async function loadCreditos() {
  const { data } = await axios.get('/api/config/creditos')
  creditosList.value = data
}

function openCreditoModal(item) {
  if (item) {
    editingCredito.value = item
    creditoForm.value = { name: item.name, color: item.color }
  } else {
    editingCredito.value = null
    creditoForm.value = { name: '', color: '#1da1f2' }
  }
  showCreditoModal.value = true
}

async function saveCredito() {
  saving.value = true
  try {
    if (editingCredito.value) {
      await axios.put(`/api/config/creditos/${editingCredito.value.id}`, creditoForm.value)
    } else {
      await axios.post('/api/config/creditos', creditoForm.value)
    }
    showCreditoModal.value = false
    await loadCreditos()
  } catch (e) { console.error(e) }
  saving.value = false
}

async function deleteCredito(id) {
  if (!confirm('¿Eliminar esta tarjeta de crédito?')) return
  await axios.delete(`/api/config/creditos/${id}`)
  await loadCreditos()
}

// --- Aportaciones ---
const aportacionesList = ref([])
const showAportacionModal = ref(false)
const editingAportacion = ref(null)
const aportacionForm = ref({ category: '', person: '', amount: 0, color: '#1da1f2' })

async function loadAportaciones() {
  const { data } = await axios.get('/api/config/aportaciones')
  aportacionesList.value = data
}

function openAportacionModal(item) {
  if (item) {
    editingAportacion.value = item
    aportacionForm.value = { category: item.category, person: item.person, amount: item.amount, color: item.color }
  } else {
    editingAportacion.value = null
    aportacionForm.value = { category: '', person: '', amount: 0, color: '#1da1f2' }
  }
  showAportacionModal.value = true
}

async function saveAportacion() {
  saving.value = true
  try {
    if (editingAportacion.value) {
      await axios.put(`/api/config/aportaciones/${editingAportacion.value.id}`, aportacionForm.value)
    } else {
      await axios.post('/api/config/aportaciones', aportacionForm.value)
    }
    showAportacionModal.value = false
    await loadAportaciones()
  } catch (e) { console.error(e) }
  saving.value = false
}

async function deleteAportacion(id) {
  if (!confirm('¿Eliminar esta aportación?')) return
  await axios.delete(`/api/config/aportaciones/${id}`)
  await loadAportaciones()
}

onMounted(() => {
  loadAhorro()
  loadCreditos()
  loadAportaciones()
})
</script>

<style scoped>
.configuracion {
  max-width: 1200px;
}

.page-title {
  color: #e1e8ed;
  font-size: 1.5rem;
  margin-bottom: 24px;
}

.config-tabs {
  display: flex;
  gap: 4px;
  background-color: #192734;
  border-radius: 10px;
  padding: 4px;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: #8899a6;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.tab-btn:hover { color: #e1e8ed; }
.tab-btn.active { background-color: #1c2b3a; color: #1da1f2; }

.config-section {
  background-color: #192734;
  border: 1px solid #2d3741;
  border-radius: 12px;
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  color: #e1e8ed;
  font-size: 1.1rem;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: #1da1f2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.2s;
}

.btn-add:hover { background-color: #1a91da; }

.config-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background-color: #1c2b3a;
  border-radius: 8px;
  border-left: 4px solid #1da1f2;
}

.config-item-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.config-item-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.config-item-name {
  color: #e1e8ed;
  font-weight: 500;
  display: block;
  font-size: 0.9rem;
}

.config-item-desc {
  color: #8899a6;
  font-size: 0.8rem;
  display: block;
  margin-top: 2px;
}

.config-item-actions {
  display: flex;
  gap: 8px;
}

.config-item-actions .btn-edit,
.config-item-actions .btn-delete {
  padding: 6px 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.config-item-actions .btn-edit {
  background-color: rgba(29, 161, 242, 0.15);
  color: #1da1f2;
}

.config-item-actions .btn-edit:hover { background-color: rgba(29, 161, 242, 0.3); }

.config-item-actions .btn-delete {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.config-item-actions .btn-delete:hover { background-color: rgba(239, 68, 68, 0.3); }

.config-empty {
  color: #8899a6;
  text-align: center;
  padding: 32px;
  font-size: 0.9rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-box {
  background-color: #192734;
  border: 1px solid #2d3741;
  border-radius: 12px;
  width: 100%;
  max-width: 440px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #2d3741;
}

.modal-header h3 {
  color: #e1e8ed;
  font-size: 1rem;
}

.btn-close {
  background: none;
  border: none;
  color: #8899a6;
  cursor: pointer;
  font-size: 1.1rem;
}

.btn-close:hover { color: #e1e8ed; }

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-field label {
  display: block;
  color: #8899a6;
  font-size: 0.8rem;
  margin-bottom: 6px;
}

.form-field input[type="text"],
.form-field input[type="number"] {
  width: 100%;
  padding: 10px 12px;
  background-color: #1c2b3a;
  border: 1px solid #2d3741;
  border-radius: 8px;
  color: #e1e8ed;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}

.form-field input:focus { border-color: #1da1f2; }

.color-picker {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-picker input[type="color"] {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  background: none;
}

.color-preview {
  padding: 4px 12px;
  border-radius: 6px;
  color: white;
  font-size: 0.8rem;
  font-family: monospace;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #2d3741;
}

.btn-cancel {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #2d3741;
  color: #8899a6;
  border-radius: 8px;
  cursor: pointer;
}

.btn-cancel:hover { border-color: #8899a6; color: #e1e8ed; }

.btn-save {
  padding: 8px 16px;
  background-color: #1da1f2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
}

.btn-save:hover { background-color: #1a91da; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 768px) {
  .config-tabs { flex-direction: column; }

  .configuracion {
    padding: 16px 0;
  }

  .config-section {
    padding: 16px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .btn-add {
    width: 100%;
    justify-content: center;
  }

  .config-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .config-item-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .modal-box {
    max-width: 95vw;
  }
}
</style>
