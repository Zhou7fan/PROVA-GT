<template>
  <div id="conf-chart-container" class="scrollable-container">
    <div class="header-container">
      <h2 class="group-header">Collected Codes</h2>
      <div class="export-icon" @click="exportToCSV">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#407434" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
      </div>
    </div>
    <p class="small-hint">Press Ctrl+X to clear the Input box</p>
    <div class="blank-line"></div>
    <div class="blank-line"></div>
    <div v-for="(group, index) in point.groups" :key="index">
      <div class="group-controls">
        <h3
          class="group-title"
          contenteditable="true"
          @input="updateGroupTitle(index, $event)"
          @blur="updateGroupTitle(index, $event)"
          @keydown.enter="handleEnterKey(index, $event)"
          @keydown="handleKeyDown($event, index)"
        >
          {{ group.title }}
        </h3>
        <div class="button-group">
          <button @click="toggleGroup(index)" class="act-title">Toggle</button>
          <button @click="removeGroup(index)" class="act-title">Delete</button>
          <button @click="releaseGroup(index)" class="act-title">Release</button>
        </div>
      </div>
      <div v-if="group.expanded" class="group-data">
        <div v-for="(word, wordIndex) in group.text" :key="wordIndex" class="code-item">
          <span>{{ word }}</span>
          <span class="passage-count">{{ group.count[wordIndex] }}</span>
        </div>
      </div>
    </div>
  </div>
</template>



<script setup lang="ts">
import { usePointall } from '@/composables/state_2.ts';
import { defineEmits, ref, watch, inject } from 'vue';
import { saveAs } from 'file-saver';

const point = usePointall();
const latestCsv = inject('latestCsv'); 
const csvData = ref<any[]>([]);

const loadCsvData = (path: string) => {
  fetch(path)
    .then((response) => response.text())
    .then((csvText) => {
      const rows = csvText.split('\n');
      const header = rows[0].split(',');
      csvData.value = rows.slice(1).map((row) => {
        const values = row.split(',');
        return header.reduce((obj, key, index) => {
          obj[key] = values[index] ? values[index].trim() : '';
          return obj;
        }, {} as any);
      });
    });
};

watch(latestCsv, () => {
  if (latestCsv.value) {
    loadCsvData(`/${latestCsv.value}`);
  }
});

const exportToCSV = () => {
  const groups = point.value.groups;
  const header = ['second-order codes', 'first-order codes', 'count', 'passage', 'explanation', 'sentence', 'stage'];
  const csvRows = [header.join(',')];

  const escapeCSV = (str: string) => {
    if (typeof str !== 'string') return '';
    return `"${str.replace(/"/g, '""')}"`;
  };

  groups.forEach((group) => {
    group.text.forEach((textItem, textIndex) => {
      if (group.count[textIndex] > 1) {
        const matchingEntries = csvData.value.filter((entry: any) => entry.code === textItem);
        matchingEntries.forEach((entry: any) => {
          const row = [
            group.title,
            entry.code,
            entry.count,
            entry.passage,
            entry.explanation,
            entry.sentence,
            group.stage[textIndex] || ''
          ].map(escapeCSV);
          csvRows.push(row.join(','));
        });
      } else {
        const matchingEntry = csvData.value.find((entry: any) => entry.code === textItem);
        const row = [
          group.title,
          textItem,
          group.count[textIndex] || '',
          matchingEntry?.passage || '',
          group.explanation[textIndex] || '',
          group.sentence[textIndex] || '',
          group.stage[textIndex] || ''
        ].map(escapeCSV);
        csvRows.push(row.join(','));
      }
    });
  });

  const csvContent = csvRows.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, 'exported_data.csv');
};

const updateGroupTitle = (index: number, event: Event) => {
  point.value.groups[index].title = (event.target as HTMLElement).innerText;
};

const toggleGroup = (index: number) => {
  point.value.groups[index].expanded = !point.value.groups[index].expanded;
};

const removeGroup = (index: number) => {
  point.value.groups.splice(index, 1);
};

const emit = defineEmits(['releaseGroup']);
const count = ref(0);

const releaseGroup = (index: number) => {
  count.value++;
  emit('releaseGroup', index, count.value);
};

const handleEnterKey = (index: number, event: Event) => {
  event.preventDefault();
  updateGroupTitle(index, event);
  document.activeElement?.blur();
};

const handleKeyDown = (event: KeyboardEvent, index: number) => {
  if (event.ctrlKey && event.key === 'x') {
    event.preventDefault();
    updateGroupTitle(index, { target: { innerText: '' } } as unknown as Event);
  }
};
</script>

<style scoped>
#conf-chart-container {
  width: 500px;
  overflow: auto;
  border: 1px solid #ccc;
  border-bottom: none;
  position: relative;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 8px 0;
}

.group-header {
  color: #407434;
  font-weight: bold;
  background-color: hsl(0, 0%, 100%);
  border-radius: 5px;
  font-size: 20px;
  margin: 0;
}

.export-icon {
  cursor: pointer;
  position: absolute;
  right: 10px;
}

.export-icon svg {
  width: 24px;
  height: 24px;
}

.group-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 15px;
  background-color: #f8f8f8;
  border-bottom: 1px solid #ddd;
}

.group-title {
  color: #407434;
  font-weight: bold;
  cursor: pointer;
  margin: 0;
  flex-grow: 1;
}

.button-group {
  display: flex;
  gap: 8px;
  justify-content: space-between; 
}

.act-title {
  background: none;
  border: 1px solid #407434;
  color: #407434;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
}

.act-title:hover {
  background-color: #407434;
  color: white;
}

.group-data {
  padding: 8px 15px;
  width: 100%;
}

.code-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.passage-count {
  color: #666;
  font-size: 0.8em;
  padding-left: 8px;
}

.small-hint {
  color: #888;
  font-size: 12px;
  margin-top: 3px;
}

.blank-line {
  height: 1em;
}
</style>