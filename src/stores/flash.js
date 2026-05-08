import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useFlashStore = defineStore('flash', () => {
  const messages = ref([])

  function flash(message, type = 'success', duration = 4000) {
    const id = Date.now() + Math.random()
    messages.value.push({ id, message, type })
    setTimeout(() => dismiss(id), duration)
  }

  function dismiss(id) {
    messages.value = messages.value.filter(m => m.id !== id)
  }

  return { messages, flash, dismiss }
})
