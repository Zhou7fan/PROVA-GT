<template>
    <div class="memo-panel">
      
      <div class="memo-header">
        <div class="header-left">
          <button @click="exportMarkdown" class="memo-btn" title="Export Markdown">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
            </svg>
          </button>
          <button @click="showAIChatbot = !showAIChatbot" class="memo-btn ai-chat-btn" title="AI Chatbot">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="white" d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A2.5 2.5 0 0 0 5 15.5 2.5 2.5 0 0 0 7.5 18a2.5 2.5 0 0 0 2.5-2.5A2.5 2.5 0 0 0 7.5 13m9 0a2.5 2.5 0 0 0-2.5 2.5 2.5 2.5 0 0 0 2.5 2.5 2.5 2.5 0 0 0 2.5-2.5 2.5 2.5 0 0 0-2.5-2.5z"/>
            </svg>
          </button>
        </div>
        <h2 class="header-title">Memos</h2>
        <div class="header-right">
          <button @click="showAddMenu = !showAddMenu" class="memo-btn" title="Add Memo">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
          </button>
          <div v-if="showAddMenu" class="add-menu">
            <button v-for="t in memoTypes" :key="t" @click="handleAddMemo(t)">{{ t }}</button>
          </div>
          <button @click="sortMemos" class="memo-btn" title="Sort by Type">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z"/>
            </svg>
          </button>
          <button @click="isDragging = !isDragging" class="memo-btn" :class="{ active: isDragging }" title="Drag Mode">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M11 18c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zm-2-8c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm6 4c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
            </svg>
          </button>
          <button @click="toggleFullScreen" class="memo-btn" title="Toggle Fullscreen">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
            </svg>
          </button>
        </div>
      </div>

      
      <div class="memo-body">
        
        <div v-show="showAIChatbot" class="inline-chatbot-container">
          <AIChatbot 
             :memos="memos" 
             :passageDatabase="passageDatabase" 
             :stageOrder="stageOrder"
             @close="showAIChatbot = false"
             @ai-memo-operation="handleAiMemoOp"
             @memos-changed="$emit('memos-changed')"
             @passage-database-changed="p => $emit('passage-database-changed', p)"
          />
        </div>

        <div
          v-for="(memo, index) in memos"
          :key="memo.id"
          class="memo-card"
          :class="memoClass(memo.type)"
          :draggable="isDragging"
          @dragstart="onDragStart(index, $event)"
          @dragover.prevent
          @drop="onDrop(index)"
        >
        <div class="memo-card-header">
          <input v-model="memo.title" class="memo-title-input" @change="saveMemos" placeholder="Title"/>
          <span class="memo-type-badge">{{ (memo.type || '').split(' ')[0] }}</span>

          <button v-if="memo.type === 'Second-Order Code Notes'" @click="handleShowUmap(memo)" class="ai-btn umap-btn" title="UMAP Scatter Plot">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <circle cx="6" cy="6" r="2" fill="currentColor"/>
              <circle cx="18" cy="8" r="2" fill="currentColor"/>
              <circle cx="10" cy="16" r="2" fill="currentColor"/>
              <circle cx="16" cy="18" r="2" fill="currentColor"/>
              <circle cx="12" cy="10" r="2" fill="currentColor"/>
            </svg>
          </button>

          <button v-if="memo.type === 'Cluster Analysis Notes'" @click="toggleClusterExpanded(memo.id)" class="ai-btn" :class="{ active: clusterExpandedState[memo.id] }" title="Toggle Cluster Extracts">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14z" v-if="clusterExpandedState[memo.id]"/>
              <path fill="currentColor" d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z" v-else/>
            </svg>
          </button>

          <button v-if="memo.type !== 'Cluster Analysis Notes' && memo.type !== 'Analytical Memos'" @click="analyzeMemo(memo)" class="ai-btn" title="Analyze/Search">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
          </button>

          <button @click="toggleAIForm(memo, 'ai')" class="ai-btn" :class="{ active: activeAIFormId === memo.id && activeFormMode === 'ai' }" title="AI Assist">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A2.5 2.5 0 0 0 5 15.5 2.5 2.5 0 0 0 7.5 18a2.5 2.5 0 0 0 2.5-2.5A2.5 2.5 0 0 0 7.5 13m9 0a2.5 2.5 0 0 0-2.5 2.5 2.5 2.5 0 0 0 2.5 2.5 2.5 2.5 0 0 0 2.5-2.5 2.5 2.5 0 0 0-2.5-2.5z"/>
            </svg>
          </button>
  
  <button @click="deleteMemo(memo.id)" class="delete-btn" title="Delete">×</button>
