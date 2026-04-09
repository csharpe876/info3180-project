<template>
  <div class="page">
    <div class="container">
      <div class="admin-header">
        <h1 class="page-title">⚙️ Admin Dashboard</h1>
        <p class="page-sub">Site moderation & statistics</p>
      </div>

      <div v-if="!isAdmin" class="error-msg" style="margin-top:20px">
        Access denied. Admin only.
      </div>

      <template v-else>
        <!-- Stats cards -->
        <div class="stats-grid">
          <div class="stat-card card" v-for="s in stats" :key="s.label">
            <div class="stat-icon">{{ s.icon }}</div>
            <div class="stat-val">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
          <button v-for="t in tabs" :key="t.key"
                  class="tab-btn" :class="{ active: activeTab === t.key }"
                  @click="activeTab = t.key">{{ t.label }}</button>
        </div>

        <!-- Users tab -->
        <div v-if="activeTab === 'users'" class="tab-panel card">
          <h2 class="panel-title">All Users</h2>
          <div v-if="loadingUsers" class="spinner"></div>
          <table v-else class="admin-table">
            <thead>
              <tr><th>ID</th><th>Username</th><th>Email</th><th>Joined</th><th>Profile</th><th>Action</th></tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>#{{ u.id }}</td>
                <td><strong>{{ u.username }}</strong></td>
                <td>{{ u.email }}</td>
                <td>{{ formatDate(u.created_at) }}</td>
                <td>
                  <span v-if="u.profile" class="badge badge-navy">Has Profile</span>
                  <span v-else class="badge" style="background:#fee2e2;color:#991b1b">No Profile</span>
                </td>
                <td>
                  <button v-if="u.id !== authUser.id"
                          class="btn btn-ghost del-btn"
                          @click="deleteUser(u)">🗑 Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Reports tab -->
        <div v-if="activeTab === 'reports'" class="tab-panel card">
          <div class="panel-header">
            <h2 class="panel-title">Reports</h2>
            <div class="status-filter">
              <button v-for="s in ['pending','reviewed','dismissed']" :key="s"
                      class="status-btn" :class="{ active: reportStatus === s }"
                      @click="reportStatus = s; loadReports()">{{ s }}</button>
            </div>
          </div>
          <div v-if="loadingReports" class="spinner"></div>
          <div v-else-if="reports.length === 0" class="empty-state" style="padding:30px">
            <div class="emoji">✅</div>
            <h3>No {{ reportStatus }} reports</h3>
          </div>
          <div v-else class="reports-list">
            <div v-for="r in reports" :key="r.id" class="report-item">
              <div class="report-info">
                <p><strong>User #{{ r.reported_id }}</strong> ({{ r.reported_username }}) reported for
                   <span class="badge badge-gold">{{ r.reason }}</span></p>
                <p v-if="r.details" class="muted sm">{{ r.details }}</p>
                <p class="muted sm">{{ formatDate(r.created_at) }}</p>
              </div>
              <div v-if="r.status === 'pending'" class="report-actions">
                <button class="btn btn-navy" style="font-size:0.8rem;padding:6px 14px"
                        @click="resolveReport(r, 'reviewed')">Mark Reviewed</button>
                <button class="btn btn-ghost" style="font-size:0.8rem"
                        @click="resolveReport(r, 'dismissed')">Dismiss</button>
              </div>
              <span v-else class="badge" :class="r.status === 'reviewed' ? 'badge-navy' : 'badge-rose'">
                {{ r.status }}
              </span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

const auth        = useAuthStore()
const authUser    = computed(() => auth.user)
const isAdmin     = computed(() => auth.user?.id === 1)
const activeTab   = ref('users')
const tabs        = [{ key: 'users', label: '👥 Users' }, { key: 'reports', label: '🚨 Reports' }]

// Stats
const statData     = ref({})
const stats        = computed(() => [
  { icon: '👥', label: 'Total Users',    value: statData.value.total_users    ?? '–' },
  { icon: '💞', label: 'Total Matches',  value: statData.value.total_matches  ?? '–' },
  { icon: '💬', label: 'Messages Sent',  value: statData.value.total_messages ?? '–' },
  { icon: '🚨', label: 'Pending Reports',value: statData.value.pending_reports?? '–' },
  { icon: '👍', label: 'Total Likes',    value: statData.value.total_likes    ?? '–' },
  { icon: '🆕', label: 'New (7 days)',   value: statData.value.new_users_7d   ?? '–' },
])

