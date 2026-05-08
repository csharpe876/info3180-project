<template>
  <teleport to="body">
    <transition-group name="toast" tag="div" class="flash-container">
      <div
        v-for="msg in flash.messages"
        :key="msg.id"
        class="flash-toast"
        :class="`flash-${msg.type}`"
        role="alert"
      >
        <span class="flash-icon">{{ icons[msg.type] }}</span>
        <span class="flash-text">{{ msg.message }}</span>
        <button class="flash-close" @click="flash.dismiss(msg.id)" aria-label="Close">✕</button>
      </div>
    </transition-group>
  </teleport>
</template>

<script setup>
import { useFlashStore } from '../stores/flash'

const flash = useFlashStore()
const icons = { success: '✓', error: '✕', info: 'ℹ' }
</script>

<style scoped>
.flash-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 360px;
  pointer-events: none;
}

.flash-toast {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 13px 16px;
  border-radius: 10px;
  font-size: 0.88rem;
  font-family: 'DM Sans', sans-serif;
  font-weight: 500;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  pointer-events: all;
  min-width: 240px;
  word-break: break-word;
}

.flash-success {
  background: #f0fdf4;
  border: 1px solid #86efac;
  color: #15803d;
}
.flash-error {
  background: #fff1f2;
  border: 1px solid #fca5a5;
  color: #be123c;
}
.flash-info {
  background: #eff6ff;
  border: 1px solid #93c5fd;
  color: #1d4ed8;
}

.flash-icon {
  font-size: 1rem;
  flex-shrink: 0;
  margin-top: 1px;
}

.flash-text { flex: 1; line-height: 1.45; }

.flash-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  color: inherit;
  opacity: 0.6;
  padding: 0;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 2px;
}
.flash-close:hover { opacity: 1; }

/* Transition animations */
.toast-enter-active { transition: all 0.25s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from { opacity: 0; transform: translateX(40px); }
.toast-leave-to  { opacity: 0; transform: translateX(40px); }
</style>
