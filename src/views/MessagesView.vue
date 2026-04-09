<template>
  <div class="page">
    <div class="container">

      <!-- Conversation list (left) -->
      <div class="sidebar card">
        <h2 class="sidebar-title">Messages</h2>
        <div v-if="loadingConvos" class="spinner" style="margin:20px auto;width:24px;height:24px;border-width:2px"></div>
        <div v-else-if="conversations.length === 0" class="empty-state" style="padding:30px 10px">
          <div class="emoji" style="font-size:1.8rem">💬</div>
          <p style="font-size:0.85rem;color:var(--muted)">No conversations yet.<br>Get a match first!</p>
        </div>
        <div v-else>
          <div
            v-for="c in conversations" :key="c.match_id"
            class="convo-item"
            :class="{ active: activeMatchId == c.match_id }"
            @click="openChat(c.match_id)"
          >
            <div class="convo-avatar">
              <img v-if="c.other_profile?.photo_url"
                   :src="c.other_profile.photo_url" />
              <div v-else class="avatar-placeholder tiny">{{ initials(c.other_profile) }}</div>
            </div>
            <div class="convo-meta">
              <p class="convo-name">{{ c.other_profile?.full_name }}</p>
              <p class="convo-last">{{ c.latest_message?.body || 'Say hello!' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat window (right) -->
      <div class="chat-panel card">
        <!-- No chat selected -->
        <div v-if="!activeMatchId" class="chat-empty">
          <div class="emoji">💌</div>
          <h3>Select a conversation</h3>
          <p>Choose someone from the left to start chatting</p>
        </div>

        <template v-else>
          <!-- Chat header -->
          <div class="chat-header">
            <div class="chat-avatar">
              <img v-if="activeProfile?.photo_url" :src="activeProfile.photo_url" />
              <div v-else class="avatar-placeholder tiny">{{ initials(activeProfile) }}</div>
            </div>
            <div>
              <p class="chat-name">{{ activeProfile?.full_name }}</p>
              <p class="muted" style="font-size:0.78rem">{{ activeProfile?.parish }}</p>
            </div>
          </div>

          <!-- Messages -->
          <div class="messages-area" ref="msgArea">
            <div v-if="loadingMsgs" class="spinner" style="margin:30px auto;width:28px;height:28px;border-width:2px"></div>
            <div v-else-if="messages.length === 0" class="chat-empty-msgs">
              Say hello to {{ activeProfile?.first_name }}! 👋
            </div>
            <template v-else>
              <div
                v-for="msg in messages" :key="msg.id"
                class="msg-row"
                :class="{ mine: msg.sender_id === auth.user.id }"
              >
                <div class="msg-bubble">
                  <p>{{ msg.body }}</p>
                  <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
                </div>
              </div>
            </template>
          </div>

          <!-- Input -->
          <div class="chat-input-row">
            <input
              v-model="newMsg"
              class="chat-input"
              placeholder="Type a message…"
              @keyup.enter="sendMsg"
            />
            <button class="btn btn-primary send-btn" @click="sendMsg" :disabled="!newMsg.trim() || sending">
              {{ sending ? '…' : 'Send' }}
            </button>
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getConversations, getMessages, sendMessage } from '../services/api'

const auth          = useAuthStore()
const route         = useRoute()
const conversations = ref([])
const messages      = ref([])
const newMsg        = ref('')
const sending       = ref(false)
const loadingConvos = ref(true)
const loadingMsgs   = ref(false)
const activeMatchId = ref(null)
const msgArea       = ref(null)
let   pollTimer     = null

const activeConvo   = computed(() =>
  conversations.value.find(c => c.match_id == activeMatchId.value)
)
const activeProfile = computed(() => activeConvo.value?.other_profile)

function initials(p) {
  if (!p) return '?'
  return (p.first_name?.[0] || '') + (p.last_name?.[0] || '')
}

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleTimeString('en-JM', { hour: '2-digit', minute: '2-digit' })
}

async function openChat(matchId) {
  activeMatchId.value = matchId
  loadingMsgs.value   = true
  messages.value      = []
  try {
    const { data } = await getMessages(matchId)
    messages.value = data.messages
  } catch {}
  loadingMsgs.value = false
  await nextTick()
  scrollDown()
}

function scrollDown() {
  if (msgArea.value) msgArea.value.scrollTop = msgArea.value.scrollHeight
}

