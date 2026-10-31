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
    <div v-for="(secondOrderCode, soIndex) in processedData" :key="soIndex">
      <div class="group-controls">
        <h3 class="group-title">{{ secondOrderCode.title }}</h3>
        <button @click="toggleGroup(soIndex)" class="act-title">Toggle</button>
      </div>
      <div v-if="secondOrderCode.expanded" class="group-data">
        <div 
          v-for="(firstOrderCode, foIndex) in secondOrderCode.firstOrderCodes" 
          :key="foIndex"
          class="code-item"
        >
          {{ firstOrderCode.code }}
          <span 
            v-if="firstOrderCode.passages.length > 0"
            class="passage-count"
            :title="firstOrderCode.passages.join(', ')"
          >
            ({{ firstOrderCode.passages.length }})
          </span>
        </div>
      </div>
    </div>
    </div>
</template>

<script setup lang="ts">
import { usePoint } from '~/composables/state';
import { ref, computed, watch } from 'vue';

const point = usePoint();


const processedData = ref<{ title: string, firstOrderCodes: { code: string, passages: string[] }[], expanded: boolean }[]>([]);
const allFirstCodes = ref<Map<string, Set<string>>>(new Map());


const updateProcessedData = () => {
  const dataMap = new Map<string, { title: string, firstOrderCodes: Map<string, { code: string, passages: string[] }>, expanded: boolean }>();

  
  point.value.groups.forEach(group => {
    group.firstOrderCodes.forEach((foc, index) => {
      if (group.secondOrderCodes[index]) {
        if (!allFirstCodes.value.has(foc)) {
          allFirstCodes.value.set(foc, new Set());
        }
        allFirstCodes.value.get(foc)?.add(group.title);
      }
    });
  });

  
  point.value.groups.forEach(group => {
    group.firstOrderCodes.forEach((foc, index) => {
      const soc = group.secondOrderCodes[index];
      if (soc) {
        if (!dataMap.has(soc)) {
          dataMap.set(soc, {
            title: soc,
            firstOrderCodes: new Map(),
            expanded: false
          });
        }

        const targetSoc = dataMap.get(soc);
        if (!targetSoc) return;

        const passages = Array.from(allFirstCodes.value.get(foc) || []);

        const existing = targetSoc.firstOrderCodes.get(foc);
        if (existing) {
          if (!existing.passages.includes(group.title)) {
            existing.passages.push(group.title);
          }
        } else {
          targetSoc.firstOrderCodes.set(foc, {
            code: foc,
            passages: passages.length > 1 ? [group.title] : []
          });
        }
      }
    });
  });

  
  processedData.value = Array.from(dataMap.values()).map(soc => ({
    title: soc.title,
    firstOrderCodes: Array.from(soc.firstOrderCodes.values())
      .map(foc => ({
        ...foc,
        passages: (allFirstCodes.value.get(foc.code)?.size || 0) > 1 ? foc.passages : []
      }))
      .sort((a, b) => b.passages.length - a.passages.length), 
    expanded: soc.expanded
  }));
};


updateProcessedData();


watch(() => point.value.groups, updateProcessedData, { deep: true });


const toggleGroup = (index: number) => {
  processedData.value[index].expanded = !processedData.value[index].expanded;
};


const exportToCSV = () => {
  const csvContent = [];
  csvContent.push("SecondOrderCode,FirstOrderCode,Count,Passage,Explanation,Sentence,Stage");

  point.value.groups.forEach(group => {
    group.firstOrderCodes.forEach((foc, index) => {
      const soc = group.secondOrderCodes[index] || "";
      const count = allFirstCodes.value.get(foc)?.size || 0;
      const passageName = `"${group.title}"`;
      const explanation = `"${group.explanations[index]}"`;
      const sentence = `"${group.sentences[index]}"`;
      const stage = `"${group.stages[index]}"`;

      csvContent.push(
        `"${soc}","${foc}",${count},${passageName},${explanation},${sentence},${stage}`
      );
    });
  });

  const blob = new Blob([csvContent.join("\n")], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.href = url;
  link.setAttribute("download", "coding-data.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const emit = defineEmits(['releaseGroup']);
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

.group-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.act-title {
  background: none;
  border: 1px solid #407434;
  color: #407434;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
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
  padding: 4px 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.passage-count {
  color: #666;
  font-size: 0.8em;
  cursor: help;
  padding-left: 8px;
}

.tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.9em;
  pointer-events: none;
  z-index: 1000;
  max-width: 300px;
  word-wrap: break-word;
}
</style>
