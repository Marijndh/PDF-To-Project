<template>
  <v-container class="container">
    <v-row style="height: 600px; display: flex; flex-direction: row">
      <recent-projects
          :projectCreated = "this.createdProject"
      />
      <v-col cols="6" style="padding: 10px 20px">
        <div style="padding-bottom: 25px;">
          <progress-bar
              v-if="this.file"
              :current-step="this.currentStep"
              :total-steps="this.totalSteps"
              :projectCreated = "this.createdProject"
              @reset-refs="this.resetRefs"
          />
          <pdf-drop-zone v-else
            @file-accepted="this.setFile"
          />
        </div>
        <feedback-console
          :logs=this.logs
        />
      </v-col>
      <recent-logs
          :projectCreated = "this.createdProject"
      />
    </v-row>
  </v-container>
</template>

<script lang="ts">
import RecentProjects from '@/components/RecentProjects.vue';
import ProgressBar from '@/components/ProgressBar.vue';
import {defineComponent, onMounted, ref} from 'vue';
import RecentLogs from '@/components/RecentLogs.vue';
import PdfDropZone from '@/components/PdfDropZone.vue';
import FeedbackConsole from '@/components/FeedbackConsole.vue';
import ProjectExtractor from "@/utils/ProjectExtractor";
import ProjectController from "@/controller/ProjectController";
import StepExecutor from "@/utils/StepExecutor";
import {Log} from "@/entity/Log";

export default defineComponent({
  name: "MainComponent",
  components: {RecentLogs, RecentProjects, ProgressBar, PdfDropZone, FeedbackConsole},
  setup() {
    let file = ref<File>(null);
    let currentStep = ref<number>(1);
    let totalSteps = ref<number>(1);
    let logs = ref<Array<Log>>([]);
    let createdProject = ref<boolean>(null);

    onMounted(async () => {
      const buffer = await window.electron.getTestFile();
      file.value = new File([buffer], "test-file.pdf", { type: "application/pdf" });
      if (file.value) {
        logs.value.push(new Log("info", "Test file loaded successfully"));
        saveProject();
      }
    });
    const saveProject = async () => {
      if (!file.value) return;
      const stepExecutor = new StepExecutor(logs.value, currentStep.value);
      await stepExecutor.initializeLogMessages();
      const projectExtractor = new ProjectExtractor();
      const projectController = new ProjectController();

      stepExecutor.addStep('textExtraction',async () => {
        const text = await window.electron.textFromPdf(await file.value.arrayBuffer());
        if (text.length === 0) return false;
        projectExtractor.setText(text);
        return true;
      });

      stepExecutor.addStep('findClient',async () => {
        return projectExtractor.findClient();
      });

      stepExecutor.addStep('findTemplate',async () => {
        return projectExtractor.fetchTemplate();
      });

      stepExecutor.addStep('setProjectValues', () => {
        projectExtractor.setProjectValues();
        return Promise.resolve(true);
      });

      stepExecutor.addStep('insertProjectIntoTemplate', () => {
        projectExtractor.insertProjectIntoTemplate();
        return Promise.resolve(true);
      });

      stepExecutor.addStep('createProject', () => {
        //return projectController.create(projectExtractor.getProjectData());
        return Promise.resolve(true);
      });

      stepExecutor.addStep('logData',async () => {
        return projectExtractor.logData(logs.value, file.value);
      });

      totalSteps.value = stepExecutor.getTotalSteps();
      createdProject.value = await stepExecutor.runSteps();

    };
    const resetRefs = () => {
      file.value = null;
      currentStep.value = 1;
      totalSteps.value = 1;
      logs.value = [];
      createdProject.value = null;
    };
    const setFile = (newFile: File) => {
      logs.value = [];
      file.value = newFile;
      logs.value.push(new Log("info", "File loaded successfully"));
      saveProject();

    };
    return {
      file,
      currentStep,
      totalSteps,
      logs,
      createdProject,
      setFile,
      resetRefs,
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