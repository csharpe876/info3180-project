<template>
  <div class="page">
    <div class="container">

      <!-- User summary -->
      <div v-if="myProfile" class="my-card card">
        <div class="my-avatar">
          <img v-if="myProfile.photo_url" :src="`${myProfile.photo_url}`" alt="me" />
          <div v-else class="avatar-placeholder">{{ initials }}</div>
        </div>
        <div class="my-info">
          <h2>Welcome, {{ myProfile.first_name }}!</h2>
          <p class="muted">{{ myProfile.parish }}, {{ myProfile.country }} &nbsp;·&nbsp; Age {{ myProfile.age }}</p>
          <p v-if="myProfile.bio" class="bio-snippet">{{ myProfile.bio }}</p>
        </div>
        <router-link to="/profile" class="btn btn-outline">Edit Profile</router-link>
      </div>

      <!-- Filters -->
      <div class="filters card">
        <input v-model="search.q"      class="f-input" placeholder="Search by name or bio…" />
        <select v-model="search.age_range" class="f-select">
          <option value="">All Ages</option>
          <option value="18-25">18 – 25</option>
          <option value="26-35">26 – 35</option>
          <option value="36-50">36 – 50</option>
          <option value="51-99">51+</option>
        </select>
        <input v-model="search.parish" class="f-input" placeholder="Filter by parish…" />
        <button class="btn btn-primary" @click="loadProfiles">Search</button>
        <button class="btn btn-ghost"   @click="resetFilters">Reset</button>
      </div>

      <!-- Profile cards -->
      <h2 class="section-title">Browse Potential Matches</h2>

      <div v-if="loading" class="spinner"></div>

      <div v-else-if="profiles.length === 0" class="empty-state">
        <div class="emoji">🌊</div>
        <h3>No more profiles to browse</h3>
        <p>Check back later or adjust your filters.</p>
      </div>

      <div v-else class="profiles-list">
        <div v-for="p in profiles" :key="p.id" class="profile-row card">
          <div class="prow-avatar">
            <img v-if="p.photo_url" :src="`${p.photo_url}`" :alt="p.full_name" />
            <div v-else class="avatar-placeholder sm">{{ initials2(p) }}</div>
          </div>
          <div class="prow-info">
            <h3>{{ p.full_name }}, {{ p.age }}</h3>
            <p class="muted sm">{{ p.parish }}, {{ p.country }}</p>
            <p class="prow-bio">{{ p.bio }}</p>
            <div class="interest-tags">
              <span v-for="i in p.interests.slice(0,4)" :key="i" class="badge badge-rose">{{ i }}</span>
            </div>
            <p class="match-score">Match Score: <strong>{{ p.match_score }}%</strong></p>
          </div>
          <div class="prow-actions">
            <button class="btn btn-primary act-btn" @click="act(p, 'like')" :disabled="acted[p.user_id]">
              👍 Like
            </button>
            <button class="btn btn-ghost act-btn" @click="act(p, 'pass')" :disabled="acted[p.user_id]">
              Pass
            </button>
            <button class="btn btn-ghost act-btn icon-btn" @click="bookmark(p)" :title="bookmarked[p.id] ? 'Saved!' : 'Save profile'">
              {{ bookmarked[p.id] ? '🔖' : '🏷️' }}
            </button>
            <button class="btn btn-ghost act-btn icon-btn" @click="report(p)" title="Report user">
              🚩
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useProfileStore } from '../stores/profile'
import { getProfiles, likeProfile, addFavourite, reportUser } from '../services/api'

const auth          = useAuthStore()
const profileStore  = useProfileStore()
const myProfile     = computed(() => profileStore.myProfile)
const profiles      = ref([])
const loading   = ref(false)
const acted      = reactive({})   // track acted-on profiles this session
const bookmarked = reactive({})   // track bookmarked profiles

const search = reactive({ q: '', age_range: '', parish: '' })

const initials = computed(() => {
  if (!myProfile.value) return '?'
  return (myProfile.value.first_name?.[0] || '') + (myProfile.value.last_name?.[0] || '')
})

function initials2(p) {
  return (p.first_name?.[0] || '') + (p.last_name?.[0] || '')
}