</div>

          
          <div v-if="activeAIFormId === memo.id" class="ai-form">
            
            <label class="ai-form-label">Ask a question about this memo:</label>
            <textarea 
              v-model="memoQuestion" 
              class="ai-form-textarea" 
              placeholder=""
              rows="3"
            ></textarea>
            <div class="ai-form-actions">
              <button @click="submitMemoQuestion(memo)" class="ai-submit-btn">💬 Ask AI</button>
              <button @click="closeAIForm(memo)" class="ai-cancel-btn">Cancel</button>
            </div>

            
            <div v-if="aiLoading && loadingMemoId === memo.id" class="ai-form-loading">
              <div class="spinner-small"></div>
              <span>AI is analyzing...</span>
            </div>
          </div>

          
          <div v-if="activeAIFormId === memo.id && memoAIResponses[memo.id]" class="ai-response-panel">
            <div class="ai-response-header">
              <span class="ai-response-title">🤖 AI Response</span>
              <button @click="clearAIResponse(memo.id)" class="clear-response-btn">Clear</button>
            </div>
            <div class="ai-response-content" v-html="formatAIResponse(memoAIResponses[memo.id])"></div>
          </div>

          
          <div v-if="memo.traceData && activeTraceId === memo.id" class="trace-results">
            <div class="trace-header">
              <span class="trace-title">Source Trace: {{ memo.title }}</span>
              <button @click="activeTraceId = null" class="close-trace-btn">×</button>
            </div>
            
            
            <div v-if="memo.type === 'First-Order Code Notes'" class="trace-list">
              <div v-for="(item, idx) in memo.traceData" :key="idx" class="trace-item">
                <div class="trace-source" @click="handleTraceJump(item.passage, memo.title)">
                  <span class="chip-edit" @click.stop="handleEditCode(item.passage, memo.title)" title="Edit in preview">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"><path fill="#407434" d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>
                  </span>
                  📄 {{ item.passage }}
                  <span class="chip-delete" @click.stop="deleteFirstOrderCode(item.passage, memo.title, memo)">×</span>
                </div>
                <div class="trace-sentence">"{{ item.sentence }}"</div>
                <div class="trace-explanation" v-if="item.explanation">Note: {{ item.explanation }}</div>
              </div>
              <div v-if="memo.traceData.length === 0" class="no-trace">No matches found.</div>
            </div>

            
            <div v-if="memo.type === 'Second-Order Code Notes'" class="trace-list">
              <div v-for="(group, passageName) in groupByPassage(memo.traceData)" :key="passageName" class="trace-group">
                <div class="trace-source-header">📄 {{ passageName }}</div>
                <div class="trace-chips">
                  <span 
                    v-for="(item, idx) in group" 
                    :key="idx" 
                    class="trace-chip"
                    :title="item.explanation"
                    @click="handleTraceJump(passageName, item.code)"
                  >
                    <span class="chip-edit" @click.stop="handleEditCode(item.passage || passageName, item.code)" title="Edit in preview">
                      <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24"><path fill="#407434" d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>
                    </span>
                    {{ item.code }}
                    <span class="chip-delete" @click.stop="deleteFirstOrderCode(item.passage || passageName, item.code, memo)">×</span>
                  </span>
                </div>
              </div>
              <div v-if="!memo.traceData || memo.traceData.length === 0" class="no-trace">No first-order codes found.</div>
            </div>
            
            <div v-if="memo.type === 'Theoretical Memos'" class="trace-list">
               <div v-for="result in memo.traceData" :key="result.passageName" class="trace-group">
                <div class="trace-source-header" style="display: flex; justify-content: space-between; align-items: center;">
                  <span @click="handleTraceJump(result.passageName, result.code1Data.code)" style="cursor: pointer;">📄 {{ result.passageName }}</span>
                  <button class="btn btn-icon-text" style="padding: 2px 4px; font-size: 0.75rem;" title="Add Link to Final View" @click.stop="$emit('add-to-final', { code1: result.code1Data.code, code2: result.code2Data.code })">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"><path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
                  </button>
                </div>
                
                
                <div class="trace-sub-group">
                  <div class="trace-detail-item">
                    <div class="trace-code-tag" @click="handleTraceJump(result.passageName, result.code1Data.code)"><span class="chip-edit" @click.stop="handleEditCode(result.passageName, result.code1Data.code)" title="Edit in preview"><svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24"><path fill="#407434" d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg></span>{{ result.code1Data.code }}<span class="chip-delete" @click.stop="deleteFirstOrderCode(result.passageName, result.code1Data.code, memo)">×</span></div>
                    <div class="trace-context">
                      <div class="trace-sentence">"{{ result.code1Data.sentence }}"</div>
                      <div class="trace-explanation">Note: {{ result.code1Data.explanation }}</div>
                    </div>
                  </div>
                </div>
                
                
                <div class="trace-sub-group">
                  <div class="trace-detail-item">
                    <div class="trace-code-tag" @click="handleTraceJump(result.passageName, result.code2Data.code)"><span class="chip-edit" @click.stop="handleEditCode(result.passageName, result.code2Data.code)" title="Edit in preview"><svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24"><path fill="#407434" d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg></span>{{ result.code2Data.code }}<span class="chip-delete" @click.stop="deleteFirstOrderCode(result.passageName, result.code2Data.code, memo)">×</span></div>
                    <div class="trace-context">
                      <div class="trace-sentence">"{{ result.code2Data.sentence }}"</div>
                      <div class="trace-explanation">Note: {{ result.code2Data.explanation }}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="!memo.traceData || memo.traceData.length === 0" class="no-trace">No passages found containing both codes.</div>
            </div>
          </div>

          
          <div v-if="memo.type === 'Cluster Analysis Notes' && memo.clusterData" class="cluster-results">
            <div v-show="clusterExpandedState[memo.id]">
             <details v-for="(cluster, idx) in memo.clusterData" :key="idx" class="cluster-details">
                <summary class="cluster-summary">
                   <strong>{{ cluster.code }}</strong> ({{ cluster.items.length }})
                </summary>
                <div class="cluster-item-list">
                   <div v-for="(item, i) in cluster.items" :key="i" class="cluster-item">
                      <div class="trace-source" @click="$emit('jump-to-code', { passageName: item.passage, code: cluster.code })">
                        📄 {{ item.passage }}
                        <span class="soc-badge" v-if="item.originalSecondOrderCode" title="Original Second Order Code">[{{ item.originalSecondOrderCode }}]</span>
                      </div>
                      <div class="trace-sentence" v-if="item.sentence">"{{ item.sentence }}"</div>
                      <div class="trace-explanation" v-if="item.explanation">Note: {{ item.explanation }}</div>
                   </div>
                 </div>
             </details>
            </div>
          </div>

          <textarea v-model="memo.content" class="memo-content" @change="saveMemos" placeholder="Write your memo here..."></textarea>
        </div>
        <div v-if="memos.length === 0" class="empty-hint">
          Click "+" to create a new memo.
        </div>
      </div>
    </div>
