<template>
  <div class="h-full border-r-2 p-4 overflow-y-auto relative" @click="handleOutsideClick">
    <div class="flex items-center border-b-2 mb-2 p-1.5 justify-center">
      <div class="font-semibold text-[#407434] file-preview-header">
        File preview
      </div>
      <button @click="toggleSearch" class="ml-2 p-1">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
          <path fill="#407434" d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 0 0 1.48-5.34c-.47-2.78-2.79-5-5.59-5.34a6.505 6.505 0 0 0-7.27 7.27c.34 2.8 2.56 5.12 5.34 5.59a6.5 6.5 0 0 0 5.34-1.48l.27.28v.79l4.25 4.25c.41.41 1.08.41 1.49 0 .41-.41.41-1.08 0-1.49L15.5 14zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        </svg>
      </button>
    </div>
    
    <div v-if="showSearch" class="mb-2">
      <input
        v-model="searchQuery"
        @keyup.enter="searchInContent"
        type="text"
        placeholder="Search within file..."
        class="w-full p-2 border rounded text-sm"
      />
    </div>
    <div
      class="whitespace-pre-wrap break-words text-sm leading-tight p-0 m-0 text-left"
      v-html="highlightedContent"
      @mousemove="handleMouseMove"
      @mouseleave="hideTooltip"
      @contextmenu.prevent="handleRightClick"
      ref="contentRef"
    ></div>

    
    <div 
      v-if="activeHighlight && !editMode"
      class="fixed bg-white border border-[#407434] p-3 rounded-lg shadow-lg z-50 max-w-sm transition-opacity"
      :style="{ left: tooltipX + 'px', top: tooltipY + 'px', pointerEvents: 'none' }"
    >
      <div class="text-[#407434] font-semibold mb-2">{{ activeHighlight.code }}</div>
      <div class="text-gray-600 text-sm">{{ activeHighlight.explanation }}</div>
    </div>

    
    <div 
      v-if="editMode"
      class="edit-panel"
      :style="{ left: editPanelX + 'px', top: editPanelY + 'px' }"
      @click.stop
    >
      
      <div class="edit-panel-header">
        <button @click="deleteCode" class="edit-btn delete-btn" title="Delete this code">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
            <path fill="#dc2626" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
          </svg>
        </button>
        <span class="edit-panel-title">Edit Code</span>
        <div class="flex items-center gap-1">
          
          <button v-if="isModifiedForApplyAll" @click="applyToAll" class="edit-btn" title="Apply to all codes with this name">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <path fill="#407434" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-8 14l-5-5 1.41-1.41L11 14.17l6.59-6.59L19 9l-8 8z"/>
            </svg>
          </button>
          <button @click="saveEdit" class="edit-btn save-btn" title="Save changes">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <path fill="#407434" d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>
            </svg>
          </button>
        </div>
      </div>
      
      <div class="edit-field">
        <label>Code</label>
        <input v-model="editData.code" class="edit-input" />
      </div>
      <div class="edit-field">
        <label>Explanation</label>
        <textarea v-model="editData.explanation" class="edit-textarea" rows="3"></textarea>
      </div>
      <div class="edit-field">
        <label>Stage</label>
        
        <div v-if="!stageTextEdit" class="stage-selector" @click.stop="stageDropdownOpen = !stageDropdownOpen" @dblclick.prevent.stop="enterStageTextEdit">
          <span class="stage-value">{{ editData.stage || 'Select stage...' }}</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" class="stage-chevron" :class="{ 'rotate': stageDropdownOpen }">
            <path fill="#6b7280" d="M7 10l5 5 5-5z"/>
          </svg>
        </div>
        <div v-if="stageDropdownOpen && !stageTextEdit" class="stage-dropdown" @click.stop>
          <div 
            v-for="s in allStages" 
            :key="s" 
            class="stage-option"
            :class="{ 'active': s === editData.stage }"
            @click="selectStage(s)"
          >
            {{ s }}
          </div>
          <div v-if="allStages.length === 0" class="stage-option disabled">No stages available</div>
        </div>
        
        <input 
          v-if="stageTextEdit" 
          v-model="editData.stage" 
          class="edit-input" 
          ref="stageInputRef"
          @blur="stageTextEdit = false"
          @keyup.enter="stageTextEdit = false"
        />
      </div>
      <div class="edit-field">
        <label>second order code</label>
        <div v-if="!secondCodeTextEdit" class="stage-selector" @click.stop="secondCodeDropdownOpen = !secondCodeDropdownOpen" @dblclick.prevent.stop="enterSecondCodeTextEdit">
          <span class="stage-value">{{ editData.secondOrderCode || 'Select code...' }}</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" class="stage-chevron" :class="{ 'rotate': secondCodeDropdownOpen }">
            <path fill="#6b7280" d="M7 10l5 5 5-5z"/>
          </svg>
        </div>
        <div v-if="secondCodeDropdownOpen && !secondCodeTextEdit" class="stage-dropdown" @click.stop>
          <div 
            v-for="sc in allSecondCodes" 
            :key="sc" 
            class="stage-option"
            :class="{ 'active': sc === editData.secondOrderCode }"
            @click="selectSecondCode(sc)"
          >
            {{ sc }}
          </div>
          <div v-if="allSecondCodes.length === 0" class="stage-option disabled">No codes available</div>
        </div>
        <input 
          v-if="secondCodeTextEdit" 
          v-model="editData.secondOrderCode" 
          class="edit-input" 
          ref="secondCodeInputRef"
          @blur="secondCodeTextEdit = false"
          @keyup.enter="secondCodeTextEdit = false"
        />
      </div>
    </div>

    
    <div 
      v-if="addMode"
      class="edit-panel"
      :style="{ left: addPanelX + 'px', top: addPanelY + 'px' }"
      @click.stop
    >
      
      <div class="edit-panel-header">
        <span style="width:22px"></span>
        <span class="edit-panel-title">Add Code</span>
        <button @click="saveNewCode" class="edit-btn save-btn" title="Add new code">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
            <path fill="#407434" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
        </button>
      </div>
      
      <div class="edit-field">
        <label>Code</label>
        <input v-model="addData.code" class="edit-input" />
      </div>
      <div class="edit-field">
        <label>Explanation</label>
        <textarea v-model="addData.explanation" class="edit-textarea" rows="3"></textarea>
      </div>
      <div class="edit-field">
        <label>Stage</label>
        <div v-if="!addStageTextEdit" class="stage-selector" @click.stop="addStageDropdownOpen = !addStageDropdownOpen" @dblclick.prevent.stop="enterAddStageTextEdit">
          <span class="stage-value">{{ addData.stage || 'Select stage...' }}</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" class="stage-chevron" :class="{ 'rotate': addStageDropdownOpen }">
            <path fill="#6b7280" d="M7 10l5 5 5-5z"/>
          </svg>
        </div>
        <div v-if="addStageDropdownOpen && !addStageTextEdit" class="stage-dropdown" @click.stop>
          <div 
            v-for="s in allStages" 
            :key="s" 
            class="stage-option"
            :class="{ 'active': s === addData.stage }"
            @click="selectAddStage(s)"
          >
            {{ s }}
          </div>
          <div v-if="allStages.length === 0" class="stage-option disabled">No stages available</div>
        </div>
        <input 
          v-if="addStageTextEdit" 
          v-model="addData.stage" 
          class="edit-input" 
          ref="addStageInputRef"
          @blur="addStageTextEdit = false"
          @keyup.enter="addStageTextEdit = false"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, nextTick } from 'vue';
