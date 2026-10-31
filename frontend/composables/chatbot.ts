import { ref, reactive } from 'vue';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'tool_call' | 'proposal';
  content: string;
  
  toolName?: string;
  toolArgs?: Record<string, any>;
  toolResult?: string;
  isWrite?: boolean;
  expanded?: boolean;
  
  proposalId?: string;
  proposalStatus?: 'pending' | 'confirmed' | 'cancelled';
}

export interface Attachment {
  type: 'file' | 'memo';
  name: string;
  content: string;
}

export interface Proposal {
  tool_call_id: string;
  tool_name: string;
  arguments: Record<string, any>;
}

const AI_CHAT_API = 'http://localhost:5005';

export const useChatbot = () => {
  const sessionId = ref<string | null>(null);
  const messages = ref<ChatMessage[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const statusText = ref('AI is thinking...');

  
  const startSession = async (passageDatabase: Record<string, any>, stageOrder: string[] = []) => {
    try {
      const res = await fetch(`${AI_CHAT_API}/api/chat/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ passageDatabase, stageOrder })
      });
      const data = await res.json();
      sessionId.value = data.session_id;
      messages.value = [];
      error.value = null;
      return data.session_id;
    } catch (e: any) {
      error.value = `Failed to start session: ${e.message}`;
      return null;
    }
  };

  
  const sendMessage = async (text: string, attachments: Attachment[] = [], passageDatabase?: Record<string, any>, stageOrder?: string[], maxIterations: number = 20) => {
    if (!sessionId.value) {
      error.value = 'No active session';
      return;
    }

    
    messages.value.push({
      role: 'user',
      content: text
    });

    loading.value = true;
    error.value = null;

    try {
      const res = await fetch(`${AI_CHAT_API}/api/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId.value,
          message: text,
          attachments: attachments.map(a => ({
            type: a.type,
            name: a.name,
            content: a.content
          })),
          passageDatabase,
          stageOrder,
          max_iterations: maxIterations
        })
      });

      const data = await res.json();

      if (data.error) {
        error.value = data.error;
        loading.value = false;
        return;
      }

      
      if (data.tool_calls) {
        for (const tc of data.tool_calls) {
          messages.value.push({
            role: 'tool_call',
            content: '',
            toolName: tc.name,
            toolArgs: tc.arguments,
            toolResult: tc.result,
            isWrite: tc.is_write,
            expanded: false
          });
        }
      }

      
      if (data.response) {
        messages.value.push({
          role: 'assistant',
          content: data.response
        });
      }

      
      if (data.proposals) {
        for (const p of data.proposals) {
          messages.value.push({
            role: 'proposal',
            content: '',
            toolName: p.tool_name,
            toolArgs: p.arguments,
            proposalId: p.tool_call_id,
            proposalStatus: 'pending'
          });
        }
      }
    } catch (e: any) {
      error.value = `Request failed: ${e.message}`;
    } finally {
      loading.value = false;
    }
  };

  
  const confirmProposal = async (msg: ChatMessage, confirmed: boolean, maxIterations: number = 20) => {
    if (!sessionId.value || !msg.proposalId) return;

    msg.proposalStatus = confirmed ? 'confirmed' : 'cancelled';
    statusText.value = 'AI is implementing...';
    loading.value = true;
    try {
      const res = await fetch(`${AI_CHAT_API}/api/chat/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId.value,
          tool_call_id: msg.proposalId,
          tool_name: msg.toolName,
          arguments: msg.toolArgs,
          confirmed,
          max_iterations: maxIterations
        })
      });

      const data = await res.json();
      
      
      if (data.tool_calls) {
        for (const tc of data.tool_calls) {
          messages.value.push({
            role: 'tool_call',
            content: '',
            toolName: tc.name,
            toolArgs: tc.arguments,
            toolResult: tc.result,
            isWrite: tc.is_write,
            expanded: false
          });
        }
      }

      
      if (data.response) {
        messages.value.push({
          role: 'assistant',
          content: data.response
        });
      }

      
      if (data.proposals) {
        for (const p of data.proposals) {
          messages.value.push({
            role: 'proposal',
            content: '',
            toolName: p.tool_name,
            toolArgs: p.arguments,
            proposalId: p.tool_call_id,
            proposalStatus: 'pending'
          });
        }
      }

      return data;
    } catch (e: any) {
      error.value = `Confirm failed: ${e.message}`;
    } finally {
      loading.value = false;
      statusText.value = 'AI is thinking...';
    }
  };

  
  const uploadFile = async (file: File): Promise<Attachment | null> => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${AI_CHAT_API}/api/chat/upload`, {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (data.error) {
        error.value = data.error;
        return null;
      }

      return {
        type: 'file',
        name: data.filename,
        content: data.text
      };
    } catch (e: any) {
      error.value = `Upload failed: ${e.message}`;
      return null;
    }
  };

  
  const resetChat = () => {
    sessionId.value = null;
    messages.value = [];
    error.value = null;
    loading.value = false;
  };

  return {
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
  };
};
