<template>
  <div class="auth-container">
    <!-- Компонент авторизации -->
    <AuthPage v-if="currentView === 'auth'" @switch-view="switchView" />

    <!-- Компонент регистрации -->
    <RegisterPage v-else @switch-view="switchView" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AuthPage from './components/AuthPage.vue'
import RegisterPage from './components/RegisterPage.vue'

const currentView = ref('auth')

function switchView(view) {
  currentView.value = view
}
</script>
