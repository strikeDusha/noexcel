<template>
  <div class="auth-container">
    <div class="auth-box">
      <h2>Регистрация</h2>

      <form @submit.prevent="handleRegister">
        <input v-model="username" type="text" placeholder="Имя пользователя" />
        <input v-model="password" type="password" placeholder="Пароль" />
        <input v-model="confirmPassword" type="password" placeholder="Подтверждение пароля" />

        <button ref="registerBtn" type="submit" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>

      <p v-if="error" class="error-text">{{ error }}</p>

      <a href="#" @click.prevent="goLogin">Назад к авторизации</a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const registerBtn = ref(null)

const API_URL = 'http://localhost:8080/api/register'

// --- Обработчик клавиши Enter ---
onMounted(() => {
  window.addEventListener('keydown', handleGlobalEnter)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalEnter)
})

function handleGlobalEnter(e) {
  if (e.key === 'Enter') {
    const active = document.activeElement
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) return
    e.preventDefault()
    registerBtn.value?.click()
  }
}

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
        password: password.value,
      }),
    })

    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || 'Ошибка регистрации')
    }

    await res.json()
    alert('Регистрация успешна! Переходим на страницу входа')
    router.push({ name: 'Login' })

  } catch (e) {
    error.value = e.message || 'Ошибка сети'
  } finally {
    loading.value = false
  }
}

function goLogin() {
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.error-text {
  color: red;
  margin-top: 10px;
}
</style>
