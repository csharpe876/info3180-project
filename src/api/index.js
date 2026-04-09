/**
 * DriftDater API Service Layer
 * All calls to the Flask backend go through here.
 */

const BASE = 'http://localhost:5000/api/v1'

function getToken() {
  return localStorage.getItem('dd_token')
}

async function request(method, path, body = null, isForm = false) {
  const headers = {}
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const options = { method, headers }

  if (body !== null) {
    if (isForm) {
      options.body = body // FormData — no Content-Type header, browser sets it
    } else {
      headers['Content-Type'] = 'application/json'
      options.body = JSON.stringify(body)
    }
  }

  const res = await fetch(`${BASE}${path}`, options)
  const data = await res.json().catch(() => ({}))

  if (!res.ok) {
    const msg = data.error || (Array.isArray(data.errors) ? data.errors.join(', ') : data.errors) || 'Something went wrong'
    throw new Error(msg)
  }
  return data
}

export const api = {
  // Auth
  register: (payload) => request('POST', '/auth/register', payload),
  login:    (payload) => request('POST', '/auth/login',    payload),
  logout:   ()        => request('POST', '/auth/logout'),

  // Profiles
  getProfiles:   (params = {}) => request('GET', '/profiles?' + new URLSearchParams(params)),
  getProfile:    (userId)      => request('GET', `/profiles/${userId}`),
  updateProfile: (userId, fd)  => request('PUT', `/profiles/${userId}`, fd, true),

  // Likes
  likeUser: (userId, action) => request('POST', `/profiles/${userId}/like`, { action }),

  // Matches
  getMatches: () => request('GET', '/matches'),

  // Conversations & Messages
  getConversations: ()              => request('GET', '/conversations'),
  getMessages:      (matchId)       => request('GET', `/matches/${matchId}/messages`),
  sendMessage:      (matchId, body) => request('POST', `/matches/${matchId}/messages`, { body }),

  // Favourites
  getFavourites:   ()          => request('GET', '/favourites'),
  addFavourite:    (profileId) => request('POST',   `/favourites/${profileId}`, {}),
  removeFavourite: (profileId) => request('DELETE',  `/favourites/${profileId}`),

  // Interests
  getInterests: () => request('GET', '/interests'),
}
