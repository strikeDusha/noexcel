<template>
  <div class="auth-container">
    <div class="auth-box">
      <h2>Авторизация</h2>

      <form @submit.prevent="handleLogin">
        <input
          v-model="username"
          type="text"
          placeholder="Имя пользователя"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Пароль"
        />

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

const API_URL = 'http://localhost:8080/api/login'

// --- Добавляем обработчик клавиши Enter ---
onMounted(() => {
  window.addEventListener('keydown', handleGlobalEnter)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalEnter)
})

function handleGlobalEnter(e) {
  if (e.key === 'Enter') {
    const active = document.activeElement
    // если фокус внутри input, ничего не делаем
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) return
    // иначе нажимаем кнопку
    e.preventDefault()
    loginBtn.value?.click()
  }
}

// --- Хеширование пароля ---
async function hashPassword(password) {
  const msgBuffer = new TextEncoder().encode(password)
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

// --- Обработка входа ---
async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = 'Введите имя пользователя и пароль'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const hashed = await hashPassword(password.value)
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: hashed,
      }),
    })

    if (res.status === 401) {
      error.value = 'Неверный логин/пароль'
      return
    }

    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || 'Ошибка авторизации')
    }

    const data = await res.json()
    if (data.token && data.userId && data.ttl) {
      const now = Date.now()
      localStorage.setItem('token', data.token)
      localStorage.setItem('userId', data.userId)
      localStorage.setItem('tokenTTL', now + data.ttl * 1000)

      alert('Успешный вход!')
      setTimeout(() => {
        localStorage.removeItem('token')
        localStorage.removeItem('userId')
        localStorage.removeItem('tokenTTL')
        alert('Сессия истекла, пожалуйста, войдите снова.')
      }, data.ttl * 1000)
    } else {
      error.value = 'Некорректный ответ от сервера'
    }

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
