<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <div class="auth-logo">💞</div>
        <h1>Create account</h1>
        <p>Start finding your perfect match</p>
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="row-2">
          <div class="form-field">
            <label>First Name</label>
            <input v-model="form.first_name" placeholder="First name" required />
          </div>
          <div class="form-field">
            <label>Last Name</label>
            <input v-model="form.last_name" placeholder="Last name" required />
          </div>
        </div>
        <div class="form-field">
          <label>Username</label>
          <input v-model="form.username" placeholder="username" required />
        </div>
        <div class="form-field">
          <label>Email</label>
          <input v-model="form.email" type="email" placeholder="you@example.com" required />
        </div>
        <div class="form-field">
          <label>Date of Birth</label>
          <input v-model="form.date_of_birth" type="date" required />
        </div>
        <div class="row-2">
          <div class="form-field">
            <label>Gender</label>
            <select v-model="form.gender" required>
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="non-binary">Non-Binary</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="form-field">
            <label>Looking For</label>
            <select v-model="form.looking_for">
              <option value="any">Any</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="non-binary">Non-Binary</option>
            </select>
          </div>
        </div>
        <div class="form-field">
          <label>Password</label>
          <input v-model="form.password" type="password" placeholder="Min. 6 characters" required minlength="6" />
        </div>

        <button type="submit" class="btn btn-primary" style="width:100%;margin-top:8px" :disabled="loading">
          {{ loading ? 'Creating account…' : 'Sign Up' }}
        </button>
      </form>

      <p class="auth-switch">
        Already have an account?
        <router-link to="/login">Login here</router-link>
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
const form    = reactive({
  first_name: '', last_name: '', username: '',
  email: '', password: '', date_of_birth: '',
  gender: '', looking_for: 'any',
})

async function handleRegister() {
  error.value   = ''
  loading.value = true
  try {
    await auth.register({ ...form })
    router.push('/profile')
  } catch (e) {
    const d = e.response?.data
    error.value = d?.error || (d?.errors?.join(', ')) || 'Registration failed.'
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
.auth-card { width: 100%; max-width: 460px; padding: 36px; }
.auth-header { text-align: center; margin-bottom: 24px; }
.auth-logo { font-size: 2.2rem; margin-bottom: 10px; }
.auth-header h1 { font-size: 1.8rem; margin-bottom: 4px; }
.auth-header p  { color: var(--muted); font-size: 0.9rem; }
.auth-form { display: flex; flex-direction: column; gap: 14px; }
.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.auth-switch { text-align: center; margin-top: 18px; font-size: 0.88rem; color: var(--muted); }
.auth-switch a { color: var(--rose); font-weight: 600; }
.auth-switch a:hover { text-decoration: underline; }
.error-msg { margin-bottom: 14px; }
</style>