</template>
<script setup lang="ts">
import { ref, inject, computed } from 'vue';
import type { Memo } from '~/composables/memo';
import AIChatbot from './AIChatbot.vue';

const props = defineProps<{
  memos: Memo[];
  isPanelOpen: boolean;
  isFullScreen: boolean;
  passageDatabaseProp?: any;
  stageOrder?: string[];
}>();

const emit = defineEmits<{
  (e: 'update:isPanelOpen', val: boolean): void;
  (e: 'update:isFullScreen', val: boolean): void;
  (e: 'addMemo', type: Memo['type']): void;
  (e: 'deleteMemo', id: string): void;
  (e: 'sortMemos'): void;
  (e: 'saveMemos'): void;
  (e: 'updateMemos', memos: Memo[]): void;
  (e: 'jump-to-code', payload: { passageName: string, code: string }): void;
  (e: 'edit-code', payload: { passageName: string, code: string }): void;
  (e: 'show-umap', payload: { secondCodeName: string, firstOrderCodes: string[] }): void;
  (e: 'open-chatbot'): void;
  (e: 'passage-database-changed', pdb: Record<string, any>): void;
  (e: 'memos-changed'): void;
  (e: 'add-to-final', payload: { code1: string, code2: string }): void;
}>();

const memoTypes: Memo['type'][] = [
  'First-Order Code Notes',
  'Second-Order Code Notes',
  'Theoretical Memos',
  'Analytical Memos',
  'Cluster Analysis Notes'
];

const showAddMenu = ref(false);
const isDragging = ref(false);
const dragIndex = ref<number | null>(null);

const showAIChatbot = ref(false);

const handleAiMemoOp = (op: any) => {
  
  
  
  
  console.log('AI memo operation confirmed:', op.toolName);
};


const activeAIFormId = ref<string | null>(null);
const activeFormMode = ref<'ai' | 'search'>('ai');
const activeTraceId = ref<string | null>(null);
const aiLoading = ref(false);
const loadingMemoId = ref<string | null>(null);


const firstOrderCodeInput = ref('');
const secondOrderCodeInput = ref('');
const theoryCodes = ref<{ name: string; type: string }[]>([{ name: '', type: 'First-Order' }]);
const analyticalQuestion = ref('');


const memoQuestion = ref('');
const memoAIResponses = ref<Record<string, string>>({});


const clusterExpandedState = ref<Record<string, boolean>>({});
const toggleClusterExpanded = (id: string) => {
  clusterExpandedState.value[id] = !clusterExpandedState.value[id];
};


const injectedPassageDatabase = inject<any>('passageDatabase', null);
const passageDatabase = computed(() => props.passageDatabaseProp || injectedPassageDatabase);

const isFullScreen = ref(props.isFullScreen);

const toggleFullScreen = () => {
  isFullScreen.value = !isFullScreen.value;
  emit('update:isFullScreen', isFullScreen.value);
};

const handleAddMemo = (type: Memo['type']) => {
  emit('addMemo', type);
  showAddMenu.value = false;
};

const deleteMemo = (id: string) => emit('deleteMemo', id);
const sortMemos = () => emit('sortMemos');
const saveMemos = () => emit('saveMemos');

const memoClass = (type: Memo['type']) => {
  return {
    'type-first': type === 'First-Order Code Notes',
    'type-second': type === 'Second-Order Code Notes',
    'type-theory': type === 'Theoretical Memos',
    'type-analytical': type === 'Analytical Memos',
    'type-cluster': type === 'Cluster Analysis Notes'
  };
};

const onDragStart = (index: number, event: DragEvent) => {
  dragIndex.value = index;
};

const onDrop = (targetIndex: number) => {
  if (dragIndex.value === null || dragIndex.value === targetIndex) return;
  const newMemos = [...props.memos];
  const [moved] = newMemos.splice(dragIndex.value, 1);
  newMemos.splice(targetIndex, 0, moved);
  emit('updateMemos', newMemos);
  dragIndex.value = null;
};


