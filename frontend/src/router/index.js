import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PatientsList from '../views/PatientsList.vue'
import PatientDetail from '../views/PatientDetail.vue'
import PredictView from '../views/PredictView.vue'
import ResultView from '../views/ResultView.vue'
import ProfileView from '../views/ProfileView.vue'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/login', name: 'Login', component: LoginView, meta: { public: true } },
  { path: '/register', name: 'Register', component: RegisterView, meta: { public: true } },
  { path: '/home', name: 'Home', component: PatientsList, meta: { title: 'History', historyMode: true } },
  { path: '/patients', name: 'Patients', component: PatientsList, meta: { title: 'Patient' } },
  { path: '/patients/:id', name: 'PatientDetail', component: PatientDetail, props: true },
  { path: '/predict', name: 'Predict', component: PredictView },
  { path: '/result/:id', name: 'Result', component: ResultView, props: true },
  { path: '/profile', name: 'Profile', component: ProfileView },
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
