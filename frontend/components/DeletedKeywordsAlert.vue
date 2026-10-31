<template>
  <div class="trash-overlay">
      <div class="trash-list">
          <h3>Deleted Keywords</h3>
          <div v-for="keyword in deletedKeywords" :key="keyword.text" class="restore-item">
              {{ keyword.text }} 
              <button @click="$emit('restore-keyword', keyword.text, keyword.count,keyword.explanation, keyword.senetence,keyword.sentence)">Restore</button>
          </div>
          <button @click="$emit('close')" class="close-button">Close</button>
      </div>
  </div>
</template>

<script setup>
defineProps({
  deletedKeywords: {
      type: Array,
      required: true,
  },
});

defineEmits(['restore-keyword', 'close']);
</script>

<style scoped>

.trash-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}


.trash-list {
  background: white;
  padding: 20px;
  border-radius: 10px;
  max-width: 400px;
  width: 100%;
}


.trash-list h3 {
  margin-bottom: 10px;
  font-size: 18px;
  color: #333;
}


.restore-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
}


.restore-item button {
  background: #28a745;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}


.restore-item button:hover {
  background: #218838;
}


.close-button {
  margin-top: 10px;
  background: #dc3545;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}


.close-button:hover {
  background: #c82333;
}
</style>