<template>
  <div class="chatbot-dialog">
    
      <div class="chatbot-header">
        <div class="header-left">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24">
            <path fill="currentColor" d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A2.5 2.5 0 0 0 5 15.5 2.5 2.5 0 0 0 7.5 18a2.5 2.5 0 0 0 2.5-2.5A2.5 2.5 0 0 0 7.5 13m9 0a2.5 2.5 0 0 0-2.5 2.5 2.5 2.5 0 0 0 2.5 2.5 2.5 2.5 0 0 0 2.5-2.5 2.5 2.5 0 0 0-2.5-2.5z"/>
          </svg>
          <span class="header-title">AI Research Assistant</span>
        </div>
        <div class="header-right">
          <button @click="handleReset" class="header-btn" title="New Chat">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24">
              <path fill="currentColor" d="M17.65 6.35A7.96 7.96 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
            </svg>
          </button>
          <button @click="$emit('close')" class="header-btn close-btn" title="Close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
      </div>

      
      <div class="chatbot-messages" ref="messagesContainer">
        
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-icon"></div>
          <h3>Welcome to AI Research Assistant</h3>
          <p>I can help you analyze codes, explore relationships, and manage memos. Try asking:</p>
          <div class="suggestions">
            <button @click="handleSuggestion('What first-order codes do I have?')">List my codes</button>
            <button @click="handleSuggestion('Show me my memos')">Show memos</button>
            <button @click="handleSuggestion('Find codes similar to ')">Search similar</button>
          </div>
        </div>

        <div v-for="(msg, idx) in messages" :key="idx" :class="['message', `message-${msg.role}`]">
          
          <div v-if="msg.role === 'user'" class="msg-bubble user-bubble">
            <div class="msg-avatar">👤</div>
            <div class="msg-content">{{ msg.content }}</div>
          </div>

          
          <div v-else-if="msg.role === 'tool_call'" class="tool-call-card" :class="{ 'write-tool': msg.isWrite }">
            <div class="tool-call-header" @click="msg.expanded = !msg.expanded">
              <span class="tool-icon">{{ msg.isWrite ? '📝' : '🔍' }}</span>
              <span class="tool-name">{{ formatToolName(msg.toolName) }}</span>
              <span class="tool-args-preview">{{ formatToolArgsPreview(msg.toolArgs) }}</span>
              <span class="expand-icon">{{ msg.expanded ? '▾' : '▸' }}</span>
            </div>
            <div v-if="msg.expanded" class="tool-call-detail">
              <div class="tool-section">
                <div class="tool-section-label">Parameters:</div>
                <pre class="tool-json">{{ formatToolArgsDetail(msg.toolArgs) }}</pre>
              </div>
              <div class="tool-section">
                <div class="tool-section-label">Result:</div>
                <pre class="tool-json">{{ formatToolResult(msg.toolResult) }}</pre>
              </div>
            </div>
          </div>

          
          <div v-else-if="msg.role === 'proposal'" class="proposal-card" :class="msg.proposalStatus">
            <div class="proposal-header">
              <span class="proposal-icon">⚡</span>
              <span class="proposal-title">Proposed: {{ formatToolName(msg.toolName) }}</span>
              <span v-if="msg.proposalStatus === 'confirmed'" class="status-badge confirmed">✓ Executed</span>
              <span v-if="msg.proposalStatus === 'cancelled'" class="status-badge cancelled">✗ Cancelled</span>
            </div>
            <div class="proposal-body">
              <div v-for="(val, key) in msg.toolArgs" :key="key" class="proposal-field">
                <span class="field-label">{{ key }}:</span>
                <span class="field-value">{{ typeof val === 'object' ? JSON.stringify(val) : val }}</span>
              </div>
            </div>
            <div v-if="msg.proposalStatus === 'pending'" class="proposal-actions">
              <button @click="handleConfirm(msg, true)" class="confirm-btn">✓ Confirm</button>
              <button @click="handleConfirm(msg, false)" class="cancel-btn">✗ Cancel</button>
            </div>
          </div>

          
          <div v-else-if="msg.role === 'assistant'" class="msg-bubble assistant-bubble">
            <div class="msg-avatar">🤖</div>
            <div class="msg-content" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </div>

        
        <div v-if="loading" class="loading-indicator">
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
          <span class="loading-text">{{ statusText }}</span>
        </div>
      </div>

      
      <div v-if="attachments.length > 0" class="attachments-bar">
        <div v-for="(att, idx) in attachments" :key="idx" class="attachment-chip">
          <span class="att-icon">{{ att.type === 'file' ? '📄' : '📝' }}</span>
          <span class="att-name">{{ att.name }}</span>
          <button @click="attachments.splice(idx, 1)" class="att-remove">×</button>
        </div>
      </div>

      
      <div class="chatbot-input">
        <textarea
          class="custom-scrollbar"
          v-model="inputText"
          @keydown.enter.exact.prevent="handleSend"
          placeholder="Ask me about your codes, links, or analysis..."
          rows="3"
          ref="inputField"
        ></textarea>
        <div class="input-bottom-row">
          <div class="input-actions">
            <label class="action-btn" title="Upload PDF/TXT">
              <input type="file" accept=".pdf,.txt,.text" @change="handleFileUpload" hidden />
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                <path fill="currentColor" d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5a2.5 2.5 0 0 1 5 0v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5a2.5 2.5 0 0 0 5 0V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
              </svg>
            </label>
            <button @click="showMemoSelector = !showMemoSelector" class="action-btn" title="Attach Memo">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                <path fill="currentColor" d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
              </svg>
            </button>
            
            <div v-if="showMemoSelector" class="memo-selector-dropdown">
              <div v-for="m in memosList" :key="m.id" class="memo-selector-item" @click="attachMemo(m)">
                <span class="memo-type-dot" :class="memoTypeClass(m.type)"></span>
                <span class="memo-item-title">{{ m.title || 'Untitled' }}</span>
                <span class="memo-item-type">{{ (m.type || '').split(' ')[0] }}</span>
              </div>
              <div v-if="memosList.length === 0" class="memo-selector-empty">No memos available</div>
            </div>
          </div>
          
          <div class="iteration-control">
            <span class="iteration-label">Limit: {{ maxIterations }}</span>
            <input 
              type="range" 
              min="10" 
              max="50" 
              v-model.number="maxIterations" 
              class="iteration-slider"
              title="Max AI thinking steps"
            />
          </div>

          <button @click="handleSend" :disabled="loading || !inputText.trim()" class="send-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted, inject, computed } from 'vue';
