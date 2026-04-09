<template>
  <div class="page">
    <div class="container">

      <!-- Profile header -->
      <div class="profile-header card">
        <div class="avatar-wrap">
          <img v-if="previewUrl || profile.photo_url"
               :src="previewUrl || `${profile.photo_url}`"
               class="avatar-img" alt="Profile photo" />
          <div v-else class="avatar-placeholder large">{{ initials }}</div>
          <label class="change-photo" title="Change photo">
            📷
            <input type="file" accept="image/*" hidden @change="onPhoto" />
          </label>
        </div>
        <div class="hdr-info">
          <h1>{{ profile.full_name || auth.user?.username }}</h1>
          <p class="muted">{{ profile.parish }}, {{ profile.country }} · Age {{ profile.age }}</p>
          <p v-if="profile.bio" class="bio-text">{{ profile.bio }}</p>
          <div class="interest-tags" style="margin-top:10px">
            <span v-for="i in (profile.interests || [])" :key="i" class="badge badge-rose">{{ i }}</span>
          </div>
        </div>
      </div>

      <div v-if="success" class="success-msg">{{ success }}</div>
      <div v-if="error"   class="error-msg">{{ error }}</div>

      <!-- Edit form -->
      <div class="edit-card card">
        <h2 class="section-title">Edit Profile</h2>

        <div class="form-grid">
          <div class="form-field">
            <label>First Name</label>
            <input v-model="form.first_name" />
          </div>
          <div class="form-field">
            <label>Last Name</label>
            <input v-model="form.last_name" />
          </div>
          <div class="form-field full">
            <label>Bio</label>
            <textarea v-model="form.bio" placeholder="Tell people about yourself…" rows="3"></textarea>
          </div>
          <div class="form-field">
            <label>Parish / Region</label>
            <input v-model="form.parish" placeholder="e.g. Kingston" />
          </div>
          <div class="form-field">
            <label>City</label>
            <input v-model="form.city" placeholder="e.g. New Kingston" />
          </div>
          <div class="form-field">
            <label>Country</label>
            <input v-model="form.country" placeholder="Jamaica" />
          </div>
          <div class="form-field">
            <label>Occupation</label>
            <input v-model="form.occupation" placeholder="e.g. Software Developer" />
          </div>
          <div class="form-field">
            <label>Education Level</label>
            <select v-model="form.education_level">
              <option value="">Prefer not to say</option>
              <option value="high_school">High School</option>
              <option value="associate">Associate's Degree</option>
              <option value="bachelor">Bachelor's Degree</option>
              <option value="master">Master's Degree</option>
              <option value="doctorate">Doctorate</option>
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
          <div class="form-field">
            <label>Profile Visibility</label>
            <select v-model="form.is_public">
              <option :value="true">Public</option>
              <option :value="false">Private</option>
            </select>
          </div>
        </div>

        <!-- Age preferences -->
        <div class="pref-section">
          <h3 class="pref-title">Match Preferences</h3>
          <div class="form-grid">
            <div class="form-field">
              <label>Min Age</label>
              <input v-model.number="form.preferred_age_min" type="number" min="18" max="99" />
            </div>
            <div class="form-field">
              <label>Max Age</label>
              <input v-model.number="form.preferred_age_max" type="number" min="18" max="99" />
            </div>
            <div class="form-field">
              <label>Search Radius (km)</label>
              <input v-model.number="form.preferred_radius" type="number" min="1" />
            </div>
          </div>
        </div>

        <!-- Interests -->
        <div class="pref-section">
          <h3 class="pref-title">Interests & Hobbies</h3>
          <div class="interest-picker">
            <button
              v-for="i in availableInterests" :key="i.name"
              type="button"
              class="interest-btn"
              :class="{ selected: selectedInterests.includes(i.name) }"
              @click="toggleInterest(i.name)"
            >{{ i.name }}</button>
          </div>
          <p class="muted sm" style="margin-top:8px">Select at least 3 interests</p>
        </div>

        <div class="save-row">
          <button class="btn btn-primary" @click="saveProfile" :disabled="saving">
            {{ saving ? 'Saving…' : 'Save Changes' }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useProfileStore } from '../stores/profile'
import { getProfile, updateProfile, getInterests } from '../services/api'

const auth         = useAuthStore()
const profileStore = useProfileStore()
const profile = ref({})
const saving  = ref(false)
const success = ref('')
const error   = ref('')
const previewUrl        = ref(null)
const photoFile         = ref(null)
const availableInterests = ref([])
const selectedInterests  = ref([])