const toggleAIForm = (memo: Memo, mode: 'ai' | 'search' = 'ai') => {
  if (activeAIFormId.value === memo.id) {
    if (activeFormMode.value === mode) {
      activeAIFormId.value = null;
    } else {
      activeFormMode.value = mode;
    }
  } else {
    activeAIFormId.value = memo.id;
    activeFormMode.value = mode;
    activeTraceId.value = null; 
    
    
    firstOrderCodeInput.value = memo.title || '';
    secondOrderCodeInput.value = memo.title || '';
    theoryCodes.value = [{ name: '', type: 'First-Order' }];
    analyticalQuestion.value = '';
    memoQuestion.value = '';
  }
};


const closeAIForm = (memo: Memo) => {
  activeAIFormId.value = null;
  memoQuestion.value = '';
};


const clearAIResponse = (memoId: string) => {
  delete memoAIResponses.value[memoId];
};


const formatAIResponse = (text: string): string => {
  if (!text) return '';
  
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
};


const collectAnalyzeMemoInfo = (memo: Memo): any => {
  if (!memo.title || !memo.title.trim()) {
    return null;
  }
  
  if (memo.type === 'First-Order Code Notes') {
    
    const traceData: any[] = [];
    const code = memo.title.trim().toLowerCase();
    
    if (passageDatabase.value) {
      Object.entries(passageDatabase.value).forEach(([passageName, p]: [string, any]) => {
        p.firstOrderCodes.forEach((foc: string, idx: number) => {
          if (foc.toLowerCase() === code) {
            traceData.push({
              passage: passageName,
              explanation: p.explanations[idx] || '',
              sentence: p.sentences ? p.sentences[idx] : '',
              stage: p.stages ? p.stages[idx] : ''
            });
          }
        });
      });
    }
    
    if (traceData.length === 0) {
      return null;
    }
    
    return {
      type: 'first-order-trace',
      code: memo.title,
      passages: traceData.map((item: any) => ({
        passage: item.passage,
        sentence: item.sentence || '',
        explanation: item.explanation || '',
        stage: item.stage || ''
      }))
    };
  } else if (memo.type === 'Second-Order Code Notes') {
    
    const traceData: any[] = [];
    const soc = memo.title.trim().toLowerCase();

    if (passageDatabase.value) {
      Object.entries(passageDatabase.value).forEach(([passageName, p]: [string, any]) => {
        p.firstOrderCodes.forEach((foc: string, idx: number) => {
          const currentSoc = (p.secondOrderCodes[idx] || '').toLowerCase();
          if (currentSoc === soc) {
            traceData.push({
              code: foc,
              passage: passageName,
              explanation: p.explanations[idx] || '',
              stage: p.stages ? p.stages[idx] : ''
            });
          }
        });
      });
    }
    
    if (traceData.length === 0) {
      return null;
    }
    
    return {
      type: 'second-order-trace',
      secondOrderCode: memo.title,
      firstOrderCodes: traceData.map((item: any) => ({
        code: item.code,
        passage: item.passage,
        explanation: item.explanation || '',
        stage: item.stage || ''
      }))
    };
  } else if (memo.type === 'Theoretical Memos') {
    
    const traceData = searchTheoreticalLink(memo.title);
    if (traceData.length > 0) {
      memo.traceData = traceData;
      return {
        type: 'theory-trace',
        title: memo.title,
        results: traceData
      };
    }
    return null;
  } else if (memo.type === 'Analytical Memos') {
    
    return null;
  }
  
  return null;
};


const submitMemoQuestion = async (memo: Memo) => {
  const question = memoQuestion.value.trim();
  if (!question) {
    alert('Please enter a question');
    return;
  }

  aiLoading.value = true;
  loadingMemoId.value = memo.id;
  
  try {
    
    const analyzeInfo = collectAnalyzeMemoInfo(memo);
    
    const res = await fetch('http://localhost:5002/api/memo-question', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: memo.type,
        question: question,
        memoContent: memo.content || '',
        memoTitle: memo.title || '',
        analyzeInfo: analyzeInfo
      })
    });
    const data = await res.json();
    if (data.result) {
      memoAIResponses.value[memo.id] = data.result;
      memoQuestion.value = ''; 
    } else {
      alert('AI analysis failed: ' + (data.error || 'Unknown error'));
    }
  } catch (e) {
    console.error(e);
    alert('AI request failed');
  } finally {
    aiLoading.value = false;
    loadingMemoId.value = null;
  }
};


const submitFirstOrderAI = async (memo: Memo) => {
  const code = firstOrderCodeInput.value.trim();
  if (!code) {
    alert('Please enter a code name');
    return;
  }

  
  const passageData: { passage: string; explanation: string; sentence?: string }[] = [];
  if (passageDatabase.value) {
    Object.entries(passageDatabase.value).forEach(([passageName, p]: [string, any]) => {
      p.firstOrderCodes.forEach((foc: string, idx: number) => {
        if (foc.toLowerCase() === code.toLowerCase()) {
          passageData.push({
            passage: passageName,
            explanation: p.explanations[idx] || '',
            sentence: p.sentences ? p.sentences[idx] : '' 
          });
        }
      });
    });
  }

  if (passageData.length === 0) {
    alert(`Code "${code}" not found in any passage.`);
    return;
  }

  
  memo.title = code;
  
  await callMemoAI(memo, {
    code,
    passageCount: passageData.length,
    passages: passageData
  });
};


