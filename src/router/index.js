import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import HomeView       from '../views/HomeView.vue'
import LoginView      from '../views/LoginView.vue'
import RegisterView   from '../views/RegisterView.vue'
import DashboardView  from '../views/DashboardView.vue'
import MatchesView    from '../views/MatchesView.vue'
import MessagesView   from '../views/MessagesView.vue'
import ProfileView    from '../views/ProfileView.vue'
import FavouritesView from '../views/FavouritesView.vue'
import AdminView      from '../views/AdminView.vue'

const routes = [
  { path: '/',            name: 'Home',       component: HomeView },
  { path: '/login',       name: 'Login',      component: LoginView },
  { path: '/register',    name: 'Register',   component: RegisterView },
  { path: '/dashboard',   name: 'Dashboard',  component: DashboardView,  meta: { requiresAuth: true } },
  { path: '/matches',     name: 'Matches',    component: MatchesView,    meta: { requiresAuth: true } },
  { path: '/messages',    name: 'Messages',   component: MessagesView,   meta: { requiresAuth: true } },
  { path: '/messages/:matchId', name: 'Chat', component: MessagesView,   meta: { requiresAuth: true } },
  { path: '/profile',     name: 'Profile',    component: ProfileView,    meta: { requiresAuth: true } },
  { path: '/favourites',  name: 'Favourites', component: FavouritesView, meta: { requiresAuth: true } },
  { path: '/admin',       name: 'Admin',      component: AdminView,      meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return { name: 'Login' }
  if ((to.name === 'Login' || to.name === 'Register' || to.name === 'Home') && auth.isLoggedIn) return { name: 'Dashboard' }
})

export default router
