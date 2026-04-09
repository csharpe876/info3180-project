import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getProfile as apiGetProfile } from '../services/api'

export const useProfileStore = defineStore('profile', () => {
  const myProfile = ref(null)
  const loading   = ref(false)

  async function fetchMyProfile(userId) {
    if (!userId) return
    loading.value = true
    try {
      const { data } = await apiGetProfile(userId)
      myProfile.value = data
    } catch {}
    loading.value = false
  }

  function setProfile(p) {
    myProfile.value = p
  }

  function clearProfile() {
    myProfile.value = null
  }

  return { myProfile, loading, fetchMyProfile, setProfile, clearProfile }
})