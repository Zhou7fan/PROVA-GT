<template>
  <div id="app">
    <div class="app-header flex items-center w-full px-3" :class="{'bg-[#407434] text-white': useAltView}">
      <p>
        <span class="latecweb-text" :class="{'text-white': useAltView, 'text-[#407434]': !useAltView}">PatternWeave</span>
      </p>
      
      <label class="ml-4 cursor-pointer hover:text-green-800 transition-colors">
        <input type="file" @change="handleFileUpload" accept=".txt" multiple class="hidden" />
        <svg class="w-6 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" :style="{ color: useAltView ? 'white' : 'currentColor' }">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </label>
    </div>
    <main class="flex h-[calc(100vh-100px)] border-t">
      <FirstView
        :files="files"
        :use-alt-view="useAltView"
        @select-file="selectFile"
        @delete-file="deleteFile"
        class="border-r p-0 m-0"
        style="width: 150px;"
      />
      <SecondView
        ref="secondViewRef"
        :content="selectedContent"
        :current-file.sync="currentFile"
        :passageDatabase="mainViewRef?.passageDatabase"
        @update:current-file="updateCurrentFile"
        class="border-r p-0"
        style="width: calc((100% / 4) - 100px);"
      />
      <div class="overflow-y-auto border-r p-0 w-3/6">
        <component 
          :is="useAltView ? MainView_all : MainView" 
          ref="mainViewRef"
          :releaseIndex="releaseIndex" 
          :releaseCount="releaseCount" 
          @select-passage="handlePassageSelect"  
        />
      </div>
      
      <div class="right-panel border-l" :class="{ 'full-screen-mode': isMemoFullScreen }" style="width: 400px; min-width: 300px;">
        <component
          v-if="showCollectCode"
          :is="useAltView ? ConfView_all : ConfView"
          @releaseGroup="handleRelease"
          class="p-0"
          style="width: 100%; height: 100%;"
        />
        <MemoPanel
          v-else
          :memos="memoListComputed"
          :isPanelOpen="true"
          :isFullScreen="isMemoFullScreen"
          :passageDatabaseProp="mainViewRef?.passageDatabase"
          @update:isFullScreen="(val) => isMemoFullScreen = val"
          @addMemo="(type) => mainViewRef?.handleAddMemo(type)"
          @deleteMemo="(id) => mainViewRef?.handleDeleteMemo(id)"
          @sortMemos="() => mainViewRef?.handleSortMemos()"
          @saveMemos="() => mainViewRef?.handleSaveMemos()"
          @updateMemos="(m) => { if(mainViewRef) { mainViewRef.memoList = m; mainViewRef.handleSaveMemos(); } }"
          @jump-to-code="({ passageName, code }) => handlePassageSelect({ passageName, code })"
          @edit-code="handleEditCode"
          @show-umap="(payload) => mainViewRef?.showUmapOverlay(payload)"
          @open-chatbot="showChatbot = true"
          @passage-database-changed="handlePdbChanged"
          @memos-changed="() => mainViewRef?.fetchMemos()"
          @add-to-final="(payload) => mainViewRef?.addMemoLinkToFinal(payload)"
        />
      </div>
    </main>

    
    <AIChatbot
      v-if="showChatbot"
      :memos="memoListComputed"
      :passageDatabase="mainViewRef?.passageDatabase || {}"
      :stageOrder="mainViewRef?.stageOrder || []"
      @close="showChatbot = false"
      @memos-changed="() => mainViewRef?.fetchMemos()"
      @passage-database-changed="handlePdbChanged"
    />
  </div>
</template>

<script setup>
import { ref, computed, defineAsyncComponent, provide, onMounted, onUnmounted } from 'vue';
import ConfView from '/components/confView.vue';
import MainView from '/components/mainView.vue';
import FirstView from '/components/FirstView.vue';
import SecondView from '/components/SecondView.vue';
import MemoPanel from '/components/MemoPanel.vue';
import AIChatbot from '/components/AIChatbot.vue';

const MainView_all = defineAsyncComponent(() => import('/components/mainView_all.vue'));
const ConfView_all = defineAsyncComponent(() => import('/components/confView_all.vue'));

const releaseIndex = ref(null);
const releaseCount = ref(0);
const files = ref([]);
const selectedContent = ref('');
const currentFile = ref('');
const useAltView = ref(false);
const latestCsv = ref(null);

const secondViewRef = ref(null);
const mainViewRef = ref(null);


const showCollectCode = ref(false);
const isMemoFullScreen = ref(false);
const showChatbot = ref(false);

provide('secondViewRef', secondViewRef);
provide('latestCsv', latestCsv);
provide('showCollectCode', showCollectCode);


