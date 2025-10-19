<template>
  <div class="profile-page">
    <h1>👤 Профиль пользователя</h1>

    <div v-if="user">
      <p><strong>ID:</strong> {{ user.id }}</p>
      <p><strong>Имя:</strong> {{ user.username }}</p>
      <p><strong>Токен:</strong> {{ user.token }}</p>
      <p><strong>Сессия истекает:</strong> {{ ttlText }}</p>

      <button class="btn-logout" @click="logout">Выйти</button>
    </div>

    <div v-else>
      <p>Пользователь не авторизован. Пожалуйста, войдите.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const ttlText = ref('')

function checkUser() {
  const token = localStorage.getItem('token')
  const userId = localStorage.getItem('userId')
  const username = localStorage.getItem('username')
  const ttl = parseInt(localStorage.getItem('tokenTTL')) || 0
  const now = Date.now()

  if (token && ttl > now) {
    user.value = { id: userId, username, token }
    const secondsLeft = Math.floor((ttl - now) / 1000)
    ttlText.value = `${Math.floor(secondsLeft / 60)} мин ${secondsLeft % 60} сек`
  } else {
    user.value = null
  }
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userId')
  localStorage.removeItem('username')
  localStorage.removeItem('tokenTTL')
  user.value = null
  router.push({ name: 'Login' })
}

onMounted(() => {
  checkUser()
})
</script>

<style scoped>
.profile-page {
  max-width: 500px;
  margin: 50px auto;
  padding: 30px;
  border-radius: 15px;
  background-color: #f7f7f7;
  text-align: center;
}

.profile-page h1 {
  margin-bottom: 30px;
  color: #2ED1C9;
}

.profile-page p {
  margin: 10px 0;
  font-size: 1.1em;
}

.btn-logout {
  margin-top: 20px;
  padding: 10px 25px;
  background-color: white;
  color: black;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-logout:hover {
  background-color: #e0e0e0;
}
</style>
