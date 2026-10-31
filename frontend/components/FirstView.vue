<template>
  <div class="h-full border-r-2 p-4 overflow-y-auto">
    
    <div class="flex justify-between items-center p-2 font-semibold border-b-2 mb-2 file-list-header">
      <div class="text-[#407434]">File List</div>
      <button 
        @click="openPromptDialog"
        class="w-8 h-8 flex items-center justify-center text-gray"
        title="Generate Code"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
      </button>
    </div>

    <div v-for="file in props.files" :key="file.id" 
         class="group flex justify-between items-center p-2 hover:bg-gray-100 cursor-pointer"
         @click="selectFile(file)">
      <div class="file-name">{{ truncateFileName(file.name) }}</div>
      <button @click.stop="deleteFile(file.id)" 
              class="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700">
        ×
      </button>
    </div>

    
    <div v-if="showPromptDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-5xl flex flex-col" style="max-height: 90vh;">
        <div class="flex-1 overflow-y-auto p-6">
          <h2 class="text-lg font-semibold mb-4">Configure Prompt</h2>
          
          
          <div class="flex justify-end mb-4 space-x-2">
            <button 
              @click="exportPrompt" 
              class="bg-blue-500 text-white py-1 px-3 rounded hover:bg-blue-600"
            >
              Export Prompt
            </button>
            <button 
              @click="triggerImportPrompt" 
              class="bg-blue-500 text-white py-1 px-3 rounded hover:bg-blue-600"
            >
              Import Prompt
            </button>
            <button 
              @click="savePromptVersion" 
              class="bg-green-500 text-white py-1 px-3 rounded hover:bg-green-600"
            >
              Save Prompt
            </button>
            <select 
              v-model="selectedVersion" 
              @change="loadPromptVersion"
              class="border rounded p-1 text-gray-700"
            >
              <option value="">Select a version</option>
              <option v-for="(version, index) in promptVersions" :key="index" :value="index">
                {{ version.name }} ({{ version.timestamp }})
              </option>
            </select>
            
            <button 
              v-if="selectedVersion !== ''"
              @click="deleteSelectedVersion"
              class="bg-red-500 text-white py-1 px-3 rounded hover:bg-red-600"
            >
              Delete Prompt
            </button>
            
            <button 
              @click="deleteAllVersions"
              class="bg-red-500 text-white py-1 px-3 rounded hover:bg-red-600"
            >
              Delete All
            </button>
            <input 
              type="file" 
              ref="promptFileInput" 
              @change="importPrompt" 
              accept=".json" 
              class="hidden"
            />
          </div>

          
          <div v-if="selectedVersion !== ''" class="border p-2 rounded mb-4">
            <h4 class="text-sm font-semibold">Comparison with {{ promptVersions[selectedVersion].name }}</h4>
            <div v-if="hasDifferences">
              <p v-if="diff.context" class="text-sm"><strong>Context:</strong> Replace from "{{ promptVersions[selectedVersion].data.context }}" to "{{ promptParts.context }}"</p>
              <p v-if="diff.objective" class="text-sm"><strong>Objective:</strong> Replace from "{{ promptVersions[selectedVersion].data.objective }}" to "{{ promptParts.objective }}"</p>
              <p v-if="diff.style" class="text-sm"><strong>Style:</strong> Replace from "{{ promptVersions[selectedVersion].data.style }}" to "{{ promptParts.style }}"</p>
              <div v-if="diff.lifeStages.length" class="text-sm">
                <strong>Life Stages:</strong>
                <ul>
                  <li v-for="(change, index) in diff.lifeStages" :key="index">{{ change }}</li>
                </ul>
              </div>
              <p v-if="diff.granularity" class="text-sm"><strong>Granularity:</strong> Replace from {{ promptVersions[selectedVersion].data.granularity }} to {{ granularityValue }}</p>
            </div>
            <p v-else class="text-sm text-gray-600">No discrepancies are detected.</p>
          </div>

          
          <div class="mb-4">
            <label class="block font-semibold mb-1">Context</label>
            <textarea 
              v-model="promptParts.context"
              ref="contextTextarea"
              @input="adjustHeight($event.target)"
              class="w-full p-2 border rounded resize-none overflow-y-hidden"
              placeholder="Enter context..."
            ></textarea>
          </div>
          <div class="mb-4">
            <label class="block font-semibold mb-1">Objective</label>
            <textarea 
              v-model="promptParts.objective"
              ref="objectiveTextarea"
              @input="adjustHeight($event.target)"
              class="w-full p-2 border rounded resize-none overflow-y-hidden"
              placeholder="Enter objective..."
            ></textarea>
          </div>
          <div class="mb-4">
            <label class="block font-semibold mb-1">Style</label>
            <textarea 
              v-model="promptParts.style"
              ref="styleTextarea"
              @input="adjustHeight($event.target)"
              class="w-full p-2 border rounded resize-none overflow-y-hidden"
              placeholder="Enter style..."
            ></textarea>
          </div>
          
          <div v-if="!props.useAltView" class="mb-4">
            <label class="block font-semibold mb-1">Response Format (Fixed Structure)</label>
            <p class="text-sm text-gray-600 mb-2">[keyword]#[explanation]#[sentence]#[Concept Stage]</p>
            <label class="block font-semibold mb-1">Define Concept Stages</label>
            <div v-for="(stage, index) in promptParts.lifeStages" :key="index" class="flex items-start mb-2">
              <input 
                v-model="stage.name" 
                class="w-1/3 p-2 border rounded mr-2" 
                placeholder="Stage Name" 
              />
              <textarea 
                v-model="stage.description"
                :ref="el => lifeStageTextareas[index] = el"
                @input="adjustHeight($event.target)"
                class="w-2/3 p-2 border rounded resize-none overflow-y-hidden"
                placeholder="Description"
              ></textarea>
              <button @click="removeLifeStage(index)" class="ml-2 text-red-500 hover:text-red-700">×</button>
            </div>
            <button @click="addLifeStage" class="text-[#407434] hover:underline">+ Add Life Stage</button>
          </div>
          
          <div class="relative mt-4">
            <input 
              type="range" 
              v-model="granularityValue" 
              min="3000" 
              max="8000" 
              step="1" 
              class="w-full appearance-none h-2 bg-gray-200 rounded-lg outline-none focus:outline-none"
            />
            <div class="absolute top-[-10px] left-0 right-0 flex justify-between px-2 text-sm">
              <span>Fine</span>
              <span>Medium</span>
              <span>Coarse</span>
            </div>
            <div class="mt-2 text-center">
              <span>Text slice size: {{ granularityValue }}</span>
            </div>
          </div>
        </div>
        <div class="p-6 border-t flex justify-end">
          <button @click="closePromptDialog" class="mr-2 bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600">Cancel</button>
          <button @click="startProcess" class="bg-[#407434] text-white py-2 px-4 rounded hover:bg-[#305a2a]">Submit</button>
        </div>
      </div>
    </div>

    
    <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg">
        <div class="flex items-center">
          <div class="animate-spin mr-2">⏳</div>
          <div>
            Processing... Completed {{ processedCount }}/{{ totalFiles }} files,
            <span v-if="currentFile">
              Processing chunk {{ currentChunk }}/{{ totalChunks }} of {{ currentFile }}
            </span>
          </div>
        </div>
      </div>
    </div>
    <div v-if="errorMessage" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 class="text-lg font-semibold mb-4 text-red-500">Error</h2>
        <p class="mb-4">{{ errorMessage }}</p>
        <button @click="errorMessage = ''" class="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-700">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue';

