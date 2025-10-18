<template>
  <div class="auth-box">
    <h2>Авторизация</h2>

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

    <button @click="handleLogin" :disabled="loading">
      {{ loading ? 'Входим...' : 'Войти' }}
    </button>

    <p v-if="error" style="color: red; margin-top: 10px;">{{ error }}</p>

    <p style="margin-top: 10px;">
        <a href="#" @click.prevent="goRegister">Регистрация</a>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
//router
function goRegister() {
  router.push({ name: 'Register' })
}
// ===== Состояние =====
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

// ===== Настройки API =====
const API_URL = 'http://localhost:8080/api/login' // поменяй при необходимости

// ===== SHA-256 хэширование пароля =====
async function hashPassword(password) {
  const msgBuffer = new TextEncoder().encode(password)
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

// ===== Логин =====
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
    // ожидаем { token, userId, ttl }
    if (data.token && data.userId && data.ttl) {
      const now = Date.now()
      localStorage.setItem('token', data.token)
      localStorage.setItem('userId', data.userId)
      localStorage.setItem('tokenTTL', now + data.ttl * 1000)

      alert('Успешный вход!')

      // Авто-логаут через TTL
      setTimeout(() => {
        localStorage.removeItem('token')
        localStorage.removeItem('userId')
        localStorage.removeItem('tokenTTL')
        alert('Сессия истекла, пожалуйста, войдите снова.')
      }, data.ttl * 1000)

      // Сообщаем родителю, что логин успешен
      // emit('login-success', { token: data.token, userId: data.userId })
    } else {
      error.value = 'Некорректный ответ от сервера'
    }

  } catch (e) {
    error.value = e.message || 'Ошибка сети'
  } finally {
    loading.value = false
  }
}

</script>

<style scoped>
.auth-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 250px;
}
button {
  padding: 6px;
}
</style>