const form = reactive({
  first_name: '', last_name: '', bio: '',
  parish: '', city: '', country: 'Jamaica',
  occupation: '', education_level: '',
  looking_for: 'any', is_public: true,
  preferred_age_min: 18, preferred_age_max: 99, preferred_radius: 50,
})

const initials = computed(() => {
  const p = profile.value
  return (p.first_name?.[0] || '') + (p.last_name?.[0] || '')
})

function onPhoto(e) {
  const file = e.target.files[0]
  if (!file) return
  photoFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

function toggleInterest(name) {
  const idx = selectedInterests.value.indexOf(name)
  if (idx === -1) selectedInterests.value.push(name)
  else selectedInterests.value.splice(idx, 1)
}

function populateForm(p) {
  Object.keys(form).forEach(k => {
    if (p[k] !== undefined && p[k] !== null) form[k] = p[k]
  })
  selectedInterests.value = [...(p.interests || [])]
}

async function saveProfile() {
  success.value = ''; error.value = ''
  saving.value  = true
  try {
    let payload
    if (photoFile.value) {
      payload = new FormData()
      Object.entries(form).forEach(([k, v]) => payload.append(k, v))
      payload.append('interests', selectedInterests.value.join(','))
      payload.append('photo', photoFile.value)
    } else {
      payload = { ...form, interests: selectedInterests.value }
    }
    const { data } = await updateProfile(auth.user.id, payload)
    profile.value = data.profile
    profileStore.setProfile(data.profile)  // sync shared store so Dashboard reflects changes
    // Clear local preview — the persisted photo_url from the server now drives the image
    previewUrl.value = null
    photoFile.value  = null
    success.value = 'Profile updated successfully!'
    setTimeout(() => success.value = '', 3000)
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to save changes.'
  }
  saving.value = false
}

onMounted(async () => {
  try {
    const [pRes, iRes] = await Promise.all([
      getProfile(auth.user.id),
      getInterests(),
    ])
    profile.value = pRes.data
    availableInterests.value = iRes.data.interests
    populateForm(pRes.data)
  } catch {}
})
</script>

<style scoped>
.page { padding: 32px 24px; background: var(--cream); min-height: calc(100vh - 60px); }
.container { max-width: 780px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }

.profile-header { display: flex; align-items: flex-start; gap: 24px; padding: 28px; flex-wrap: wrap; }
.avatar-wrap { position: relative; flex-shrink: 0; }
.avatar-img, .avatar-placeholder {
  width: 100px; height: 100px; border-radius: 50%; object-fit: cover;
}
.avatar-placeholder.large {
  background: linear-gradient(135deg, var(--rose), var(--rose2));
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 2rem;
}
.change-photo {
  position: absolute; bottom: 0; right: 0;
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--navy); color: #fff; font-size: 0.75rem;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; border: 2px solid #fff;
}
.hdr-info { flex: 1; }
.hdr-info h1 { font-size: 1.7rem; margin-bottom: 4px; }
.bio-text { font-size: 0.9rem; color: var(--muted); line-height: 1.6; margin-top: 8px; }
.interest-tags { display: flex; flex-wrap: wrap; gap: 5px; }

.edit-card { padding: 28px; }
.section-title { font-size: 1.3rem; margin-bottom: 20px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-field.full { grid-column: 1 / -1; }

.pref-section { margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--cream2); }
.pref-title { font-size: 1rem; font-family: 'DM Sans', sans-serif; font-weight: 600;
              color: var(--navy3); margin-bottom: 14px; }

.interest-picker { display: flex; flex-wrap: wrap; gap: 8px; }
.interest-btn {
  padding: 6px 14px; border-radius: 50px; font-size: 0.83rem; font-weight: 500;
  border: 1.5px solid #e2e8f0; background: #f8fafc; color: var(--navy3);
  cursor: pointer; transition: all 0.15s;
}
.interest-btn:hover   { border-color: var(--rose); color: var(--rose); }
.interest-btn.selected { background: var(--rose); color: #fff; border-color: var(--rose); }

.save-row { margin-top: 24px; display: flex; justify-content: flex-end; }

.muted { color: var(--muted); font-size: 0.84rem; }
.sm    { font-size: 0.8rem; }

@media (max-width: 600px) {
  .form-grid { grid-template-columns: 1fr; }
  .profile-header { flex-direction: column; align-items: center; text-align: center; }
}
</style>