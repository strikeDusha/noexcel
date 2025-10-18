<template>
  <div class="auth-container">
    <div class="auth-box">
      <h2>Авторизация</h2>

      <form @submit.prevent="handleLogin">
        <input v-model="username" type="text" placeholder="Имя пользователя" />
        <input v-model="password" type="password" placeholder="Пароль" />

        <button ref="loginBtn" type="submit" :disabled="loading">
          {{ loading ? 'Входим...' : 'Войти' }}
        </button>
      </form>

      <p v-if="error" class="error-text">{{ error }}</p>

      <a href="#" @click.prevent="goRegister">Регистрация</a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const loginBtn = ref(null)

// ключ в localStorage, где храним зарегистрированных пользователей
const USER_KEY = 'fake-user'

onMounted(() => window.addEventListener('keydown', handleGlobalEnter))
onUnmounted(() => window.removeEventListener('keydown', handleGlobalEnter))

function handleGlobalEnter(e) {
  if (e.key === 'Enter') {
    const active = document.activeElement
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) return
    e.preventDefault()
    loginBtn.value?.click()
  }
}

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = 'Введите имя пользователя и пароль'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await new Promise(r => setTimeout(r, 300)) // имитация задержки

    const stored = JSON.parse(localStorage.getItem(USER_KEY))
    if (!stored || stored.username !== username.value || stored.password !== password.value) {
      error.value = 'Неверный логин/пароль'
      return
    }

    // сохраняем токен и TTL
    const token = 'fake-token-123'
    const ttl = 60 * 5 * 1000 // 5 минут
    const now = Date.now()
    localStorage.setItem('token', token)
    localStorage.setItem('userId', stored.id)
    localStorage.setItem('tokenTTL', now + ttl)

    alert('Успешный вход!')
    setTimeout(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('userId')
      localStorage.removeItem('tokenTTL')
      alert('Сессия истекла, пожалуйста, войдите снова.')
    }, ttl)

    router.push('/table')

  } catch (e) {
    error.value = e.message || 'Ошибка сети'
  } finally {
    loading.value = false
  }
}

function goRegister() {
  router.push({ name: 'Register' })
}
</script>

<style scoped>
.error-text {
  color: red;
  margin-top: 10px;
}
</style>
