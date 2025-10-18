// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router/router.js'   // <-- подключаем твой router

const app = createApp(App)

// подключаем роутер к приложению
app.use(router)

// монтируем приложение
app.mount('#app')
