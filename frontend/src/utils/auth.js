// Gestión de autenticación en el cliente.
// La contraseña se valida en el backend contra un hash scrypt almacenado en la DB.
import axios from 'axios'

const TOKEN_KEY = 'fin_token'

export function isAuthenticated() {
  return !!sessionStorage.getItem(TOKEN_KEY)
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY)
}

/**
 * Valida la contraseña contra el backend.
 * Devuelve { success: true } o lanza un Error con el mensaje del backend.
 */
export async function login(password) {
  const { data } = await axios.post('/api/auth/login', { password })
  if (data?.token) {
    sessionStorage.setItem(TOKEN_KEY, data.token)
  }
  return data
}

export function logout() {
  sessionStorage.removeItem(TOKEN_KEY)
}
