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

// --- Импорт простого “хранилища” пользователя ---
const userKey = 'fake-user'

const router = useRouter()
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const registerBtn = ref(null)

// --- Обработчик клавиши Enter ---
onMounted(() => window.addEventListener('keydown', handleGlobalEnter))
onUnmounted(() => window.removeEventListener('keydown', handleGlobalEnter))

function handleGlobalEnter(e) {
  if (e.key === 'Enter') {
    const active = document.activeElement
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) return
    e.preventDefault()
    registerBtn.value?.click()
  }
}

// --- Фейковая регистрация ---
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
    // Здесь имитация задержки (как будто бек обрабатывает)
    await new Promise(r => setTimeout(r, 500))

    // Сохраняем пользователя в localStorage
    const user = { id: Date.now(), username: username.value, token: 'fake-token-123' }
    localStorage.setItem(userKey, JSON.stringify(user))

    alert(`Регистрация успешна! Привет, ${username.value}`)
    router.push('/table') // редирект на таблицы

  } catch (e) {
    error.value = 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}

// --- Переход на страницу логина ---
function goLogin() {
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.auth-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.error-text {
  color: red;
  margin-top: 10px;
}
</style>
