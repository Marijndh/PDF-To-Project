<template>
  <v-col class="log-container" cols="3">
    <v-row
        class="title"
    >
      <span>Recente Logs</span>
    </v-row>
    <v-col class="scrollable-container">
      <v-row
          v-for="(log, index) in this.logs"
          :key="log.getPath()"
          :class="['log-row', { 'no-bottom-border': index === this.amount - 1 }]"
      >
        <span class="log-name">{{ log.getName() }}</span>
        <i @click="log.sendEmail()" class="material-symbols-outlined icon-button">mail</i>
      </v-row>
    </v-col>
  </v-col>
</template>

<script lang="ts">
import {defineComponent, onMounted, ref, watch} from "vue";
import LogFile from "@/entity/LogFile";

export default defineComponent({
  name: "RecentLogs",
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
    let logs = ref<LogFile[]>([]);

    onMounted(async () => {
      setLogs();
    });

    watch(() => props.projectCreated, async (newValue) => {
      if (newValue) {
        setLogs();
      }
    });

    const setLogs = async () => {
      let fetchedLogs = await window.electron.getLogs(props.amount);
      logs.value = fetchedLogs.map(log => {
        return new LogFile(log.name, log.path);
      });
    }

    return {
      logs,
    };
  },
});
</script>

<style scoped>
.log-container {
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
.log-row {
  border-bottom: 2px solid #90a4ae;
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
  margin-left: 5px;
}

.icon-button:active {
  transform: scale(1.2);
}

.log-name {
  width: 80%;
  overflow: clip;
  height: 40px;
  font-size: 13px;
  font-family: Verdana,sans-serif;
}

.log-row:hover {
  background-color: #f0f0f0;
}
.no-bottom-border {
  border-bottom: none;
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