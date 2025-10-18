<template>
  <div class="auth-box">
    <h2>Авторизация</h2>
    <input type="text" placeholder="Имя пользователя" />
    <input type="password" placeholder="Пароль" />
    <button>Войти</button>
    <p style="margin-top: 10px;">
      <a href="#" @click.prevent="$emit('switch-view', 'register')">Регистрация</a>
    </p>
  </div>
</template>