const submitSecondOrderAI = async (memo: Memo) => {
  const soc = secondOrderCodeInput.value.trim();
  if (!soc) {
    alert('Please enter a Second-Order Code name');
    return;
  }

  
  const firstOrderCodes: { code: string; explanation: string; passage: string }[] = [];
  if (passageDatabase.value) {
    Object.entries(passageDatabase.value).forEach(([passageName, p]: [string, any]) => {
      p.firstOrderCodes.forEach((foc: string, idx: number) => {
        if ((p.secondOrderCodes[idx] || '').toLowerCase() === soc.toLowerCase()) {
          firstOrderCodes.push({
            code: foc,
            explanation: p.explanations[idx] || '',
            passage: passageName
          });
        }
      });
    });
  }

  if (firstOrderCodes.length === 0) {
    alert(`Second-Order Code "${soc}" not found or has no First-Order Codes.`);
    return;
  }

  
  memo.title = soc;

  await callMemoAI(memo, {
    secondOrderCode: soc,
    firstOrderCodes
  });
};


const submitTheoryAI = async (memo: Memo) => {
  const validCodes = theoryCodes.value.filter(c => c.name.trim());
  if (validCodes.length < 2) {
    alert('Please enter at least 2 codes to analyze relationships');
    return;
  }

  
  const codesData = validCodes.map(c => {
    const explanations: string[] = [];
    const passages: string[] = [];
    
    if (passageDatabase.value) {
      Object.entries(passageDatabase.value).forEach(([passageName, p]: [string, any]) => {
        if (c.type === 'First-Order') {
          p.firstOrderCodes.forEach((foc: string, idx: number) => {
            if (foc.toLowerCase() === c.name.toLowerCase()) {
              explanations.push(p.explanations[idx] || '');
              if (!passages.includes(passageName)) passages.push(passageName);
            }
          });
        } else {
          p.secondOrderCodes.forEach((soc: string, idx: number) => {
            if ((soc || '').toLowerCase() === c.name.toLowerCase()) {
              explanations.push(p.explanations[idx] || '');
              if (!passages.includes(passageName)) passages.push(passageName);
            }
          });
        }
      });
    }
    
    return {
      name: c.name,
      type: c.type,
      explanations,
      passageCount: passages.length
    };
  });

  await callMemoAI(memo, { codes: codesData });
};


const submitTheoryTrace = (memo: Memo) => {
  const validCodes = theoryCodes.value.filter(c => c.name.trim());
  if (validCodes.length === 0) {
    alert('Please enter at least one code to search');
    return;
  }

  const results: any[] = [];

  if (passageDatabase.value) {
    Object.entries(passageDatabase.value).forEach(([passageName, p]: [string, any]) => {
      
      const hasAllCodes = validCodes.every(c => {
        if (c.type === 'First-Order') {
          return p.firstOrderCodes.some((foc: string) => foc.toLowerCase() === c.name.trim().toLowerCase());
        } else {
          return p.secondOrderCodes.some((soc: string) => (soc || '').toLowerCase() === c.name.trim().toLowerCase());
        }
      });

      if (hasAllCodes) {
        
        const passageResult = {
          passageName: passageName,
          focs: [] as any[],
          socs: [] as any[]
        };

        
        validCodes.filter(c => c.type === 'First-Order').forEach(c => {
             p.firstOrderCodes.forEach((foc: string, idx: number) => {
                 if (foc.toLowerCase() === c.name.trim().toLowerCase()) {
                     passageResult.focs.push({
                         code: foc,
                         explanation: p.explanations[idx] || '',
                         sentence: p.sentences ? p.sentences[idx] : ''
                     });
                 }
             });
        });

        
        validCodes.filter(c => c.type === 'Second-Order').forEach(c => {
            const socData = {
                code: c.name,
                children: [] as any[]
            };
            
            p.secondOrderCodes.forEach((soc: string, idx: number) => {
                 if ((soc || '').toLowerCase() === c.name.trim().toLowerCase()) {
                     socData.children.push({
                         code: p.firstOrderCodes[idx], 
                         explanation: p.explanations[idx] || '',
                         sentence: p.sentences ? p.sentences[idx] : ''
                     });
                 }
            });
            passageResult.socs.push(socData);
        });

        results.push(passageResult);
      }
    });
  }

  memo.traceData = results;
  activeAIFormId.value = null; 
  activeTraceId.value = memo.id; 
};


const submitAnalyticalAI = async (memo: Memo) => {
  const question = analyticalQuestion.value.trim();
  if (!question) {
    alert('Please enter a question');
    return;
  }

  await callMemoAI(memo, { question });
};


