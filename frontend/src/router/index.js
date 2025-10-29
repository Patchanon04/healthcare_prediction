import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import PatientsList from '../views/PatientsList.vue'
import Dashboard from '../views/Dashboard.vue'
import PatientDetail from '../views/PatientDetail.vue'
import ProfileView from '../views/ProfileView.vue'
import ChatView from '../views/ChatView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { title: 'Dashboard' } },
  { path: '/login', name: 'Login', component: LoginView, meta: { public: true } },
  // Register route removed
  { path: '/patients', name: 'Patients', component: PatientsList, meta: { title: 'Patients' } },
  { path: '/patients/:id', name: 'PatientDetail', component: PatientDetail, props: true },
  { path: '/profile', name: 'Profile', component: ProfileView },
  { path: '/chat', name: 'Chat', component: ChatView, meta: { title: 'Chat' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // If route is public, allow (e.g., login)
  if (to.meta && to.meta.public) {
    // If already logged in, prevent visiting login
    if (token && (to.name === 'Login')) {
      return next({ name: 'Patients' })
    }
    return next()
  }

  // Protected routes: require token
  if (!token) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  return next()
})

export default router