function buildParams() {
  const p = {}
  if (search.q)      p.q      = search.q
  if (search.parish) p.parish = search.parish
  if (search.age_range) {
    const [mn, mx] = search.age_range.split('-')
    p.age_min = mn; p.age_max = mx
  }
  return p
}

async function loadProfiles() {
  loading.value = true
  try {
    const { data } = await getProfiles(buildParams())
    profiles.value = data.profiles
  } catch {}
  loading.value = false
}

function resetFilters() {
  search.q = ''; search.age_range = ''; search.parish = ''
  loadProfiles()
}

async function bookmark(profile) {
  bookmarked[profile.id] = true
  try { await addFavourite(profile.id) } catch { delete bookmarked[profile.id] }
}

async function report(profile) {
  const reason = prompt("Report reason (spam / harassment / fake / inappropriate / other):")
  if (!reason) return
  const details = prompt("Any additional details? (optional)") || ""
  try {
    await reportUser(profile.user_id, reason.trim(), details.trim())
    alert("Report submitted. Thank you!")
  } catch (e) {
    alert(e.response?.data?.error || "Failed to submit report.")
  }
}

async function act(profile, action) {
  acted[profile.user_id] = true
  try {
    await likeProfile(profile.user_id, action)
    // Remove from list smoothly
    profiles.value = profiles.value.filter(p => p.user_id !== profile.user_id)
  } catch {
    delete acted[profile.user_id]
  }
}

onMounted(async () => {
  if (!profileStore.myProfile) {
    await profileStore.fetchMyProfile(auth.user.id)
  }
  loadProfiles()
})
</script>

<style scoped>
.page { padding: 32px 24px; min-height: calc(100vh - 60px); background: var(--cream); }
.container { max-width: 860px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }

.my-card {
  display: flex; align-items: center; gap: 20px; padding: 20px 24px; flex-wrap: wrap;
}
.my-avatar img, .my-avatar .avatar-placeholder {
  width: 64px; height: 64px; border-radius: 50%; object-fit: cover; flex-shrink: 0;
}
.my-info { flex: 1; }
.my-info h2 { font-size: 1.3rem; margin-bottom: 4px; }
.bio-snippet { font-size: 0.88rem; color: var(--muted); margin-top: 4px; }

.filters {
  display: flex; gap: 10px; padding: 16px 20px; flex-wrap: wrap; align-items: center;
}
.f-input, .f-select {
  padding: 9px 13px; border: 1.5px solid #e2e8f0; border-radius: 8px;
  font-size: 0.88rem; background: #f8fafc; font-family: 'DM Sans', sans-serif;
  flex: 1; min-width: 140px;
}
.f-input:focus, .f-select:focus { outline: none; border-color: var(--rose); }

.section-title { font-size: 1.3rem; color: var(--navy); }

.profiles-list { display: flex; flex-direction: column; gap: 14px; }
.profile-row {
  display: flex; align-items: center; gap: 18px; padding: 18px 20px;
  transition: box-shadow 0.2s;
}
.profile-row:hover { box-shadow: var(--shadow-lg); }
.prow-avatar img, .prow-avatar .avatar-placeholder {
  width: 70px; height: 70px; border-radius: 12px; object-fit: cover; flex-shrink: 0;
}
.prow-info { flex: 1; }
.prow-info h3 { font-size: 1.05rem; margin-bottom: 2px; font-family: 'DM Sans', sans-serif; font-weight: 600; }
.prow-bio { font-size: 0.87rem; color: var(--muted); margin: 4px 0; line-height: 1.5; }
.interest-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
.match-score { font-size: 0.8rem; color: var(--rose); margin-top: 6px; }
.prow-actions { display: flex; flex-direction: column; gap: 8px; flex-shrink: 0; }
.act-btn { padding: 8px 18px; font-size: 0.88rem; }

.avatar-placeholder {
  background: linear-gradient(135deg, var(--rose), var(--rose2));
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.2rem; border-radius: 50%;
}
.avatar-placeholder.sm { border-radius: 12px; font-size: 1rem; }
.muted { color: var(--muted); font-size: 0.85rem; }
.sm { font-size: 0.82rem; }

@media (max-width: 600px) {
  .my-card { flex-direction: column; text-align: center; }
  .profile-row { flex-wrap: wrap; }
  .prow-actions { flex-direction: row; width: 100%; }
}
</style>