
<template>
  <header class="header">
    <!-- Логотип -->
    <div class="logo" @click="goHome">
      <img src="/logo.png" alt="NoExcel" class="logo-img" />
      <span>NoExcel</span>
    </div>

    <!-- Навигация -->
    <nav class="nav">
      
      <template v-if="isSignedIn">
        <router-link class  = "btn-link" to ="/profile">Профиль</router-link>
      </template>
      <template v-else>
        <router-link class  = "btn-link" to="/login">Вход</router-link>
        <router-link class  = "btn-link" to="/register">Регистрация</router-link>
      </template>
     
    </nav>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isSignedIn = ref(false)

function checkToken() {
  const token = localStorage.getItem('token')
  const ttl = parseInt(localStorage.getItem('tokenTTL')) || 0
  const now = Date.now()
  isSignedIn.value = !!token && ttl > now
}
function goHome() {
    router.push("/")
}

onMounted(() => {
  checkToken()
  // обновляем каждый раз при фокусе на вкладку
  window.addEventListener('focus', checkToken)
})
</script>

<style scoped>
.btn-link {
  display: inline-block;
  background-color: white;
  color: black;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  font-size: 1em;
  cursor: pointer;
  text-decoration: none; /* убираем underline */
  transition: background-color 0.2s;
}

.btn-link:hover {
  background-color: #f0f0f0; /* лёгкое выделение при наведении */
}


.header {
  background: #2ED1C9;
  color: black;
  padding: 15px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 0 0 20px 20px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 1.4em;
  font-weight: bold;
}

.logo-img {
  height: 40px;
  width: 40px;
  object-fit: contain;
}

.nav {
  display: flex;
  gap: 20px;
}

.nav a {
  color: black;
  text-decoration: none;
  font-weight: 500;
}

.nav a.router-link-active {
  text-decoration: underline;
}
</style>