const callMemoAI = async (memo: Memo, context: any) => {
  aiLoading.value = true;
  loadingMemoId.value = memo.id;
  
  try {
    const res = await fetch('http://localhost:5002/api/memo-ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: memo.type, context })
    });
    const data = await res.json();
    if (data.result) {
      memo.content = data.result;
      saveMemos();
      activeAIFormId.value = null; 
    } else {
      alert('AI analysis failed: ' + (data.error || 'Unknown error'));
    }
  } catch (e) {
    console.error(e);
    alert('AI request failed');
  } finally {
    aiLoading.value = false;
    loadingMemoId.value = null;
  }
};


const searchTheoreticalLink = (title: string): any[] => {
  if (!title || !passageDatabase.value) return [];
  
  const parts = title.split(/\s*[—\-]\s*/);
  if (parts.length < 2) return [];
  const code1 = parts[0].trim().toLowerCase();
  const code2 = parts[1].trim().toLowerCase();
  if (!code1 || !code2) return [];

  const results: any[] = [];
  Object.entries(passageDatabase.value).forEach(([passageName, p]: [string, any]) => {
    const focs = p.firstOrderCodes || [];
    
    const idx1 = focs.findIndex((f: string) => f.toLowerCase() === code1);
    const idx2 = focs.findIndex((f: string) => f.toLowerCase() === code2);
    if (idx1 !== -1 && idx2 !== -1) {
      results.push({
        passageName,
        code1Data: {
          code: focs[idx1],
          explanation: (p.explanations || [])[idx1] || '',
          sentence: (p.sentences || [])[idx1] || '',
          stage: (p.stages || [])[idx1] || ''
        },
        code2Data: {
          code: focs[idx2],
          explanation: (p.explanations || [])[idx2] || '',
          sentence: (p.sentences || [])[idx2] || '',
          stage: (p.stages || [])[idx2] || ''
        }
      });
    }
  });
  return results;
};

const analyzeMemo = (memo: Memo) => {
  if (memo.type === 'Theoretical Memos') {
    if (!memo.title) {
      toggleAIForm(memo, 'ai');
      return;
    }
    
    if (activeTraceId.value === memo.id) {
      activeTraceId.value = null;
      return;
    }
    activeAIFormId.value = null;
    memo.traceData = searchTheoreticalLink(memo.title);
    activeTraceId.value = memo.id;
    return;
  }

  if (!memo.title) {
    toggleAIForm(memo, 'ai');
    return;
  }

  
  if (activeTraceId.value === memo.id) {
    activeTraceId.value = null;
    return;
  }

  activeAIFormId.value = null; 

  if (memo.type === 'First-Order Code Notes') {
    const traceData: any[] = [];
    const code = memo.title.trim().toLowerCase();
    
    if (passageDatabase.value) {
      Object.entries(passageDatabase.value).forEach(([passageName, p]: [string, any]) => {
        p.firstOrderCodes.forEach((foc: string, idx: number) => {
          if (foc.toLowerCase() === code) {
            traceData.push({
              passage: passageName,
              explanation: p.explanations[idx] || '',
              sentence: p.sentences ? p.sentences[idx] : ''
            });
          }
        });
      });
    }
    memo.traceData = traceData;
    activeTraceId.value = memo.id;
  } else if (memo.type === 'Second-Order Code Notes') {
    const traceData: any[] = [];
    const soc = memo.title.trim().toLowerCase();

    if (passageDatabase.value) {
      Object.entries(passageDatabase.value).forEach(([passageName, p]: [string, any]) => {
        p.firstOrderCodes.forEach((foc: string, idx: number) => {
          const currentSoc = (p.secondOrderCodes[idx] || '').toLowerCase();
          if (currentSoc === soc) {
            traceData.push({
              code: foc,
              passage: passageName,
              explanation: p.explanations[idx] || ''
            });
          }
        });
      });
    }
    memo.traceData = traceData;
    activeTraceId.value = memo.id;
  } else {
    
    toggleAIForm(memo, 'ai');
  }
};

const groupByPassage = (data: any[]) => {
  const groups: Record<string, any[]> = {};
  data.forEach(item => {
    if (!groups[item.passage]) groups[item.passage] = [];
    groups[item.passage].push(item);
  });
  return groups;
};

const handleTraceJump = (passageName: string, code: string) => {
  emit('jump-to-code', { passageName, code });
};

const handleEditCode = (passageName: string, code: string) => {
  emit('edit-code', { passageName, code });
};


const handleShowUmap = (memo: Memo) => {
  if (!memo.title || !memo.title.trim()) {
    alert('Please set a title for this memo first');
    return;
  }
  const soc = memo.title.trim().toLowerCase();
  const codes = new Set<string>();

  if (passageDatabase.value) {
    Object.entries(passageDatabase.value).forEach(([, p]: [string, any]) => {
      p.firstOrderCodes.forEach((foc: string, idx: number) => {
        const currentSoc = (p.secondOrderCodes[idx] || '').toLowerCase();
        if (currentSoc === soc) {
          codes.add(foc);
        }
      });
    });
  }

  if (codes.size === 0) {
    alert(`No first-order codes found for "${memo.title}"`);
    return;
  }

  emit('show-umap', {
    secondCodeName: memo.title,
    firstOrderCodes: Array.from(codes)
  });
};

