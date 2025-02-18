<template>
  <v-row class="console-container">
    <div class="console-output">
      <div
          v-for="(log, index) in this.logs"
          :key="index"
          class="console-log"
      >
        <span :class="`log-prefix ${log.type}`">
          [[{{ log.type.toUpperCase() }}]]
        </span>
        {{ log.message }}
      </div>
    </div>
  </v-row>
</template>

<script lang="ts">
import { defineComponent, ref, watch, nextTick, PropType } from "vue";
import {Log} from "@/entity/Log";


export default defineComponent({
  name: "ConsoleComponent",
  props: {
    logs: {
      type: Array as PropType<Log[]>,
      default: () => [] as PropType<Log[]>,
    },
  },
  setup(props) {
    const scrollToBottom = () => {
      nextTick(() => {
        const container = document.querySelector(".console-output");
        if (container) container.scrollTop = container.scrollHeight;
      });
    };

    watch(props.logs, () => {
      scrollToBottom();
    });
  },
});
</script>

<style scoped>
.console-container {
  display: flex;
  flex-direction: column;
  height: 270px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  border-radius: 10px 10px 0 0;
  font-family: monospace;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.console-output {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
}

.console-log {
  margin: 2px 0;
  word-wrap: break-word;
}

.log-prefix {
  font-weight: bold;
  margin-right: 8px;
}

.log-prefix.info {
  color: #5bc0de;
}

.log-prefix.error {
  color: #ff5c5c;
}

.log-prefix.success {
  color: #5cff88;
}

.log-prefix.warning {
  color: #ffa500;
}
</style>
