import axios from 'axios'

const api = axios.create({
  // In dev: Vite proxy forwards /api → http://localhost:5000
  // In prod: set VITE_API_BASE in .env (e.g. https://yourapp.onrender.com/api/v1)
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Global 401 handler — clear stale token and redirect to login
api.interceptors.response.use(
  res => res,
  err => {
    const isAuthEndpoint = err.config?.url?.includes('/auth/')
    if (err.response?.status === 401 && !isAuthEndpoint) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────
export const register = (data) => api.post('/auth/register', data)
export const login    = (data) => api.post('/auth/login',    data)
export const logout   = ()     => api.post('/auth/logout')

// ── Profiles ──────────────────────────────────────────────
export const getProfiles   = (params) => api.get('/profiles', { params })
export const getProfile    = (uid)    => api.get(`/profiles/${uid}`)
export const updateProfile = (uid, data) => {
  if (data instanceof FormData) {
    return api.put(`/profiles/${uid}`, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  }
  return api.put(`/profiles/${uid}`, data)
}

// ── Likes & Matching ──────────────────────────────────────
export const likeProfile = (uid, action) => api.post(`/profiles/${uid}/like`, { action })
export const getMatches  = ()            => api.get('/matches')

// ── Messaging ─────────────────────────────────────────────
export const getConversations = ()            => api.get('/conversations')
export const getMessages      = (matchId)     => api.get(`/matches/${matchId}/messages`)
export const sendMessage      = (matchId, body) => api.post(`/matches/${matchId}/messages`, { body })

// ── Favourites ────────────────────────────────────────────
export const getFavourites   = ()    => api.get('/favourites')
export const addFavourite    = (pid) => api.post(`/favourites/${pid}`)
export const removeFavourite = (pid) => api.delete(`/favourites/${pid}`)

// ── Interests ─────────────────────────────────────────────
export const getInterests = () => api.get('/interests')

// ── Report & Block ────────────────────────────────────────
export const reportUser  = (uid, reason, details) => api.post(`/users/${uid}/report`, { reason, details })
export const blockUser   = (uid) => api.post(`/users/${uid}/block`)
export const unblockUser = (uid) => api.delete(`/users/${uid}/block`)
export const getBlocks   = ()    => api.get('/blocks')

export default api
