// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// Импортируем страницы / компоненты
import AuthPage from '../components/AuthPage.vue'
import RegisterPage from '../components/RegisterPage.vue'


const routes = [
  { path: '/login', name: 'Login', component: AuthPage },
  { path: '/register', name: 'Register', component: RegisterPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})


export default router
