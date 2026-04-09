<template>
  <div class="page">
    <div class="container">
      <h1 class="page-title">Saved Profiles</h1>
      <p class="page-sub">Profiles you've bookmarked 🔖</p>

      <div v-if="loading" class="spinner"></div>

      <div v-else-if="favourites.length === 0" class="empty-state">
        <div class="emoji">🔖</div>
        <h3>No saved profiles yet</h3>
        <p>Bookmark profiles from the dashboard to find them here.</p>
        <router-link to="/dashboard" class="btn btn-primary" style="margin-top:16px">Browse Profiles</router-link>
      </div>

      <div v-else class="fav-grid">
        <div v-for="p in favourites" :key="p.id" class="fav-card card">
          <button class="remove-btn" title="Remove bookmark" @click="remove(p)">✕</button>

          <div class="fav-avatar">
            <img v-if="p.photo_url" :src="`${p.photo_url}`" :alt="p.full_name" />
            <div v-else class="avatar-placeholder">{{ initials(p) }}</div>
          </div>

          <div class="fav-info">
            <h3>{{ p.full_name }}, {{ p.age }}</h3>
            <p class="muted">{{ p.parish }}, {{ p.country }}</p>
            <p class="fav-bio">{{ p.bio }}</p>
            <div class="interest-tags">
              <span v-for="i in (p.interests || []).slice(0, 3)" :key="i" class="badge badge-rose">{{ i }}</span>
            </div>
          </div>

          <div class="fav-actions">
            <button class="btn btn-primary act-btn" @click="like(p)" :disabled="acted[p.user_id]">
              {{ acted[p.user_id] === 'like' ? '✓ Liked' : '👍 Like' }}
            </button>
            <button class="btn btn-ghost act-btn" @click="like(p, 'pass')" :disabled="acted[p.user_id]">
              Pass
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getFavourites, removeFavourite, likeProfile } from '../services/api'

const favourites = ref([])
const loading    = ref(true)
const acted      = reactive({})

function initials(p) {
  return (p.first_name?.[0] || '') + (p.last_name?.[0] || '')
}

async function remove(profile) {
  try {
    await removeFavourite(profile.id)
    favourites.value = favourites.value.filter(f => f.id !== profile.id)
  } catch {}
}

async function like(profile, action = 'like') {
  acted[profile.user_id] = action
  try {
    await likeProfile(profile.user_id, action)
  } catch {
    delete acted[profile.user_id]
  }
}

onMounted(async () => {
  try {
    const { data } = await getFavourites()
    favourites.value = data.favourites
  } catch {}
  loading.value = false
})
</script>

<style scoped>
.page { padding: 32px 24px; background: var(--cream); min-height: calc(100vh - 60px); }
.container { max-width: 960px; margin: 0 auto; }
.page-title { font-size: 2rem; margin-bottom: 4px; }
.page-sub   { color: var(--muted); margin-bottom: 28px; }

.fav-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px;
}
.fav-card { padding: 20px; position: relative; transition: box-shadow 0.2s; }
.fav-card:hover { box-shadow: var(--shadow-lg); }

.remove-btn {
  position: absolute; top: 12px; right: 12px;
  background: none; border: none; color: var(--muted);
  font-size: 0.85rem; cursor: pointer; padding: 4px 6px;
  border-radius: 50%; transition: background 0.15s, color 0.15s;
}
.remove-btn:hover { background: var(--rose3); color: var(--rose); }

.fav-avatar { margin-bottom: 12px; }
.fav-avatar img, .avatar-placeholder {
  width: 64px; height: 64px; border-radius: 50%; object-fit: cover;
}
.avatar-placeholder {
  background: linear-gradient(135deg, var(--rose), var(--rose2));
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.2rem;
}
.fav-info h3 { font-size: 1rem; margin-bottom: 2px; font-family: 'DM Sans', sans-serif; font-weight: 600; }
.fav-bio { font-size: 0.84rem; color: var(--muted); margin: 5px 0; line-height: 1.5;
           display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.interest-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
.fav-actions { display: flex; gap: 8px; margin-top: 14px; }
.act-btn { flex: 1; padding: 8px 12px; font-size: 0.85rem; }
.muted { color: var(--muted); font-size: 0.83rem; }
</style>
