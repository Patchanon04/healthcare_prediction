import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import './assets/styles.css'

const app = createApp(App)

// Toast configuration
app.use(Toast, {
  position: 'top-right',
  timeout: 3000,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  showCloseButtonOnHover: false,
})

app.use(router)
app.mount('#app')
