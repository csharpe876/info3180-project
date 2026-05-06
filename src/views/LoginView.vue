<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <div class="auth-logo">💞</div>
        <h1>Welcome back</h1>
        <p>Sign in to continue your journey</p>
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-field">
          <label>Email</label>
          <input v-model="form.email" type="email" placeholder="you@example.com" required />
        </div>
        <div class="form-field">
          <label>Password</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%;margin-top:8px" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign In' }}
        </button>
      </form>

      <p class="auth-switch">
        Don't have an account?
        <router-link to="/register">Sign up here</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth    = useAuthStore()
const router  = useRouter()
const loading = ref(false)
const error   = ref('')
const form    = reactive({ email: '', password: '' })

async function handleLogin() {
  error.value   = ''
  loading.value = true
  try {
    await auth.login(form.email, form.password)
    router.push('/dashboard')
  } catch (e) {
    const d = e.response?.data
    error.value = d?.error || (Array.isArray(d?.errors) ? d.errors.join(', ') : null) || e.message || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: var(--navy); padding: 24px;
}
.auth-card {
  width: 100%; max-width: 420px; padding: 40px 36px;
}
.auth-header { text-align: center; margin-bottom: 28px; }
.auth-logo { font-size: 2.4rem; margin-bottom: 12px; }
.auth-header h1 { font-size: 1.9rem; color: var(--navy); margin-bottom: 6px; }
.auth-header p  { color: var(--muted); font-size: 0.92rem; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.auth-switch { text-align: center; margin-top: 20px; font-size: 0.88rem; color: var(--muted); }
.auth-switch a { color: var(--rose); font-weight: 600; }
.auth-switch a:hover { text-decoration: underline; }
.error-msg { margin-bottom: 16px; }
</style>
