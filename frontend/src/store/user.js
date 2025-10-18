// src/store/user.js (Pinia)
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null) // null = не авторизован
  const token = ref(null)

  function loginFake(username) {
    user.value = { id: 1, username }
    token.value = 'fake-token-123' // любой идентификатор
    localStorage.setItem('token', token.value) // сохраняем между перезагрузками
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  function isSignedIn() {
    return !!user.value
  }

  return { user, token, loginFake, logout, isSignedIn }
})