import { useChatbot, type Attachment, type ChatMessage } from '~/composables/chatbot';
import type { Memo } from '~/composables/memo';

const props = defineProps<{
  memos: Memo[];
  passageDatabase: Record<string, any>;
  stageOrder?: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'memos-changed'): void;
  (e: 'passage-database-changed', pdb: Record<string, any>): void;
  (e: 'ai-memo-operation', op: any): void;
}>();

const {
  sessionId,
  messages,
  loading,
  statusText,
  error,
  startSession,
  sendMessage,
  confirmProposal,
  uploadFile,
  resetChat
} = useChatbot();

const inputText = ref('');
const attachments = ref<Attachment[]>([]);
const showMemoSelector = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);
const inputField = ref<HTMLTextAreaElement | null>(null);
const maxIterations = ref(20);


const memosList = computed(() => props.memos || []);


onMounted(async () => {
  if (!sessionId.value) {
    await startSession(props.passageDatabase, props.stageOrder || []);
  }
});


watch(() => messages.value.length, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
});

const handleSend = async () => {
  const text = inputText.value.trim();
  if (!text || loading.value) return;

  inputText.value = '';
  showMemoSelector.value = false;
  await sendMessage(text, [...attachments.value], props.passageDatabase, props.stageOrder || [], maxIterations.value);
  attachments.value = [];
};

const handleSuggestion = (text: string) => {
  inputText.value = text;
  inputField.value?.focus();
};

const handleReset = async () => {
  resetChat();
  await startSession(props.passageDatabase, props.stageOrder || []);
};

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const att = await uploadFile(file);
  if (att) {
    attachments.value.push(att);
  }
  target.value = '';  
};

const attachMemo = (memo: Memo) => {
  attachments.value.push({
    type: 'memo',
    name: `[${memo.type}] ${memo.title || 'Untitled'}`,
    content: `Type: ${memo.type}\nTitle: ${memo.title}\nContent:\n${memo.content || '(empty)'}`
  });
  showMemoSelector.value = false;
};

const handleConfirm = async (msg: ChatMessage, confirmed: boolean) => {
  const result = await confirmProposal(msg, confirmed, maxIterations.value);
  if (confirmed && result) {
    
    if (['create_memo', 'update_memo', 'delete_memo'].includes(msg.toolName || '')) {
      emit('ai-memo-operation', { toolName: msg.toolName, args: msg.toolArgs, result });
      emit('memos-changed');
    }
    
    if (result.passage_database_modified && result.passage_database) {
      emit('passage-database-changed', result.passage_database);
    }
  }
};



