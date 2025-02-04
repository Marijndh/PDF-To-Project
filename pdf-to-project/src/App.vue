<template>
  <v-container class="container">
    <v-row style="height: 600px; display: flex; flex-direction: row">
      <recent-projects/>
      <v-col cols="6" style="background-color: gray;">
        <div style="padding-bottom: 25px;">
          <progress-bar
              v-if="file"
              :current-step=4
              :total-steps=10
              title='Email ophalen'
          />
          <pdf-drop-zone v-else/>
        </div>
        <feedback-console
          :initial-logs=[]
        />
      </v-col>
      <logs-column/>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import RecentProjects from "@/components/RecentProjects.vue";
import ProgressBar from '@/components/ProgressBar.vue';
import FeedbackConsole from "@/components/FeedbackConsole.vue";
import LogsColumn from "@/components/LogsColumn.vue";
import {ref} from "vue";
import PdfDropZone from "@/components/PdfDropZone.vue";

const file = ref<File | null>(null);
</script>

<style scoped>
.container {
  padding: 12px;
}
</style>