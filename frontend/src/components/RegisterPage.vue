<template>
  <div class="auth-box">
    <h2>Регистрация</h2>

    <input v-model="username" type="text" placeholder="Имя пользователя" />
    <input v-model="password" type="password" placeholder="Пароль" />
    <input v-model="confirmPassword" type="password" placeholder="Подтверждение пароля" />

    <button @click="handleRegister" :disabled="loading">
      {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
    </button>

    <p v-if="error" style="color: red; margin-top: 10px;">{{ error }}</p>

    <p style="margin-top: 10px;">
      <a href="#" @click.prevent="goLogin">Назад к авторизации</a>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

// URL бэка
const API_URL = 'http://localhost:8080/api/register'

// Логика регистрации
async function handleRegister() {
  if (!username.value || !password.value || !confirmPassword.value) {
    error.value = 'Заполните все поля'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Пароли не совпадают'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: password.value, // можно хэшировать, если бэк ожидает SHA-256
      }),
    })

    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || 'Ошибка регистрации')
    }

    const data = await res.json()
    alert('Регистрация успешна! Переходим на страницу входа')
    router.push({ name: 'Login' })

  } catch (e) {
    error.value = e.message || 'Ошибка сети'
  } finally {
    loading.value = false
  }
}

// Переход на Login через роутер
function goLogin() {
  router.push({ name: 'Login' })
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