const props = defineProps({
  files: { type: Array, required: true },
  useAltView: { type: Boolean, default: false }
});
const emit = defineEmits(['select-file', 'delete-file']);

const showPromptDialog = ref(false);
const granularityValue = ref(3000);
const loading = ref(false);
const errorMessage = ref('');
const processedCount = ref(0);
const totalFiles = ref(0);
const currentFile = ref('');
const currentChunk = ref(0);
const totalChunks = ref(0);
const contextTextarea = ref(null);
const objectiveTextarea = ref(null);
const styleTextarea = ref(null);
const lifeStageTextareas = ref([]);
const promptFileInput = ref(null);
const promptVersions = ref([]); 
const selectedVersion = ref(''); 
const diff = ref({}); 
let pollInterval = null;

const promptParts = ref({
  context: '[Context: This research project examines the life events of social entrepreneurs, defined as founders or co-founders of Non-profit Organizations. The following is PART OF an interview transcript with a social entrepreneur.]',
  objective: '[Objective: Extract keywords that encapsulate recurring themes across diverse life stories. These keywords must:{-Be highly abstract, universally applicable, and capture the essence of events or experiences, focusing on their function and significance rather than specific details.}{-Relate to:1. The origins and underlying motivations for establishing the social enterprise.2. The life trajectory and pivotal experiences shaping the individual’s entrepreneurial journey.3. The developmental processes and formative influences constructing their identity as a social entrepreneur.{-Emphasize consistency by identifying common patterns across different interviewees, avoiding terms that are overly specific, contextually unique, or tied to particular individuals or organizations.{-Avoid being influenced by superficial characteristics, such as names or specific locations, to ensure keywords reflect broader themes.]For example:[personal background]#[birthplace/family/school etc.]#[Um, so i am a kiwi by birth. Ah, but when I was four years old, my parents moved to Bangladesh, which is really random. But um, I spent ten years there and actually went to a boarding school in India.]#[Childhood Stage]',
  style: '[Style: Employ the conventions of academic writing. Tone: Maintain the formal tone of scholarly discourse.]',
  lifeStages: [
    { name: 'Childhood Stage', description: 'Early life phase fostering foundational attributes and values.' },
    { name: 'Foundation Stage', description: 'Period of acquiring essential skills, resources, or networks for future pursuits.' },
    { name: 'Pre-enterprise Stage', description: 'Phase of preparation, opportunity identification, or planning prior to enterprise creation.' },
    { name: 'Enterprise Stage', description: 'Active involvement in establishing and managing the social enterprise.' }
  ]
});


