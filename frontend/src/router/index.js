import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import HomeView from '../views/HomeView.vue'
import PredictView from '../views/PredictView.vue'
import ResultView from '../views/ResultView.vue'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/login', name: 'Login', component: LoginView, meta: { public: true } },
  { path: '/register', name: 'Register', component: RegisterView, meta: { public: true } },
  { path: '/home', name: 'Home', component: HomeView },
  { path: '/predict', name: 'Predict', component: PredictView },
  { path: '/result/:id', name: 'Result', component: ResultView, props: true },
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
