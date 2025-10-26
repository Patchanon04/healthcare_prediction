import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PatientsList from '../views/PatientsList.vue'
import Dashboard from '../views/Dashboard.vue'
import PatientDetail from '../views/PatientDetail.vue'
import ProfileView from '../views/ProfileView.vue'
import ChatView from '../views/ChatView.vue'

const routes = [
  { path: '/', redirect: '/patients' },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { title: 'Dashboard' } },
  { path: '/login', name: 'Login', component: LoginView, meta: { public: true } },
  { path: '/register', name: 'Register', component: RegisterView, meta: { public: true } },
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
  if (!to.meta.public && !token) {
    return next({ name: 'Login' })
  }
  next()
})

export default router