// Users
const users        = ref([])
const loadingUsers = ref(false)

// Reports
const reports        = ref([])
const loadingReports = ref(false)
const reportStatus   = ref('pending')

function formatDate(iso) {
  if (!iso) return '–'
  return new Date(iso).toLocaleDateString('en-JM', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function loadStats() {
  try { const { data } = await api.get('/admin/stats'); statData.value = data } catch {}
}

async function loadUsers() {
  loadingUsers.value = true
  try { const { data } = await api.get('/admin/users'); users.value = data.users } catch {}
  loadingUsers.value = false
}

async function loadReports() {
  loadingReports.value = true
  try {
    const { data } = await api.get('/admin/reports', { params: { status: reportStatus.value } })
    reports.value = data.reports
  } catch {}
  loadingReports.value = false
}

async function deleteUser(u) {
  if (!confirm(`Delete user "${u.username}"? This cannot be undone.`)) return
  try {
    await api.delete(`/admin/users/${u.id}`)
    users.value = users.value.filter(x => x.id !== u.id)
    await loadStats()
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to delete user.')
  }
}

async function resolveReport(r, status) {
  try {
    await api.put(`/admin/reports/${r.id}`, { status })
    reports.value = reports.value.filter(x => x.id !== r.id)
    await loadStats()
  } catch {}
}

onMounted(async () => {
  if (!isAdmin.value) return
  await Promise.all([loadStats(), loadUsers(), loadReports()])
})
</script>

<style scoped>
.page { padding: 32px 24px; background: var(--cream); min-height: calc(100vh - 60px); }
.container { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
.page-title { font-size: 2rem; margin-bottom: 4px; }
.page-sub   { color: var(--muted); }

.stats-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px;
}
.stat-card { padding: 20px 16px; text-align: center; }
.stat-icon  { font-size: 1.6rem; margin-bottom: 6px; }
.stat-val   { font-size: 2rem; font-weight: 700; color: var(--navy); font-family: 'Playfair Display', serif; }
.stat-label { font-size: 0.78rem; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

.tabs { display: flex; gap: 8px; }
.tab-btn {
  padding: 9px 20px; border-radius: 8px; font-size: 0.9rem; font-weight: 600;
  border: 1.5px solid #e2e8f0; background: #fff; color: var(--muted); cursor: pointer;
  transition: all 0.15s;
}
.tab-btn.active { background: var(--navy); color: #fff; border-color: var(--navy); }

.tab-panel { padding: 24px; }
.panel-title { font-size: 1.2rem; margin-bottom: 18px; }
.panel-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; flex-wrap: wrap; gap: 10px; }
.panel-header .panel-title { margin-bottom: 0; }

.admin-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.admin-table th { text-align: left; padding: 8px 12px; background: var(--cream2); font-size: 0.75rem;
                  text-transform: uppercase; letter-spacing: 0.05em; color: var(--navy3); }
.admin-table td { padding: 10px 12px; border-bottom: 1px solid var(--cream2); }
.admin-table tr:last-child td { border-bottom: none; }
.admin-table tr:hover td { background: var(--cream); }
.del-btn { color: #dc2626; font-size: 0.82rem; padding: 5px 10px; }
.del-btn:hover { background: #fee2e2; }

.status-filter { display: flex; gap: 6px; }
.status-btn {
  padding: 5px 14px; border-radius: 50px; font-size: 0.8rem; font-weight: 600;
  border: 1.5px solid #e2e8f0; background: #fff; color: var(--muted); cursor: pointer; text-transform: capitalize;
}
.status-btn.active { background: var(--navy); color: #fff; border-color: var(--navy); }

.reports-list { display: flex; flex-direction: column; gap: 12px; }
.report-item {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 14px 16px; background: var(--cream); border-radius: 8px; flex-wrap: wrap;
}
.report-info { flex: 1; }
.report-info p { font-size: 0.9rem; margin-bottom: 3px; }
.report-actions { display: flex; gap: 8px; }

.muted { color: var(--muted); }
.sm    { font-size: 0.8rem; }

@media (max-width: 600px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .admin-table { font-size: 0.78rem; }
}
</style>
