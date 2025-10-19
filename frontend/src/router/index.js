import { createRouter, createWebHistory } from 'vue-router'

import AuthPage from '@/components/AuthPage.vue'
import RegisterPage from '@/components/RegisterPage.vue'
import MainPage from '@/components/MainPage.vue'
import SpreadsheetPage from '@/components/SpreadsheetPage.vue'
import Profile from '@/components/Profile.vue'

const routes = [
  { path: '/', name: 'MainPage', component: MainPage },
  { path: '/login', name: 'Login', component: AuthPage },
  { path: '/register', name: 'Register', component: RegisterPage },
  { path: '/me', name: 'Profile', component: Profile },
  { path: '/spreadsheets', name: 'Spreadsheet', component: SpreadsheetPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
