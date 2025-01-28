<template>
  <h1>💖 Hello World!</h1>
  <p>Welcome to your Electron application.</p>
  <button @click="count++">
    Count is: {{ count }}
  </button>
</template>

<script setup lang="ts">
import {ref} from "vue";
import {Ref} from "@vue/runtime-dom";

const count: Ref<number, number> = ref(0);
</script>