<template>
  <v-col
      class="pdf-drop-zone"
      @dragover.prevent="this.handleDragOver"
      @dragleave.prevent="this.handleDragLeave"
      @drop.prevent="this.handleDrop"
  >
    <div class="drop-message">
      <v-col v-if="!this.file">
        <v-row><span>{{ this.message }}</span></v-row>
        <v-row><p class="error-text">{{this.errorText}}</p></v-row>
      </v-col>
      <v-col v-else>
        <v-row>
          <span>Bestand geüpload: {{ this.file.name }}</span>
        </v-row>
        <v-row class="button-row">
          <v-btn>
            <i class="material-icons">check</i>
          </v-btn>
          <v-btn  @click="this.deleteFile">
            <i class="material-icons">delete</i>
          </v-btn>
        </v-row>
      </v-col>
    </div>
  </v-col>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
export default defineComponent({
  name: "PDFDropZone",
  props: {
    message: {
      type: String,
      default: "Drop hier een PDF bestand",
    },
  },
  setup() {
    let file = ref<File>(null);
    const isDragging = ref<boolean>(false);
    let errorText = ref<string>(null);

    // Handle drag-over event
    const handleDragOver = () => {
      isDragging.value = true;
    };

    // Handle drag-leave event
    const handleDragLeave = () => {
      isDragging.value = false;
    };

    // Handle file drop
    const handleDrop = (event: DragEvent) => {
      isDragging.value = false;
      errorText.value = "";
      const files = event.dataTransfer?.files;
      if (files && files.length > 0) {
        const result = files[0];
        if (result.type === "application/pdf") {
          file.value = result
        } else {
          errorText.value = 'Gebruik een pdf bestand, dit type wordt niet ondersteund'
        }
      }
    };

    const deleteFile = () => {
      file.value = null;
    };

    return {
      file,
      isDragging,
      errorText,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      deleteFile,
    };
  },
});
</script>

<style scoped>
.pdf-drop-zone {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  background-color: white;
  border-radius: 5px;
  border: 2px dashed #444;
  color: #d4d4d4;
  font-family: Helvetica, Arial, sans-serif;
  padding: 20px;
  height: 250px; /* Same height as progress-bar-container */
  transition: background-color 0.3s;
}

.pdf-drop-zone:hover {
  background-color: #f0f0f0;
}

.pdf-drop-zone.dragging {
  background-color: #e0ffe0;
  border-color: #5cff88;
}

.drop-message {
  text-align: center;
  font-size: 18px;
  color: #333;
  align-items: center;
}

.drop-message span {
  font-weight: bold;
  color: #444;
  justify-self: center;
}

.button-row {
  display: inline-flex;
  justify-content: space-between;
  margin-top: 30px;
  gap: 20px;
}

.error-text {
  color: #d80b0b;
  font-size: 14px;
  font-weight: bolder;
  margin-top: 5px;
}
</style>