const deleteFirstOrderCode = (passageName: string, code: string, memo: Memo) => {
  if (!passageDatabase.value || !passageDatabase.value[passageName]) return;
  const p = passageDatabase.value[passageName];
  
  const indices: number[] = [];
  p.firstOrderCodes.forEach((foc: string, idx: number) => {
    if (foc === code) indices.push(idx);
  });
  if (indices.length === 0) return;
  
  for (let i = indices.length - 1; i >= 0; i--) {
    const idx = indices[i];
    p.firstOrderCodes.splice(idx, 1);
    if (p.explanations) p.explanations.splice(idx, 1);
    if (p.secondOrderCodes) p.secondOrderCodes.splice(idx, 1);
    if (p.sentences) p.sentences.splice(idx, 1);
  }
  
  if (memo.traceData) {
    if (memo.type === 'Second-Order Code Notes') {
      
      memo.traceData = memo.traceData.filter((item: any) =>
        !(item.code === code && item.passage === passageName)
      );
    } else if (memo.type === 'Theoretical Memos') {
      
      memo.traceData = memo.traceData.filter((result: any) =>
        !(result.passageName === passageName &&
          (result.code1Data.code === code || result.code2Data.code === code))
      );
    } else if (memo.type === 'First-Order Code Notes') {
      
      memo.traceData = memo.traceData.filter((item: any) =>
        item.passage !== passageName
      );
    }
  }
  saveMemos();
};

const exportMarkdown = () => {
  let md = '# Memos\n\n';
  props.memos.forEach(m => {
    md += `## ${m.title}\n`;
    md += `**Type:** ${m.type}\n\n`;
    md += `${m.content}\n\n---\n\n`;
  });
  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'memos.md';
  a.click();
  URL.revokeObjectURL(url);
};
</script>

<style scoped>
.memo-panel {
  width: 100%;
  height: 100%;
  background: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.memo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #407434;
  color: #fff;
}
.header-title {
  margin: 0;
  font-size: 18px;
}
.header-left, .header-right {
  display: flex;
  gap: 8px;
  align-items: center;
  position: relative;
}
.memo-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}
.memo-btn:hover, .memo-btn.active {
  background: rgba(255,255,255,0.2);
}
.close-btn {
  font-weight: bold;
}
.add-menu {
  position: absolute;
  top: 36px;
  right: 0;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 10;
}
.add-menu button {
  display: block;
  width: 100%;
  padding: 8px 12px;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  white-space: nowrap;
  color: #333;
}
.add-menu button:hover {
  background: #f0f0f0;
}
.memo-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
.memo-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  border-left: 4px solid #ccc;
}
.memo-card.type-first { background: #e8f5e9; border-color: #4caf50; }
.memo-card.type-second { background: #e3f2fd; border-color: #2196f3; }
.memo-card.type-theory { background: #fff3e0; border-color: #ff9800; }
.memo-card.type-analytical { background: #fce4ec; border-color: #e91e63; }

.memo-card-header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
  flex-wrap: nowrap;
}
.memo-title-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  font-weight: bold;
  font-size: 14px;
}
.memo-type-badge {
  font-size: 10px;
  background: rgba(0,0,0,0.1);
  padding: 2px 6px;
  border-radius: 4px;
}
.ai-btn, .delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  color: #666;
  flex-shrink: 0;
}
.ai-btn:hover, .ai-btn.active { color: #407434; }
.umap-btn { color: #2e7d32; }
.umap-btn:hover { color: #1b5e20; background: rgba(76, 175, 80, 0.12); border-radius: 4px; }
.delete-btn:hover { color: #c00; }


.ai-form {
  background: rgba(255,255,255,0.9);
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}
.ai-form-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}
.ai-form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 8px;
}
.ai-form-input:focus {
  border-color: #407434;
  outline: none;
}
.ai-form-select {
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 13px;
  flex: 1;
}
.ai-form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}
.ai-form-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.ai-submit-btn {
  flex: 1;
  padding: 8px 16px;
  background: #407434;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.ai-submit-btn:hover {
  background: #305828;
}
.ai-cancel-btn {
  padding: 8px 16px;
  background: #f0f0f0;
  color: #666;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.ai-cancel-btn:hover {
  background: #e0e0e0;
}
.theory-code-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}
.theory-remove-btn {
  background: #ff5252;
  color: #fff;
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 14px;
}
.add-code-btn {
  background: none;
  border: 1px dashed #999;
  color: #666;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-bottom: 8px;
}
.add-code-btn:hover {
  border-color: #407434;
  color: #407434;
}
.ai-form-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  color: #666;
  font-size: 13px;
}
.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid #ccc;
  border-top-color: #407434;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}


