<template>
  <div class="auth-box">
    <h2>Регистрация</h2>
    <input type="text" placeholder="Имя пользователя" />
    <input type="password" placeholder="Пароль" />
    <input type="password" placeholder="Подтверждение пароля" />
    <button>Зарегистрироваться</button>
    <p style="margin-top: 10px;">
      <a href="#" @click.prevent="$emit('switch-view', 'auth')">Назад к авторизации</a>
    </p>
  </div>
</template>