import DOMPurify from 'dompurify';
import * as d3 from 'd3';

const props = defineProps({
  content: String,
  currentFile: String,
  passageDatabase: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['update:currentFile']);

const highlightedContent = ref('');
const activeHighlight = ref(null);
const tooltipX = ref(0);
const tooltipY = ref(0);
const contentRef = ref(null);

const showSearch = ref(false);
const searchQuery = ref('');


const editMode = ref(false);
const editPanelX = ref(0);
const editPanelY = ref(0);
const editData = ref({
  code: '',
  explanation: '',
  stage: '',
  secondOrderCode: '',
  originalCode: '',
  originalStage: '',
  originalSecondOrderCode: '',
  idx: -1
});


const stageDropdownOpen = ref(false);
const stageTextEdit = ref(false);
const stageInputRef = ref(null);

const secondCodeDropdownOpen = ref(false);
const secondCodeTextEdit = ref(false);
const secondCodeInputRef = ref(null);


const addMode = ref(false);
const addPanelX = ref(0);
const addPanelY = ref(0);
const addData = ref({
  code: '',
  explanation: '',
  stage: '',
  sentence: ''
});
const addStageDropdownOpen = ref(false);
const addStageTextEdit = ref(false);
const addStageInputRef = ref(null);


const allStages = computed(() => {
  const stagesSet = new Set();
  if (props.passageDatabase) {
    Object.values(props.passageDatabase).forEach(passage => {
      if (passage.stages) {
        passage.stages.forEach(s => { if (s) stagesSet.add(s); });
      }
    });
  }
  return Array.from(stagesSet);
});

const selectStage = (s) => {
  editData.value.stage = s;
  stageDropdownOpen.value = false;
};

const enterStageTextEdit = () => {
  stageDropdownOpen.value = false;
  stageTextEdit.value = true;
  nextTick(() => {
    if (stageInputRef.value) stageInputRef.value.focus();
  });
};

const allSecondCodes = computed(() => {
  const codesSet = new Set();
  if (props.passageDatabase) {
    Object.values(props.passageDatabase).forEach(passage => {
      if (passage.secondOrderCodes) {
        passage.secondOrderCodes.forEach(sc => { if (sc) codesSet.add(sc); });
      }
    });
  }
  return Array.from(codesSet);
});

const selectSecondCode = (sc) => {
  editData.value.secondOrderCode = sc;
  secondCodeDropdownOpen.value = false;
};

const enterSecondCodeTextEdit = () => {
  secondCodeDropdownOpen.value = false;
  secondCodeTextEdit.value = true;
  nextTick(() => {
    if (secondCodeInputRef.value) secondCodeInputRef.value.focus();
  });
};

const isModifiedForApplyAll = computed(() => {
  if (!editMode.value) return false;
  return (
    editData.value.code !== editData.value.originalCode ||
    editData.value.stage !== editData.value.originalStage ||
    editData.value.secondOrderCode !== editData.value.originalSecondOrderCode
  );
});


const lcs = (X, Y) => {
  const m = X.length;
  const n = Y.length;
  const L = Array(m + 1).fill().map(() => Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) {
    for (let j = 0; j <= n; j++) {
      if (i === 0 || j === 0) {
        L[i][j] = 0;
      } else if (X[i - 1] === Y[j - 1]) {
        L[i][j] = L[i - 1][j - 1] + 1;
      } else {
        L[i][j] = Math.max(L[i - 1][j], L[i][j - 1]);
      }
    }
  }
  return L[m][n];
};


const findMostSimilarSentence = (target, sentences) => {
  let maxSimilarity = 0;
  let mostSimilar = null;
  sentences.forEach(sentence => {
    const similarity = lcs(target.trim(), sentence.trim());
    if (similarity > maxSimilarity) {
      maxSimilarity = similarity;
      mostSimilar = sentence;
    }
  });
  return mostSimilar;
};


const splitIntoSentences = (text) => {
  return text.split(/[.!?]+/).filter(s => s.trim() !== '');
};


const updateHighlights = () => {
  if (!props.content || !props.currentFile || !props.passageDatabase || !props.passageDatabase[props.currentFile]) {
    highlightedContent.value = props.content || '';
    return;
  }

  let content = props.content;
  const sentences = splitIntoSentences(props.content);
  const seenSentences = new Set();
  
  const passageData = props.passageDatabase[props.currentFile];
  const { firstOrderCodes, explanations, sentences: passageSentences, stages } = passageData;

  if (passageSentences && passageSentences.length > 0) {
    passageSentences.forEach((passageText, idx) => {
      const code = firstOrderCodes ? firstOrderCodes[idx] : '';
      const explanation = explanations ? explanations[idx] : '';
      const stage = stages ? stages[idx] : '';
      const secondOrderCode = passageData.secondOrderCodes ? passageData.secondOrderCodes[idx] : '';
      
      if (!passageText) return;

      const subSentences = splitIntoSentences(passageText);

      subSentences.forEach(subSentence => {
        if (!subSentence || seenSentences.has(subSentence.toLowerCase())) return;
        seenSentences.add(subSentence.toLowerCase());
    
        const mostSimilar = findMostSimilarSentence(subSentence, sentences);
        if (mostSimilar) {
          const escapeRegExp = (string) => string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const regex = new RegExp(escapeRegExp(mostSimilar), 'g');
          const safeExplanation = (explanation || '').replace(/"/g, '&quot;');
          content = content.replace(regex, (match) =>
            `<span 
              class="highlight" 
              data-code="${code || ''}" 
              data-explanation="${safeExplanation}"
              data-stage="${stage || ''}"
              data-second-order-code="${secondOrderCode || ''}"
              data-idx="${idx}"
              style="background-color: #A0BF7C55; border-bottom: 2px solid #407434; cursor: help;"
            >${match}</span>`
          );
        }
      });
    });
  }

  highlightedContent.value = DOMPurify.sanitize(content);
};


const handleMouseMove = (event) => {
  if (editMode.value || addMode.value) return;
  const highlight = event.target.closest('.highlight');
  if (highlight) {
    activeHighlight.value = {
      code: highlight.dataset.code,
      explanation: highlight.dataset.explanation
    };
    tooltipX.value = event.pageX + 15;
    tooltipY.value = event.pageY + 15;
  } else {
    activeHighlight.value = null;
  }
};


const hideTooltip = () => {
  if (editMode.value || addMode.value) return;
  activeHighlight.value = null;
};


const handleRightClick = (event) => {
  const highlight = event.target.closest('.highlight');
  if (highlight) {
    
    const code = highlight.dataset.code || '';
    const explanation = highlight.dataset.explanation || '';
    const stage = highlight.dataset.stage || '';
    const secondOrderCode = highlight.dataset.secondOrderCode || '';
    const idx = parseInt(highlight.dataset.idx, 10);
    openEditPanel(event.clientX, event.clientY, code, explanation, stage, secondOrderCode, idx);
    return;
  }

  
  const selection = window.getSelection();
  const selectedText = selection ? selection.toString().trim() : '';
  if (selectedText) {
    openAddPanel(event.clientX, event.clientY, selectedText);
  }
};


const openEditPanel = (x, y, code, explanation, stage, secondOrderCode, idx) => {
  editMode.value = true;
  activeHighlight.value = null;
  stageDropdownOpen.value = false;
  stageTextEdit.value = false;
  secondCodeDropdownOpen.value = false;
  secondCodeTextEdit.value = false;

  editPanelX.value = x;
  editPanelY.value = y;

  editData.value = {
    code,
    explanation,
    stage,
    secondOrderCode,
    originalCode: code,
    originalStage: stage,
    originalSecondOrderCode: secondOrderCode,
    idx
  };
};


const editCode = (code) => {
  if (!contentRef.value) return;

  const sentenceSpan = Array.from(contentRef.value.querySelectorAll('.highlight'))
    .find(span => span.dataset.code === code);

  if (!sentenceSpan) return;

  
  editMode.value = false;

  
  const scrollContainer = contentRef.value.closest('.h-full.overflow-y-auto') || contentRef.value.parentElement;

  
  sentenceSpan.scrollIntoView({ behavior: 'smooth', block: 'center' });
  sentenceSpan.style.backgroundColor = '#A0BF7CAA';

  
  let scrollTimer = null;
  let scrollStarted = false;

  const onScrollEnd = () => {
    
    if (scrollContainer) scrollContainer.removeEventListener('scroll', onScroll);
    clearTimeout(fallbackTimer);

    const rect = sentenceSpan.getBoundingClientRect();
    const explanation = sentenceSpan.dataset.explanation || '';
    const stage = sentenceSpan.dataset.stage || '';
    const secondOrderCode = sentenceSpan.dataset.secondOrderCode || '';
    const idx = parseInt(sentenceSpan.dataset.idx, 10);

    openEditPanel(rect.left, rect.bottom + 4, code, explanation, stage, secondOrderCode, idx);
  };

  const onScroll = () => {
    scrollStarted = true;
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(onScrollEnd, 100); 
  };

  if (scrollContainer) {
    scrollContainer.addEventListener('scroll', onScroll);
  }

  
  const fallbackTimer = setTimeout(() => {
    if (!scrollStarted && !editMode.value) {
      if (scrollContainer) scrollContainer.removeEventListener('scroll', onScroll);
      clearTimeout(scrollTimer);
      onScrollEnd();
    }
  }, 600);
};


const handleOutsideClick = () => {
  if (editMode.value) {
    editMode.value = false;
    stageDropdownOpen.value = false;
    stageTextEdit.value = false;
    secondCodeDropdownOpen.value = false;
    secondCodeTextEdit.value = false;
  }
  if (addMode.value) {
    addMode.value = false;
    addStageDropdownOpen.value = false;
    addStageTextEdit.value = false;
  }
};


const saveEdit = () => {
  if (!props.currentFile || !props.passageDatabase || !props.passageDatabase[props.currentFile]) return;

  const passageData = props.passageDatabase[props.currentFile];
  const idx = editData.value.idx;

  if (idx >= 0 && idx < passageData.firstOrderCodes.length) {
    passageData.firstOrderCodes[idx] = editData.value.code;
    if (passageData.explanations) passageData.explanations[idx] = editData.value.explanation;
    if (passageData.stages) passageData.stages[idx] = editData.value.stage;
    if (passageData.secondOrderCodes) passageData.secondOrderCodes[idx] = editData.value.secondOrderCode;
  }

  editMode.value = false;
  stageDropdownOpen.value = false;
  stageTextEdit.value = false;
  secondCodeDropdownOpen.value = false;
  secondCodeTextEdit.value = false;
  updateHighlights();
};


const applyToAll = () => {
  if (!props.passageDatabase) return;

  const originalFirstCode = editData.value.originalCode;
  const newFirstCode = editData.value.code;
  const newStage = editData.value.stage;
  const newSecondCode = editData.value.secondOrderCode;

  Object.values(props.passageDatabase).forEach(passage => {
    if (passage.firstOrderCodes) {
      passage.firstOrderCodes.forEach((code, i) => {
        if (code === originalFirstCode) {
          passage.firstOrderCodes[i] = newFirstCode;
          if (passage.stages) passage.stages[i] = newStage;
          
          if (!passage.secondOrderCodes) passage.secondOrderCodes = new Array(passage.firstOrderCodes.length).fill(null);
          passage.secondOrderCodes[i] = newSecondCode;
        }
      });
    }
  });

  editMode.value = false;
  stageDropdownOpen.value = false;
  stageTextEdit.value = false;
  secondCodeDropdownOpen.value = false;
  secondCodeTextEdit.value = false;
  updateHighlights();
};


const deleteCode = () => {
  if (!props.currentFile || !props.passageDatabase || !props.passageDatabase[props.currentFile]) return;

  const passageData = props.passageDatabase[props.currentFile];
  const idx = editData.value.idx;

  if (idx >= 0 && idx < passageData.firstOrderCodes.length) {
    passageData.firstOrderCodes.splice(idx, 1);
    if (passageData.secondOrderCodes) passageData.secondOrderCodes.splice(idx, 1);
    if (passageData.explanations) passageData.explanations.splice(idx, 1);
    if (passageData.sentences) passageData.sentences.splice(idx, 1);
    if (passageData.stages) passageData.stages.splice(idx, 1);
  }

  editMode.value = false;
  stageDropdownOpen.value = false;
  stageTextEdit.value = false;
  secondCodeDropdownOpen.value = false;
  secondCodeTextEdit.value = false;
  updateHighlights();
};


const openAddPanel = (x, y, sentence) => {
  addMode.value = true;
  editMode.value = false;
  activeHighlight.value = null;
  addStageDropdownOpen.value = false;
  addStageTextEdit.value = false;

  addPanelX.value = x;
  addPanelY.value = y;

  addData.value = {
    code: '',
    explanation: '',
    stage: '',
    sentence
  };
};


const selectAddStage = (s) => {
  addData.value.stage = s;
  addStageDropdownOpen.value = false;
};

const enterAddStageTextEdit = () => {
  addStageDropdownOpen.value = false;
  addStageTextEdit.value = true;
  nextTick(() => {
    if (addStageInputRef.value) addStageInputRef.value.focus();
  });
};


const saveNewCode = () => {
  if (!props.currentFile || !props.passageDatabase) return;

  
  if (!props.passageDatabase[props.currentFile]) {
    props.passageDatabase[props.currentFile] = {
      firstOrderCodes: [],
      secondOrderCodes: [],
      explanations: [],
      sentences: [],
      stages: []
    };
  }

  const passageData = props.passageDatabase[props.currentFile];

  if (!passageData.sentences) passageData.sentences = [];
  if (!passageData.firstOrderCodes) passageData.firstOrderCodes = [];
  if (!passageData.explanations) passageData.explanations = [];
  if (!passageData.stages) passageData.stages = [];

  passageData.sentences.push(addData.value.sentence);
  passageData.firstOrderCodes.push(addData.value.code);
  passageData.explanations.push(addData.value.explanation);
  passageData.stages.push(addData.value.stage);
  if (passageData.secondOrderCodes) passageData.secondOrderCodes.push(null);

  addMode.value = false;
  addStageDropdownOpen.value = false;
  addStageTextEdit.value = false;
  updateHighlights();
};


const toggleSearch = () => {
  showSearch.value = !showSearch.value;
  if (showSearch.value) {
    searchQuery.value = '';
    setTimeout(() => document.querySelector('input')?.focus(), 0);
  }
};


const searchInContent = () => {
  if (!searchQuery.value || !props.currentFile || !props.passageDatabase || !props.passageDatabase[props.currentFile]) return;

  const passageData = props.passageDatabase[props.currentFile];
  const firstOrderCodes = passageData.firstOrderCodes || [];

  const highlightIdx = firstOrderCodes.findIndex(code => code.toLowerCase() === searchQuery.value.toLowerCase());

  if (highlightIdx !== -1 && contentRef.value) {
    const code = firstOrderCodes[highlightIdx];
    const sentenceSpan = Array.from(contentRef.value.querySelectorAll('.highlight'))
      .find(span => span.dataset.code === code);
    if (sentenceSpan) {
      sentenceSpan.scrollIntoView({ behavior: 'smooth', block: 'center' });
      sentenceSpan.style.backgroundColor = '#A0BF7CAA';
      setTimeout(() => {
        sentenceSpan.style.backgroundColor = '#A0BF7C55';
      }, 2000);
    }
  }
};


const jumpToCode = (code) => {
  if (!props.currentFile || !props.passageDatabase || !props.passageDatabase[props.currentFile] || !contentRef.value) return;

  const passageData = props.passageDatabase[props.currentFile];
  const firstOrderCodes = passageData.firstOrderCodes || [];

  const highlightIdx = firstOrderCodes.findIndex(c => c === code);

  if (highlightIdx !== -1) {
    const sentenceSpan = Array.from(contentRef.value.querySelectorAll('.highlight'))
      .find(span => span.dataset.code === code);
    if (sentenceSpan) {
      sentenceSpan.scrollIntoView({ behavior: 'smooth', block: 'center' });
      sentenceSpan.style.backgroundColor = '#A0BF7CAA';
      setTimeout(() => {
        sentenceSpan.style.backgroundColor = '#A0BF7C55';
      }, 2000);
    }
  }
};

defineExpose({ jumpToCode, editCode });


watch(() => [props.content, props.currentFile], () => {
  editMode.value = false;
  addMode.value = false;
  updateHighlights();
}, { immediate: true });

watch(() => props.passageDatabase, () => {
  updateHighlights();
}, { deep: true });

onMounted(() => {
  updateHighlights();
});
</script>

<style scoped>
.highlight {
  transition: background-color 0.2s ease;
}

.highlight:hover {
  background-color: #A0BF7CAA !important;
}

.text-left {
  text-align: left;
}

.file-preview-header {
  padding-top: 0px;
}

.flex.items-center {
  margin-top: -4px;
}


.edit-panel {
  position: fixed;
  z-index: 100;
  background: white;
  border: 2px solid #407434;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
  width: 280px;
  padding: 0;
  overflow: visible;
}

.edit-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f0f7ec;
  padding: 6px 10px;
  border-bottom: 1px solid #d4e6cb;
  border-radius: 8px 8px 0 0;
}

.edit-panel-title {
  font-size: 12px;
  font-weight: 600;
  color: #407434;
}

.edit-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 3px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.edit-btn:hover {
  background: #e5e7eb;
}

.edit-btn.delete-btn:hover {
  background: #fee2e2;
}

.edit-btn.save-btn:hover {
  background: #dcfce7;
}

.edit-field {
  padding: 6px 12px;
  position: relative;
}

.edit-field label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 3px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.edit-input {
  width: 100%;
  padding: 5px 8px;
  border: 1px solid #d1d5db;
  border-radius: 5px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.edit-input:focus {
  border-color: #407434;
  box-shadow: 0 0 0 2px rgba(64, 116, 52, 0.15);
}

.edit-textarea {
  width: 100%;
  padding: 5px 8px;
  border: 1px solid #d1d5db;
  border-radius: 5px;
  font-size: 13px;
  resize: vertical;
  outline: none;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.edit-textarea:focus {
  border-color: #407434;
  box-shadow: 0 0 0 2px rgba(64, 116, 52, 0.15);
}


.stage-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 5px 8px;
  border: 1px solid #d1d5db;
  border-radius: 5px;
  font-size: 13px;
  cursor: pointer;
  background: white;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.stage-selector:hover {
  border-color: #407434;
}

.stage-value {
  color: #374151;
}

.stage-chevron {
  transition: transform 0.2s;
  flex-shrink: 0;
}

.stage-chevron.rotate {
  transform: rotate(180deg);
}

.stage-dropdown {
  position: absolute;
  left: 12px;
  right: 12px;
  top: 100%;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 5px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  z-index: 200;
  max-height: 150px;
  overflow-y: auto;
  margin-top: 2px;
}

.stage-option {
  padding: 6px 10px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.1s;
}

.stage-option:hover {
  background: #f0f7ec;
}

.stage-option.active {
  background: #d4e6cb;
  font-weight: 600;
  color: #407434;
}

.stage-option.disabled {
  color: #9ca3af;
  cursor: default;
  font-style: italic;
}
</style>