.ai-response-panel {
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
  border: 1px solid #a5d6a7;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.15);
  text-align: left;
}
.ai-response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #c8e6c9;
}
.ai-response-title {
  font-weight: bold;
  color: #2e7d32;
  font-size: 14px;
}
.clear-response-btn {
  background: none;
  border: 1px solid #81c784;
  color: #388e3c;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}
.clear-response-btn:hover {
  background: #c8e6c9;
  border-color: #66bb6a;
}
.ai-response-content {
  font-size: 13px;
  line-height: 1.6;
  color: #333;
  max-height: 300px;
  overflow-y: auto;
  text-align: left;
}

.memo-content {
  width: 100%;
  min-height: 80px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  resize: vertical;
  font-family: inherit;
}
.memo-content::-webkit-scrollbar { width: 6px; height: 6px; }
.memo-content::-webkit-scrollbar-track { background: transparent; }
.memo-content::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 3px; }

.empty-hint {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

@keyframes spin { to { transform: rotate(360deg); } }


.memo-panel-slide-enter-active, .memo-panel-slide-leave-active {
  transition: transform 0.3s ease;
}
.memo-panel-slide-enter-from, .memo-panel-slide-leave-to {
  transform: translateX(100%);
}

.trace-results {
  background: #f1f8e9;
  border: 1px solid #c5e1a5;
  border-radius: 6px;
  padding: 10px;
  margin-top: 8px;
  text-align: left;
}
.trace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dcedc8;
  padding-bottom: 6px;
  margin-bottom: 8px;
}
.trace-title {
  font-weight: bold;
  color: #33691e;
  font-size: 14px;
}
.close-trace-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 16px;
}
.trace-item {
  margin-bottom: 8px;
  padding: 8px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  text-align: left;
}
.trace-source {
  font-size: 12px;
  font-weight: bold;
  color: #1565c0;
  cursor: pointer;
  margin-bottom: 4px;
}
.trace-source:hover {
  text-decoration: underline;
}
.trace-sentence {
  font-size: 13px;
  color: #333;
  margin-bottom: 4px;
  font-style: italic;
}
.trace-explanation {
  font-size: 12px;
  color: #666;
}
.no-trace {
  color: #999;
  font-style: italic;
  font-size: 13px;
  text-align: center;
}
.trace-group {
  margin-bottom: 12px;
}
.trace-source-header {
  font-size: 13px;
  font-weight: bold;
  color: #424242;
  margin-bottom: 6px;
  border-bottom: 1px dashed #ccc;
  padding-bottom: 2px;
  text-align: left;
}
.trace-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.trace-chip {
  background: #e3f2fd;
  color: #0277bd;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  cursor: pointer;
  border: 1px solid #b3e5fc;
  transition: all 0.2s;
}
.trace-chip:hover {
  background: #bbdefb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.chip-delete {
  color: #c00;
  font-weight: bold;
  margin-left: 4px;
  cursor: pointer;
  font-size: 13px;
  line-height: 1;
  display: none;
}
.chip-delete:hover {
  color: #f00;
}
.trace-chip:hover .chip-delete,
.trace-code-tag:hover .chip-delete,
.trace-source:hover .chip-delete {
  display: inline;
}

.chip-edit {
  display: none;
  cursor: pointer;
  margin-right: 3px;
  margin-left: 0;
  vertical-align: middle;
  opacity: 0.7;
  transition: opacity 0.15s;
}
.chip-edit:hover {
  opacity: 1;
}
.trace-chip:hover .chip-edit,
.trace-code-tag:hover .chip-edit,
.trace-source:hover .chip-edit {
  display: inline-flex;
}

.trace-sub-group {
  margin-left: 8px;
  margin-bottom: 8px;
  border-left: 2px solid #e0e0e0;
  padding-left: 8px;
}
.trace-label {
  font-size: 13px;
  font-weight: bold;
  color: #555;
  margin-bottom: 4px;
}
.trace-items-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.trace-detail-item {
  background: #f9f9f9;
  padding: 6px;
  border-radius: 4px;
  border: 1px solid #eee;
}
.trace-code-tag {
  display: inline-block;
  background: #e8f5e9;
  color: #2e7d32;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
  margin-bottom: 4px;
}
.trace-code-tag:hover {
  text-decoration: underline;
}
.soc-block {
    margin-bottom: 8px;
}
.child-tag {
    background: #e3f2fd;
    color: #1565c0;
}
.trace-context {
    font-size: 12px;
}


.type-cluster {
  border-left-color: #fbc02d;
}
.cluster-results {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.cluster-details {
  border: 1px solid #eee;
  border-radius: 6px;
  background: #fff;
  overflow: hidden;
}
.cluster-summary {
  padding: 8px 12px;
  background: #fffde7;
  cursor: pointer;
  font-size: 13px;
  user-select: none;
  border-bottom: 1px solid transparent;
}
.cluster-details[open] .cluster-summary {
  border-bottom-color: #eee;
}
.cluster-item-list {
  padding: 8px 12px;
  background: #fafafa;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}
.cluster-item {
  padding-bottom: 8px;
  border-bottom: 1px dashed #eee;
}
.cluster-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}
.soc-badge {
  font-size: 11px;
  background: #e0e0e0;
  color: #555;
  padding: 0 4px;
  border-radius: 3px;
  margin-left: 6px;
}
.ai-chat-btn {
  color: #6366f1 !important;
  transition: all 0.15s;
}
.ai-chat-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  color: #4f46e5 !important;
}

.inline-chatbot-container {
  height: 640px;
  flex-shrink: 0;
  margin-bottom: 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
