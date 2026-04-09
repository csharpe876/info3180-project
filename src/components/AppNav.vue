<template>
  <nav class="nav">
    <div class="nav-inner">
      <router-link to="/dashboard" class="nav-brand">
        <span class="brand-icon">💞</span>
        <span class="brand-name">DriftDater</span>
      </router-link>

      <div class="nav-links">
        <router-link to="/dashboard"  class="nav-link">Dashboard</router-link>
        <router-link to="/matches"    class="nav-link">
          Matches
          <span v-if="matchCount > 0" class="match-badge">{{ matchCount }}</span>
        </router-link>
        <router-link to="/messages"   class="nav-link">Messages</router-link>
        <router-link to="/favourites" class="nav-link">Saved</router-link>
        <router-link to="/profile"    class="nav-link">Profile</router-link>
        <router-link v-if="isAdmin" to="/admin" class="nav-link admin-link">Admin</router-link>
        <button class="btn btn-outline btn-sm" @click="handleLogout">Logout</button>
      </div>

      <button class="hamburger" @click="open = !open" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
    </div>

    <div class="mobile-menu" :class="{ active: open }">
      <router-link to="/dashboard"  class="mob-link" @click="open=false">Dashboard</router-link>
      <router-link to="/matches"    class="mob-link" @click="open=false">Matches</router-link>
      <router-link to="/messages"   class="mob-link" @click="open=false">Messages</router-link>
      <router-link to="/favourites" class="mob-link" @click="open=false">Saved</router-link>
      <router-link to="/profile"    class="mob-link" @click="open=false">Profile</router-link>
      <router-link v-if="isAdmin" to="/admin" class="mob-link" @click="open=false">⚙️ Admin</router-link>
      <button class="btn btn-primary" style="width:100%;margin-top:8px" @click="handleLogout">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getMatches } from '../services/api'

const auth       = useAuthStore()
const router     = useRouter()
const route      = useRoute()
const open       = ref(false)
const matchCount = ref(0)
const isAdmin    = computed(() => auth.user?.id === 1)

// Refresh match count whenever route changes (catches new matches from liking)
async function refreshCount() {
  try {
    const { data } = await getMatches()
    matchCount.value = data.total || 0
  } catch {}
}

// Watch route changes to keep the badge fresh
import { watch } from 'vue'
watch(() => route.path, refreshCount)

onMounted(refreshCount)

async function handleLogout() {
  open.value = false
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav {
  background: var(--navy);
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 2px 16px rgba(15,23,42,0.25);
}
.nav-inner {
  max-width: 1100px; margin: 0 auto;
  padding: 0 24px; height: 60px;
  display: flex; align-items: center; justify-content: space-between;
}
.nav-brand {
  display: flex; align-items: center; gap: 8px;
  font-family: 'Playfair Display', serif; font-size: 1.25rem;
  color: var(--white); font-weight: 700;
}
.brand-icon { font-size: 1.4rem; }
.nav-links { display: flex; align-items: center; gap: 2px; }
.nav-link {
  position: relative; padding: 6px 12px; border-radius: 6px;
  color: rgba(255,255,255,0.7); font-size: 0.88rem; font-weight: 500;
  transition: color 0.2s, background 0.2s;
}
.nav-link:hover, .nav-link.router-link-active { color: #fff; background: rgba(255,255,255,0.1); }
.admin-link { color: var(--gold) !important; }
.admin-link:hover { background: rgba(245,158,11,0.15) !important; }
.match-badge {
  position: absolute; top: 0; right: 0;
  background: var(--rose); color: #fff;
  font-size: 0.6rem; font-weight: 700;
  width: 15px; height: 15px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transform: translate(30%, -30%);
}
.btn-sm { padding: 7px 16px; font-size: 0.82rem; margin-left: 6px; }
.hamburger { display: none; flex-direction: column; gap: 5px; background: none; padding: 4px; }
.hamburger span { display: block; width: 22px; height: 2px; background: rgba(255,255,255,0.8); border-radius: 2px; }
.mobile-menu {
  display: none; padding: 12px 24px 16px;
  background: var(--navy2); border-top: 1px solid rgba(255,255,255,0.08);
}
.mob-link { display: block; padding: 10px 0; color: rgba(255,255,255,0.8); font-size: 0.95rem; border-bottom: 1px solid rgba(255,255,255,0.06); }
@media (max-width: 760px) {
  .nav-links { display: none; }
  .hamburger { display: flex; }
  .mobile-menu.active { display: block; }
}
</style>