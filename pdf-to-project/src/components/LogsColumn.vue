<template>
<v-col cols="3" class="log-column">
  <v-data-table
      height="535"
      hide-default-header
      hide-default-footer
  >
  </v-data-table>
</v-col>
</template>

<script setup lang="ts">
</script>

<style scoped>
.log-column {
  background-color: yellow;
  display: flex;
  flex-direction: column;
  padding: 10px;
  gap: 10px;
}
</style>