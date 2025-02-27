<template>
    <v-col class="project-container" cols="3">
      <v-row class="title">
        <span>Recente Projecten</span>
      </v-row>
      <v-col class="scrollable-container">
      <v-row
          v-for="(project, index) in this.projects"
          :key="project.getId()"
          :class="['project-row', { 'no-bottom-border': index === this.amount - 1 }]"
      >
        <span class="project-name-text">{{ project.getName() }}</span>
        <i @click="this.openProject(project.getId())" class="material-symbols-outlined icon-button">open_in_new</i>
      </v-row>
    </v-col>
    </v-col>
</template>

<script lang="ts">
import {ref, defineComponent, onMounted, watch} from "vue";
import ProjectController from '@/controller/ProjectController';
import Project from '@/entity/Project';

export default defineComponent({
  name: "RecentProjects",
  props: {
    amount: {
      type: Number,
      default: 10,
    },
    projectCreated: {
      type: Boolean,
      required: false,
      default: null,
    }
  },
  setup(props) {
      let projects = ref<Project[]>([]);
      const projectController = new ProjectController();
      const openProject = async (projectId: number) => {
        const url = `${ await window.electron.getEnvVariable('PROJECT_URL')}${projectId}`;
        window.electron.openExternal(url);
      };
      onMounted(async () => {
        await projectController.initialize();
        setProjects();
      });

      watch(() => props.projectCreated, async (createdProject) => {
        if (createdProject) {
          setProjects()
        }
      });

      const setProjects = async () => {
        projects.value = await projectController.listProjects(props.amount);
      }

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
  height: 548px;
  background: white;
  border-radius: 8px;
}
.scrollable-container {
  padding: 16px 16px 16px 20px;
  direction: rtl;
  height: 556px;
  overflow-y: clip;
}
.project-row {
  border-bottom: 2px solid #90a4ae;
  direction: ltr;
  align-items: center;
  max-height: 50px;
  padding: 5px 5px 5px 0;
  gap: 4px;
}

.no-bottom-border {
  border-bottom: none;
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
  margin: 0 0 0 4px;
  padding: 10px 4px 4px 4px;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-family: Verdana,sans-serif;
  font-weight: bolder;
}
</style>