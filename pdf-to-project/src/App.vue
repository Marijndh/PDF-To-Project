<template>

  <p>Welcome to your Electron application.</p>
  <button @click="count++">
    Count is: {{ count }}
  </button>
  <v-row></v-row>
</template>

<script setup lang="ts">
import {ref} from "vue";
import {Ref} from "@vue/runtime-dom";

const count: Ref<number, number> = ref(0);
</script>