const memoListComputed = computed(() => mainViewRef.value?.memoList || []);


const toggleView = () => {
  if (confirm('Switching views will reset the current state. Continue?')) {
    useAltView.value = !useAltView.value;
  }
};
const updateCurrentFile = (file) => {
  currentFile.value = file;
};

const checkLatestCsv = async () => {
  try {
    const response = await fetch('http://localhost:8000/latest-csv');
    const data = await response.json();
    if (data.filename && data.filename !== latestCsv.value) {
      latestCsv.value = data.filename;
    }
  } catch (error) {
    console.error('Error fetching latest CSV:', error);
  }
};

onMounted(() => {
  checkLatestCsv();
  const interval = setInterval(checkLatestCsv, 3000);
  onUnmounted(() => clearInterval(interval));
});


const handleRelease = (index, count) => {
  releaseIndex.value = index;
  releaseCount.value = count;
};

const handleFileUpload = (event) => {
  const newFiles = Array.from(event.target.files);
  const validFiles = newFiles.filter((file) => file.type === 'text/plain');

  if (validFiles.length === 0) {
    alert('Please select .txt files');
    event.target.value = '';
    return;
  }

  validFiles.forEach((file) => {
    files.value.push({
      name: file.name,
      content: file,
      id: Date.now() + Math.random(),
    });
  });

  event.target.value = '';
};

const selectFile = (fileData) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    selectedContent.value = e.target.result;
    currentFile.value = fileData.name;
  };
  reader.readAsText(fileData.content);
};

const deleteFile = (fileId) => {
  files.value = files.value.filter((f) => f.id !== fileId);
};


const handlePassageSelect = ({ passageName, code }) => {
  console.log('index.vue: Handling passage select:', passageName, code); 
  const file = files.value.find(f => f.name === passageName);
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      selectedContent.value = e.target.result;
      currentFile.value = passageName;
      setTimeout(() => {
        if (secondViewRef.value) {
          console.log('index.vue: Jumping to code:', code);
          secondViewRef.value.jumpToCode(code);
        } else {
          console.error('SecondView ref not available');
        }
      }, 100); 
    };
    reader.readAsText(file.content);
  } else {
    console.error(`File not found for passage: ${passageName}`);
    
    fetchPassageContent(passageName, code);
  }
};


const fetchPassageContent = async (passageName, code) => {
  try {
    
    const response = await fetch(`http://localhost:8000/passage/${passageName}`);
    if (!response.ok) throw new Error('Failed to fetch passage content');
    const text = await response.text();
    selectedContent.value = text;
    currentFile.value = passageName;
    setTimeout(() => {
      if (secondViewRef.value) {
        secondViewRef.value.jumpToCode(code);
      }
    }, 100);
  } catch (error) {
    console.error('Error fetching passage content:', error);
  }
};


const handleEditCode = ({ passageName, code }) => {
  const file = files.value.find(f => f.name === passageName);
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      selectedContent.value = e.target.result;
      currentFile.value = passageName;
      setTimeout(() => {
        if (secondViewRef.value) {
          secondViewRef.value.editCode(code);
        }
      }, 200);
    };
    reader.readAsText(file.content);
  } else {
    
    fetchPassageContentForEdit(passageName, code);
  }
};

const fetchPassageContentForEdit = async (passageName, code) => {
  try {
    const response = await fetch(`http://localhost:8000/passage/${passageName}`);
    if (!response.ok) throw new Error('Failed to fetch passage content');
    const text = await response.text();
    selectedContent.value = text;
    currentFile.value = passageName;
    setTimeout(() => {
      if (secondViewRef.value) {
        secondViewRef.value.editCode(code);
      }
    }, 200);
  } catch (error) {
    console.error('Error fetching passage content for edit:', error);
  }
};

const handlePdbChanged = (newPdb) => {
  if (mainViewRef.value && newPdb) {
    
    Object.keys(mainViewRef.value.passageDatabase).forEach(k => delete mainViewRef.value.passageDatabase[k]);
    Object.assign(mainViewRef.value.passageDatabase, newPdb);
  }
};
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  padding-bottom: 0;
  margin-top: 0px;
  height: auto; 
}

main {
  margin-top: 0px;
  padding-top: 0;
  flex-grow: 1;
}

.latecweb-text {
  font-family: 'Comic Sans MS', cursive;
  font-size: 3rem;
  font-weight: bold;
}

.right-panel {
  overflow-y: auto;
  overflow-x: hidden;
  transition: all 0.3s ease;
  background-color: white; 
}

.right-panel.full-screen-mode {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw !important;
  height: 100vh !important;
  max-width: none !important;
  z-index: 1000;
}
</style>