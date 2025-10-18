<template>
  <div class="auth-container">
    <component :is="currentViewComponent" @switch-view="switchView" />
  <div id="app">
    <!-- router-view рендерит текущий маршрут -->
    <router-view />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AuthPage from './components/AuthPage.vue'
import RegisterPage from './components/RegisterPage.vue'
import SpreadsheetPage from './components/SpreadsheetPage.vue'

// потом убрать 
const currentView = ref('auth') // стартовая страница: авторизация
// const currentView = ref('spreadsheet') // вместо 'auth'


function switchView(view) {
  currentView.value = view
}

const currentViewComponent = computed(() => {
  switch(currentView.value) {
    case 'auth': return AuthPage
    case 'register': return RegisterPage
    case 'spreadsheet': return SpreadsheetPage
  }
})
// здесь ничего не нужно, роутер подключается в main.js
</script>