const adjustHeight = (textarea) => {
  if (!textarea) return;
  textarea.style.height = 'auto'; 
  textarea.style.height = `${textarea.scrollHeight}px`; 
};


const adjustAllTextareas = () => {
  nextTick(() => {
    [contextTextarea.value, objectiveTextarea.value, styleTextarea.value, ...lifeStageTextareas.value]
      .filter(Boolean)
      .forEach(adjustHeight);
  });
};


const loadVersionsFromStorage = () => {
  const storedVersions = localStorage.getItem('promptVersions');
  if (storedVersions) {
    promptVersions.value = JSON.parse(storedVersions);
  }
};


const savePromptVersion = () => {
  const versionName = prompt('Enter a name for this version:', `Version ${promptVersions.value.length + 1}`);
  if (!versionName) return;

  const newVersion = {
    name: versionName,
    timestamp: new Date().toLocaleString(),
    data: {
      context: promptParts.value.context,
      objective: promptParts.value.objective,
      style: promptParts.value.style,
      lifeStages: JSON.parse(JSON.stringify(promptParts.value.lifeStages)),
      granularity: granularityValue.value
    }
  };

  promptVersions.value.push(newVersion);
  localStorage.setItem('promptVersions', JSON.stringify(promptVersions.value));
  selectedVersion.value = ''; 
  diff.value = {}; 
};


const loadPromptVersion = () => {
  if (selectedVersion.value === '' || !promptVersions.value[selectedVersion.value]) {
    diff.value = {};
    return;
  }

  const version = promptVersions.value[selectedVersion.value].data;
  promptParts.value.context = version.context;
  promptParts.value.objective = version.objective;
  promptParts.value.style = version.style;
  promptParts.value.lifeStages = JSON.parse(JSON.stringify(version.lifeStages));
  granularityValue.value = version.granularity;

  nextTick(() => adjustAllTextareas());
  computeDifferences();
};


