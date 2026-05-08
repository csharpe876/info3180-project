<template>
  <div id="app">
    <AppNav v-if="auth.isLoggedIn" />
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <FlashMessage />
  </div>
</template>

<script setup>
import AppNav from './components/AppNav.vue'
import FlashMessage from './components/FlashMessage.vue'
import { useAuthStore } from './stores/auth'
const auth = useAuthStore()
</script>

<style>
#app { min-height: 100vh; display: flex; flex-direction: column; }
</style>