async function sendMsg() {
  if (!newMsg.value.trim() || sending.value) return
  sending.value = true
  const body = newMsg.value.trim()
  newMsg.value = ''
  try {
    const { data } = await sendMessage(activeMatchId.value, body)
    messages.value.push(data.message)
    // Also update sidebar latest message
    const convo = conversations.value.find(c => c.match_id == activeMatchId.value)
    if (convo) convo.latest_message = data.message
    await nextTick()
    scrollDown()
  } catch {
    newMsg.value = body  // restore on failure
  }
  sending.value = false
}

// Poll for new messages — compare last message id, not just count
function startPolling(matchId) {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (!matchId) return
    try {
      const { data } = await getMessages(matchId)
      const lastKnownId = messages.value[messages.value.length - 1]?.id ?? -1
      const lastNewId   = data.messages[data.messages.length - 1]?.id ?? -1
      if (lastNewId > lastKnownId) {
        messages.value = data.messages
        await nextTick()
        scrollDown()
      }
    } catch {}
  }, 4000)
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

watch(activeMatchId, (id) => {
  if (id) startPolling(id)
  else    stopPolling()
})

// Clean up timer when navigating away
onUnmounted(() => stopPolling())

onMounted(async () => {
  try {
    const { data } = await getConversations()
    conversations.value = data.conversations
  } catch {}
  loadingConvos.value = false

  // Auto-open from route param (e.g. /messages/3)
  if (route.params.matchId) {
    await openChat(Number(route.params.matchId))
  }
})
</script>

<style scoped>
.page { padding: 32px 24px; min-height: calc(100vh - 60px); background: var(--cream); }
.container {
  max-width: 960px; margin: 0 auto;
  display: grid; grid-template-columns: 280px 1fr; gap: 20px;
  height: calc(100vh - 124px);
}

/* Sidebar */
.sidebar { overflow-y: auto; padding: 0; }
.sidebar-title { padding: 18px 18px 12px; font-size: 1.2rem; border-bottom: 1px solid var(--cream2); }
.convo-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px; cursor: pointer; transition: background 0.15s;
  border-bottom: 1px solid var(--cream2);
}
.convo-item:hover, .convo-item.active { background: var(--cream2); }
.convo-meta { overflow: hidden; }
.convo-name { font-weight: 600; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.convo-last { font-size: 0.78rem; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Chat panel */
.chat-panel { display: flex; flex-direction: column; overflow: hidden; padding: 0; }
.chat-empty {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 8px; color: var(--muted);
}
.chat-empty .emoji { font-size: 3rem; }
.chat-empty h3 { font-family: 'DM Sans', sans-serif; color: var(--navy3); }

.chat-header {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 18px; border-bottom: 1px solid var(--cream2); background: var(--white);
}
.chat-name { font-weight: 600; font-size: 0.95rem; }

.messages-area {
  flex: 1; overflow-y: auto; padding: 18px;
  display: flex; flex-direction: column; gap: 10px;
}
.msg-row { display: flex; }
.msg-row.mine { justify-content: flex-end; }
.msg-bubble {
  max-width: 68%; padding: 10px 14px; border-radius: 16px;
  background: var(--cream2); color: var(--text);
}
.msg-row.mine .msg-bubble  { background: var(--rose); color: #fff; border-bottom-right-radius: 4px; }
.msg-row:not(.mine) .msg-bubble { border-bottom-left-radius: 4px; }
.msg-bubble p { font-size: 0.92rem; line-height: 1.5; }
.msg-time { display: block; font-size: 0.7rem; opacity: 0.65; margin-top: 4px; text-align: right; }

.chat-input-row { display: flex; gap: 10px; padding: 14px 16px; border-top: 1px solid var(--cream2); }
.chat-input {
  flex: 1; padding: 10px 14px; border: 1.5px solid #e2e8f0;
  border-radius: 24px; font-size: 0.9rem; font-family: 'DM Sans', sans-serif;
  background: var(--cream); transition: border-color 0.2s;
}
.chat-input:focus { outline: none; border-color: var(--rose); }
.send-btn { border-radius: 24px; padding: 10px 20px; }

.chat-empty-msgs { text-align: center; padding: 40px; color: var(--muted); font-size: 0.9rem; }

/* Avatars */
.convo-avatar img, .chat-avatar img,
.avatar-placeholder { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.chat-avatar img, .chat-avatar .avatar-placeholder { width: 38px; height: 38px; }
.avatar-placeholder.tiny {
  background: linear-gradient(135deg, var(--rose), var(--rose2));
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.85rem;
}
.muted { color: var(--muted); }

@media (max-width: 700px) {
  .container { grid-template-columns: 1fr; height: auto; }
  .sidebar { max-height: 220px; }
  .chat-panel { min-height: 450px; }
}
</style>