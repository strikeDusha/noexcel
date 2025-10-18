<template>
  <div id="app">
    <Header />
    <router-view />
  </div>
</template>

<script setup>
// здесь ничего не нужно, роутер подключается в main.js

import Header from "./components/Header.vue"
</script>