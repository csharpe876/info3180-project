<template>
  <div class="page">
    <div class="container">
      <h1 class="page-title">Your Matches</h1>
      <p class="page-sub">People who liked you back 💞</p>

      <div v-if="loading" class="spinner"></div>

      <div v-else-if="matches.length === 0" class="empty-state">
        <div class="emoji">💔</div>
        <h3>No matches yet</h3>
        <p>Keep liking profiles on the Dashboard!</p>
        <router-link to="/dashboard" class="btn btn-primary" style="margin-top:16px">Browse Profiles</router-link>
      </div>

      <div v-else class="matches-grid">
        <div v-for="m in matches" :key="m.id" class="match-card card">
          <div class="match-avatar">
            <img v-if="m.other_profile?.photo_url"
                 :src="`${m.other_profile.photo_url}`"
                 :alt="m.other_profile.full_name" />
            <div v-else class="avatar-placeholder">
              {{ initials(m.other_profile) }}
            </div>
            <span class="online-dot"></span>
          </div>

          <div class="match-info">
            <h3>{{ m.other_profile?.full_name }}, {{ m.other_profile?.age }}</h3>
            <p class="muted">{{ m.other_profile?.parish }}, {{ m.other_profile?.country }}</p>
            <p class="match-bio">{{ m.other_profile?.bio }}</p>
            <div class="interest-tags">
              <span v-for="i in (m.other_profile?.interests || []).slice(0, 3)"
                    :key="i" class="badge badge-rose">{{ i }}</span>
            </div>
            <p class="match-date">Matched {{ formatDate(m.matched_at) }}</p>
          </div>

          <router-link :to="`/messages/${m.id}`" class="btn btn-primary msg-btn">
            💬 Message
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMatches } from '../services/api'

const matches = ref([])
const loading = ref(true)

function initials(p) {
  if (!p) return '?'
  return (p.first_name?.[0] || '') + (p.last_name?.[0] || '')
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-JM', { month: 'short', day: 'numeric', year: 'numeric' })
}

onMounted(async () => {
  try {
    const { data } = await getMatches()
    matches.value = data.matches
  } catch {}
  loading.value = false
})
</script>

<style scoped>
.page { padding: 32px 24px; min-height: calc(100vh - 60px); background: var(--cream); }
.container { max-width: 860px; margin: 0 auto; }
.page-title { font-size: 2rem; margin-bottom: 4px; }
.page-sub   { color: var(--muted); margin-bottom: 28px; }

.matches-grid { display: flex; flex-direction: column; gap: 16px; }
.match-card {
  display: flex; align-items: center; gap: 20px; padding: 20px 24px;
  transition: box-shadow 0.2s;
}
.match-card:hover { box-shadow: var(--shadow-lg); }

.match-avatar { position: relative; flex-shrink: 0; }
.match-avatar img, .avatar-placeholder {
  width: 76px; height: 76px; border-radius: 50%; object-fit: cover;
}
.avatar-placeholder {
  background: linear-gradient(135deg, var(--rose), var(--rose2));
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.3rem;
}
.online-dot {
  position: absolute; bottom: 2px; right: 2px;
  width: 12px; height: 12px; background: #34d399;
  border: 2px solid #fff; border-radius: 50%;
}
.match-info { flex: 1; }
.match-info h3 { font-size: 1.1rem; margin-bottom: 3px; font-family: 'DM Sans', sans-serif; font-weight: 600; }
.match-bio { font-size: 0.87rem; color: var(--muted); margin: 5px 0; line-height: 1.5; }
.interest-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 6px; }
.match-date { font-size: 0.78rem; color: var(--muted); }

.msg-btn { white-space: nowrap; flex-shrink: 0; }
.muted { color: var(--muted); font-size: 0.84rem; }

@media (max-width: 600px) {
  .match-card { flex-wrap: wrap; }
  .msg-btn { width: 100%; }
}
</style>
