// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// Импортируем страницы / компоненты
import AuthPage from '../components/AuthPage.vue'
import RegisterPage from '../components/RegisterPage.vue'
import MainPage from '../components/MainPage.vue'
import SpreedSheet from '../components/SpreadsheetPage.vue'
import Profile from '@/components/Profile.vue'

const routes = [
 {path: '/me',name: "Profile",component: Profile},
  { path: '/spreadsheets', name: 'SpreadSheet', component: SpreedSheet },
  { path: '/', name: 'MainPage', component: MainPage },
  { path: '/login', name: 'Login', component: AuthPage },
  { path: '/register', name: 'Register', component: RegisterPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})


export default router
