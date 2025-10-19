
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
  padding: 10px 20px;
  background-color: white;
  color: #2ED1C9; /* бирюзовый акцент */
  border-radius: 10px;
  text-decoration: none; /* убираем underline */
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
}

.btn-link:hover {
  transform: scale(1.05); /* лёгкое увеличение */
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
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

