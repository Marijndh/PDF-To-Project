<template>
  <v-container class="container">
    <v-row style="height: 600px; display: flex; flex-direction: row">
      <recent-projects/>
      <v-col cols="6" style="padding: 10px 20px">
        <div style="padding-bottom: 25px;">
          <progress-bar
              v-if="this.file"
              :current-step="this.currentStep"
              :total-steps="this.totalSteps"
          />
          <pdf-drop-zone v-else
            @file-accepted="this.setFile"
          />
        </div>
        <feedback-console
          :logs=this.logs
        />
      </v-col>
      <recent-logs/>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import RecentProjects from '@/components/RecentProjects.vue';
import ProgressBar from '@/components/ProgressBar.vue';
import { defineComponent, ref } from 'vue';
import RecentLogs from '@/components/RecentLogs.vue';
import PdfDropZone from '@/components/PdfDropZone.vue';
import FeedbackConsole from '@/components/FeedbackConsole.vue';

export default defineComponent({
  name: "MainComponent",
  components: {RecentLogs, RecentProjects, ProgressBar, PdfDropZone, FeedbackConsole},
  setup() {
    let file = ref<File>(null);
    let currentStep = ref<number>(0);
    let totalSteps = ref<number>(10);
    let logs = ref([]);
    const setFile = (newFile: File) => {
      file.value = newFile;
    };
    return {
      file,
      currentStep,
      totalSteps,
      logs,
      setFile
    };
  },
});
</script>

<style scoped>
.container {
  background-color: gray;
  padding: 18px 20px 0 20px;
}
</style>