const deleteSelectedVersion = () => {
  if (selectedVersion.value === '') return;
  
  if (!confirm(`Delete version "${promptVersions.value[selectedVersion.value].name}"?`)) return;
  
  promptVersions.value.splice(selectedVersion.value, 1);
  localStorage.setItem('promptVersions', JSON.stringify(promptVersions.value));
  selectedVersion.value = ''; 
  diff.value = {}; 
};


const deleteAllVersions = () => {
  if (promptVersions.value.length === 0) {
    alert('No versions to delete');
    return;
  }
  
  if (!confirm('Delete all versions? This action cannot be undone.')) return;
  
  promptVersions.value = [];
  localStorage.setItem('promptVersions', JSON.stringify(promptVersions.value));
  selectedVersion.value = ''; 
  diff.value = {}; 
};


const computeDifferences = () => {
  if (selectedVersion.value === '' || !promptVersions.value[selectedVersion.value]) {
    diff.value = {};
    return;
  }

  const version = promptVersions.value[selectedVersion.value].data;
  diff.value = {
    context: version.context !== promptParts.value.context,
    objective: version.objective !== promptParts.value.objective,
    style: version.style !== promptParts.value.style,
    lifeStages: [],
    granularity: version.granularity !== granularityValue.value
  };

  
  const oldStages = version.lifeStages;
  const newStages = promptParts.value.lifeStages;
  if (JSON.stringify(oldStages) !== JSON.stringify(newStages)) {
    oldStages.forEach((oldStage, index) => {
      const newStage = newStages[index];
      if (!newStage) {
        diff.value.lifeStages.push(`Removed stage: ${oldStage.name}`);
      } else if (oldStage.name !== newStage.name || oldStage.description !== newStage.description) {
        diff.value.lifeStages.push(`Modified stage: ${oldStage.name} -> ${newStage.name}, description changed from "${oldStage.description}" to "${newStage.description}"`);
      }
    });
    newStages.slice(oldStages.length).forEach(newStage => {
      diff.value.lifeStages.push(`Added stage: ${newStage.name} (${newStage.description})`);
    });
  }
};


const hasDifferences = computed(() => {
  return diff.value.context || diff.value.objective || diff.value.style || diff.value.lifeStages.length > 0 || diff.value.granularity;
});


onMounted(() => {
  loadVersionsFromStorage();
  watch(showPromptDialog, (newVal) => {
    if (newVal) adjustAllTextareas();
  });
  watch(() => promptParts.value, () => {
    adjustAllTextareas();
    computeDifferences();
  }, { deep: true });
  watch(granularityValue, () => computeDifferences());
  watch(promptVersions, () => {
    if (selectedVersion.value !== '' && !promptVersions.value[selectedVersion.value]) {
      selectedVersion.value = '';
    }
    computeDifferences();
  }, { deep: true });
});

const addLifeStage = () => {
  promptParts.value.lifeStages.push({ name: '', description: '' });
  nextTick(() => adjustAllTextareas());
};
const removeLifeStage = (index) => {
  promptParts.value.lifeStages.splice(index, 1);
  nextTick(() => adjustAllTextareas());
};

const truncateFileName = (name) => {
  const maxLength = 20;
  if (name.length > maxLength) return name.substring(0, maxLength - 3) + '...';
  return name;
};

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval);
});

const updateProgress = async () => {
  try {
    const response = await fetch('http://localhost:8000/progress');
    if (!response.ok) return;
    const data = await response.json();
    processedCount.value = data.processed_files;
    currentFile.value = data.current_file;
    currentChunk.value = data.current_chunk;
    totalChunks.value = data.total_chunks;
    totalFiles.value = data.total_files;
  } catch (error) {
    console.error('Error fetching progress:', error);
  }
};


