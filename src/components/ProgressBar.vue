<template>
  <v-row
      v-if="!this.projectCreated === null"
      class="progress-bar-container"
  >
    <div class="spinner-container">
      <div class="spinner"></div>
    </div>
    <div class="progress-bar">
      <div
          class="progress-bar-fill"
          :style="{ width: this.progressPercentage + '%' }"
      ></div>
    </div>
  </v-row>
  <v-row
      v-else-if="this.projectCreated !== null"
      class="progress-bar-container"
  >
    <div class="spinner-container">
      <div v-if="this.projectCreated">
        <span class="material-symbols-outlined text-green icon">done_outline</span>
      </div>
      <div v-else>
        <span class="material-symbols-outlined text-red icon">block</span>
      </div>
    </div>
    <div>
      <v-btn @click="this.$emit('reset-refs')">
        <span class="material-symbols-outlined">redo</span>
      </v-btn>
    </div>
  </v-row>
</template>

<script lang="ts">
import {defineComponent, computed, onMounted} from "vue";

export default defineComponent({
  name: "ProgressBar",
  props: {
    currentStep: {
      type: Number,
      required: true,
      default: 0,
    },
    totalSteps: {
      type: Number,
      required: true,
      default: 1,
    },
    projectCreated: {
      type: Boolean,
      required: false,
      default: null,
    }
  },
  setup(props) {
    // Compute the progress percentage
    const progressPercentage = computed(() => {
      if (props.totalSteps === 0) return 0;
      return (props.currentStep / props.totalSteps) * 100;
    });

    return {
      progressPercentage,
    };
  },
});
</script>

<style scoped>
/* Main Container Styling */
.progress-bar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: white;
  justify-content: space-between;
  border-radius: 5px;
  color: #d4d4d4;
  font-family: Helvetica, Arial, sans-serif;
  margin-bottom: 10px;
  margin-top: 5px;
  padding: 30px 20px;
  height: 250px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* Spinner and Title */
.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 10px;
}

.spinner {
  border: 8px solid rgba(0, 0, 0, 0.1); /* Light gray border */
  border-top: 10px solid #5cff88; /* Active color */
  border-radius: 50%;
  width: 120px;
  height: 120px;
  animation: spin 1s linear infinite;
}
.progress-bar {
  height: 30px;
  width: 100%;
  background-color: #444;
  border-radius: 10px;
  border: 4px solid #1e1e1e;
  overflow: hidden;
  margin: 0;
  justify-self: center;
}

.progress-bar-fill {
  height: 100%;
  background-color: #5cff88;
  transition: width 0.3s ease-in-out;
}

/* Animations */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.icon {
  font-size: 130px;
}
</style>