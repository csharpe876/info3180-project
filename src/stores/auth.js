import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, logout as apiLogout } from '../services/api'
import { useProfileStore } from './profile'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user  = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  function setAuth(t, u) {
    token.value = t
    user.value  = u
    localStorage.setItem('token', t)
    localStorage.setItem('user',  JSON.stringify(u))
  }

  function clearAuth() {
    token.value = null
    user.value  = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function login(email, password) {
    const { data } = await apiLogin({ email, password })
    setAuth(data.token, data.user)
    return data
  }

  async function register(payload) {
    const { data } = await apiRegister(payload)
    setAuth(data.token, data.user)
    return data
  }

  async function logout() {
    try { await apiLogout() } catch {}
    clearAuth()
    // Clear cached profile so next login starts fresh
    try { useProfileStore().clearProfile() } catch {}
  }

  return { token, user, isLoggedIn, login, register, logout }
})