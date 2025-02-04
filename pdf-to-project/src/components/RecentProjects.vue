<template>
    <v-col class="project-container" cols="3">
      <v-row
          class="title"
      >
        <span>Recente Projecten</span>
      </v-row>
      <v-col class="scrollable-container">
      <v-row
          v-for="project in this.projects"
          :key="project.getId()"
          class="project-row"
      >
        <span class="project-name-text">{{ project.getName() }}</span>
        <i @click="this.openProject(project.getId())" class="material-icons icon-button">open_in_new</i>
      </v-row>
    </v-col>
    </v-col>
</template>

<script lang="ts">
import { ref, defineComponent, onMounted } from "vue";
import ProjectController from '@/controller/ProjectController';
import Project from '@/entity/Project';
import { shell } from 'electron';
export default defineComponent({
  name: "RecentProjects",
  setup() {
      let projects = ref<Project[]>([]);
      const projectController = new ProjectController();
      const openProject = (projectId: number) => {
        const url = `${import.meta.env.VITE_PROJECT_URL}${projectId}`;
        window.electron.openExternal(url);
      };
      onMounted(async () => {
        projects.value = await projectController.listProjects(10);
      });

      return {
        projects,
        openProject,
      };
    },
});
</script>
<style scoped>
.project-container {
  padding: 0 !important;
  padding-right: 8px !important;
  height: 560px;
}
.scrollable-container {
  padding: 16px 16px 16px 20px;
  direction: rtl;
  height: 556px;
  overflow-y: clip;
}
.project-row {
  border-bottom: 2px solid #e0e0e0;
  direction: ltr;
  align-items: center;
  max-height: 50px;
  padding: 5px 5px 5px 0;
  gap: 4px;
}

.icon-button {
  cursor: pointer;
  color: #000000;
  transition: transform 0.2s ease-in-out;
}

.icon-button:active {
  transform: scale(1.2);
}

.project-name-text {
  width: 80%;
  overflow: clip;
  height: 40px;
  font-size: 13px;
  font-family: Verdana,sans-serif;
}

.project-row:hover {
  background-color: #f0f0f0;
}

.title {
  border-bottom: 2px solid #888888;
  margin: 0;
  padding: 10px 4px 4px 4px;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-family: Verdana,sans-serif;
  font-weight: bolder;
}
</style>