const formatToolName = (name?: string): string => {
  if (!name) return '';
  return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const formatToolArgsPreview = (args?: Record<string, any>): string => {
  if (!args) return '';
  const vals = Object.entries(args).map(([k,v]) => `${k}: ${v}`);
  if (vals.length === 0) return '';
  const first = vals.join(', ');
  return first.length > 40 ? first.slice(0, 40) + '...' : first;
};

const compactJson = (obj: any): string => {
  if (Array.isArray(obj)) {
    return obj.map(o => compactJson(o)).join('\n');
  } else if (obj !== null && typeof obj === 'object') {
    return '{ ' + Object.entries(obj).map(([k, v]) => `"${k}": ${JSON.stringify(v)}`).join(', ') + ' }';
  }
  return JSON.stringify(obj);
};

const formatToolArgsDetail = (args: any) => {
    return compactJson(args);
};

const formatToolResult = (result?: string): string => {
  if (!result) return '';
  try {
    const obj = JSON.parse(result);
    if (Array.isArray(obj)) {
        return obj.map((item: any) => compactJson(item)).join('\n');
    }
    return compactJson(obj);
  } catch {
    return result;
  }
};

const renderMarkdown = (text: string): string => {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/### (.*)/g, '<h4>$1</h4>')
    .replace(/## (.*)/g, '<h3>$1</h3>')
    .replace(/# (.*)/g, '<h2>$1</h2>')
    .replace(/\n- /g, '\n• ')
    .replace(/\n\d+\. /g, (m) => '\n' + m.trim() + ' ')
    .replace(/\n/g, '<br>');
};

const memoTypeClass = (type: string) => ({
  'dot-first': type.includes('First'),
  'dot-second': type.includes('Second'),
  'dot-theory': type.includes('Theoretical'),
  'dot-analytical': type.includes('Analytical'),
  'dot-cluster': type.includes('Cluster')
});
</script>

<style scoped>
.chatbot-dialog {
  width: 100%;
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  color: #333;
  text-align: left;
}


.chatbot-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: #f8fafc;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1e293b;
}
.header-title {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.3px;
}
.header-right { display: flex; gap: 6px; }
.header-btn {
  background: rgba(0,0,0,0.05);
  border: none;
  color: #64748b;
  padding: 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.header-btn:hover { background: rgba(0,0,0,0.1); color: #0f172a; }
.close-btn:hover { background: rgba(220, 38, 38, 0.1); color: #dc2626; }


.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.chatbot-messages::-webkit-scrollbar,
.custom-scrollbar::-webkit-scrollbar,
.tool-json::-webkit-scrollbar { width: 6px; height: 6px; }

.chatbot-messages::-webkit-scrollbar-track,
.custom-scrollbar::-webkit-scrollbar-track,
.tool-json::-webkit-scrollbar-track { background: transparent; }

.chatbot-messages::-webkit-scrollbar-thumb,
.custom-scrollbar::-webkit-scrollbar-thumb,
.tool-json::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 3px; }


.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #64748b;
}
.welcome-icon { font-size: 48px; margin-bottom: 12px; }
.welcome-message h3 { color: #1e293b; margin-bottom: 8px; font-size: 18px; }
.welcome-message p { margin-bottom: 16px; font-size: 13px; }
.suggestions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.suggestions button {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 8px 14px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
}
.suggestions button:hover {
  background: rgba(100, 140, 255, 0.15);
  border-color: rgba(100, 140, 255, 0.3);
  color: #ccf;
}


.msg-bubble {
  display: flex;
  gap: 12px;
  width: 100%;
}
.user-bubble { 
  align-self: flex-end; 
  flex-direction: row-reverse;
}
.assistant-bubble { 
  align-self: flex-start;
}
.msg-avatar { font-size: 20px; flex-shrink: 0; margin-top: 2px; }
.msg-content {
  flex-grow: 0;
  max-width: calc(100% - 32px);
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13.5px;
  line-height: 1.6;
  word-wrap: break-word;
  text-align: left;
}
.user-bubble .msg-content {
  background: linear-gradient(135deg, #4a6cf7, #6366f1);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.assistant-bubble .msg-content {
  background: #f1f5f9;
  color: #334155;
  border-bottom-left-radius: 4px;
  border: 1px solid #e2e8f0;
}
.assistant-bubble .msg-content :deep(code) {
  background: #e2e8f0;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 12px;
  color: #0f172a;
}
.assistant-bubble .msg-content :deep(h2),
.assistant-bubble .msg-content :deep(h3),
.assistant-bubble .msg-content :deep(h4) {
  margin: 8px 0 4px;
  color: #1e293b;
}
.assistant-bubble .msg-content :deep(strong) { color: #0f172a; }


.tool-call-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  font-size: 12.5px;
  align-self: stretch;
}
.tool-call-card.write-tool {
  border-color: #fde68a;
  background: #fffbeb;
}
.tool-call-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.15s;
}
.tool-call-header:hover { background: rgba(0,0,0,0.02); }
.tool-icon { font-size: 14px; }
.tool-name { font-weight: 600; color: #2563eb; }
.write-tool .tool-name { color: #d97706; }
.tool-args-preview { color: #64748b; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.expand-icon { color: #94a3b8; font-size: 11px; }
.tool-call-detail { padding: 0 12px 10px; border-top: 1px solid #f1f5f9; }
.tool-section { margin-top: 8px; }
.tool-section-label { color: #777; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.tool-json {
  background: #f1f5f9;
  padding: 8px 10px;
  border-radius: 6px;
  color: #334155;
  font-size: 11.5px;
  line-height: 1.5;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
  border: 1px solid #e2e8f0;
  text-align: left;
}


.proposal-card {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  overflow: hidden;
  font-size: 13px;
  align-self: stretch;
}
.proposal-card.cancelled {
  border-color: #fecaca;
  background: #fef2f2;
}
.proposal-card.confirmed {
  border-color: #bbf7d0;
  background: #f0fdf4;
}
.proposal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid #ecfdf5;
}
.proposal-icon { font-size: 16px; }
.proposal-title { font-weight: 600; color: #166534; flex: 1; }
.cancelled .proposal-title { color: #991b1b; }
.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}
.status-badge.confirmed { background: #dcfce7; color: #166534; }
.status-badge.cancelled { background: #fee2e2; color: #991b1b; }
.proposal-body { padding: 10px 14px; }
.proposal-field { display: flex; gap: 8px; margin-bottom: 4px; align-items: flex-start; }
.field-label { color: #64748b; min-width: 80px; word-break: break-all; }
.field-value { color: #1e293b; word-break: break-all; flex: 1; }
.proposal-actions {
  display: flex;
  gap: 8px;
  padding: 10px 14px;
  border-top: 1px solid #ecfdf5;
}
.confirm-btn, .cancel-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.15s;
}
.confirm-btn {
  background: rgba(80, 200, 120, 0.2);
  color: #7dd87d;
  border: 1px solid rgba(80, 200, 120, 0.3);
}
.confirm-btn:hover { background: rgba(80, 200, 120, 0.35); }
.cancel-btn {
  background: rgba(200, 80, 80, 0.15);
  color: #d87d7d;
  border: 1px solid rgba(200, 80, 80, 0.2);
}
.cancel-btn:hover { background: rgba(200, 80, 80, 0.3); }


.loading-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  color: #8888aa;
  font-size: 13px;
}
.typing-dots { display: flex; gap: 4px; }
.typing-dots span {
  width: 6px; height: 6px;
  background: #6366f1;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}


.attachments-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 14px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
}
.attachment-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 16px;
  padding: 3px 10px;
  font-size: 12px;
  color: #3b82f6;
}
.att-icon { font-size: 13px; }
.att-name { max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.att-remove {
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 14px;
  padding: 0 2px;
  line-height: 1;
}
.att-remove:hover { color: #ff6b6b; }


.chatbot-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 14px;
  border-top: 1px solid #f1f5f9;
  background: #fbfcfd;
  position: relative;
}
.input-bottom-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.input-actions {
  display: flex;
  gap: 4px;
  position: relative;
}
.action-btn {
  background: #f1f5f9;
  border: none;
  color: #64748b;
  padding: 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.action-btn:hover { background: #e2e8f0; color: #1e293b; }
.iteration-control {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f1f5f9;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  margin: 0 10px;
}
.iteration-label {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  white-space: nowrap;
}
.iteration-slider {
  flex: 1;
  height: 4px;
  cursor: pointer;
  accent-color: #4a6cf7;
  min-width: 40px;
}

.chatbot-input textarea {
  flex: 1;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px 14px;
  color: #1e293b;
  font-size: 13.5px;
  resize: none;
  outline: none;
  font-family: inherit;
  line-height: 1.5;
  min-height: 20px;
  max-height: 120px;
  transition: all 0.15s;
}
.chatbot-input textarea:focus {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.1);
}
.chatbot-input textarea::placeholder { color: #555; }

.send-btn {
  background: linear-gradient(135deg, #4a6cf7, #6366f1);
  border: none;
  color: #fff;
  padding: 6px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.send-btn:hover { transform: scale(1.05); box-shadow: 0 2px 12px rgba(99, 102, 241, 0.4); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none; }


.memo-selector-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  width: 280px;
  max-height: 240px;
  overflow-y: auto;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  margin-bottom: 6px;
  z-index: 10;
}
.memo-selector-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 12.5px;
  transition: background 0.1s;
}
.memo-selector-item:hover { background: #f1f5f9; }
.memo-type-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-first { background: #64b5f6; }
.dot-second { background: #81c784; }
.dot-theory { background: #ffb74d; }
.dot-analytical { background: #e57373; }
.dot-cluster { background: #ba68c8; }
.memo-item-title { flex: 1; color: #1e293b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.memo-item-type { color: #666; font-size: 11px; }
.memo-selector-empty { padding: 16px; text-align: center; color: #555; font-size: 12px; }
</style>