const exportPrompt = () => {
  const promptData = {
    context: promptParts.value.context,
    objective: promptParts.value.objective,
    style: promptParts.value.style,
    lifeStages: promptParts.value.lifeStages,
    granularity: granularityValue.value
  };
  
  const jsonString = JSON.stringify(promptData, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `prompt-config-${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};


const triggerImportPrompt = () => {
  promptFileInput.value.click();
};


const importPrompt = (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const importedData = JSON.parse(e.target.result);
      
      if (!importedData.context || !importedData.objective || !importedData.style) {
        throw new Error('Invalid prompt format: missing required fields');
      }

      promptParts.value.context = importedData.context;
      promptParts.value.objective = importedData.objective;
      promptParts.value.style = importedData.style;
      
      if (importedData.lifeStages && Array.isArray(importedData.lifeStages)) {
        promptParts.value.lifeStages = importedData.lifeStages.map(stage => ({
          name: stage.name || '',
          description: stage.description || ''
        }));
      }

      if (importedData.granularity && typeof importedData.granularity === 'number') {
        granularityValue.value = Math.max(3000, Math.min(8000, importedData.granularity));
      }

      event.target.value = '';
      
      nextTick(() => adjustAllTextareas());
    } catch (error) {
      errorMessage.value = `Failed to import prompt: ${error.message}`;
    }
  };
  reader.readAsText(file);
};

const startProcess = async () => {
  loading.value = true;
  errorMessage.value = '';
  processedCount.value = 0;
  totalFiles.value = props.files.length;
  currentFile.value = '';
  currentChunk.value = 0;
  totalChunks.value = 0;

  const lifeStagesText = props.useAltView ? '' : 
    promptParts.value.lifeStages.map((stage, index) => `${index + 1}. ${stage.name}: ${stage.description}`).join(' ');

  const assembledPrompt = props.useAltView ? 
    `##${promptParts.value.context}##${promptParts.value.objective}##${promptParts.value.style}##[Response: Extract keywords alongside their corresponding original content, presented in a line-by-line format. Each entry must adhere to the following structure: [keyword(all in lowercase letters)]#[explanation]#[most related sentence(no quotation marks)].Sentences must be verbatim from the transcript. Should the response exceed the character limit, eliminate entries of lesser thematic significance to ensure compliance with formatting requirements. Output must be in English, devoid of supplementary commentary beyond the specified format.]Script:{chunk}` :
    `##${promptParts.value.context}##${promptParts.value.objective}##${promptParts.value.style}##[Response: Extract keywords alongside their corresponding original content, presented in a line-by-line format. Each entry must adhere to the following structure: [keyword(all in lowercase letters)]#[explanation]#[most related sentence(no quotation marks)]#[Concept Stage].Concept Stage classifications are: ${lifeStagesText}. Your should analyze the content and determine which stage it belongs to.Sentences must be verbatim from the transcript. Should the response exceed the character limit, eliminate entries of lesser thematic significance to ensure compliance with formatting requirements. Output must be in English, devoid of supplementary commentary beyond the specified format.]Script:{chunk}`;

  pollInterval = setInterval(updateProgress, 500);

  try {
    const formData = new FormData();
    props.files.forEach((file) => {
      if (file.content) formData.append('files', file.content);
    });
    formData.append('granularityValue', granularityValue.value);
    formData.append('prompt', assembledPrompt);

    const response = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Processing failed');
    alert(`Success! Processed ${data.processed_files.length} files. Total codes: ${data.total_codes}`);
  } catch (error) {
    console.error('Error:', error);
    errorMessage.value = error.message;
  } finally {
    clearInterval(pollInterval);
    loading.value = false;
    closePromptDialog();
  }
};

const selectFile = (file) => {
  emit('select-file', { content: file.content, name: file.name });
};
const deleteFile = (fileId) => {
  emit('delete-file', fileId);
};

const openPromptDialog = () => {
  showPromptDialog.value = true;
  adjustAllTextareas();
};

const closePromptDialog = () => {
  showPromptDialog.value = false;
};
</script>

<style scoped>
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #407434;
  border-radius: 50%;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #407434;
  border-radius: 50%;
  cursor: pointer;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

.file-name {
  text-align: left;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-list-header {
  padding-top: 0px; 
}

.h-full.border-r-2.p-4.overflow-y-auto {
  padding-top: 0.8rem;
}

textarea {
  box-sizing: border-box;
}
</style>