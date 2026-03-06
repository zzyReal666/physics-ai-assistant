import { useEffect, useState } from 'react';
import { askQuestion } from '../services/api/chat';
import type { ChatAnswer } from '../types';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  answer?: ChatAnswer;
  status?: 'loading' | 'done' | 'error';
}

interface ChatSessionState {
  messages: ChatMessage[];
  level: 'junior' | 'senior';
  pendingCount: number;
}

const STORAGE_KEY = 'physics-ai-chat-session-v1';
const listeners = new Set<() => void>();

let state: ChatSessionState = {
  messages: [],
  level: 'senior',
  pendingCount: 0
};

function loadFromStorage() {
  if (typeof window === 'undefined') {
    return;
  }
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return;
  }
  try {
    const parsed = JSON.parse(raw) as Partial<ChatSessionState>;
    state = {
      messages: Array.isArray(parsed.messages) ? parsed.messages : [],
      level: parsed.level === 'junior' ? 'junior' : 'senior',
      pendingCount: 0
    };
  } catch {
    state = { messages: [], level: 'senior', pendingCount: 0 };
  }
}

function persistToStorage() {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ messages: state.messages, level: state.level })
  );
}

function emit() {
  persistToStorage();
  listeners.forEach((l) => l());
}

function setState(next: Partial<ChatSessionState>) {
  state = { ...state, ...next };
  emit();
}

function newId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function updateMessage(id: string, patch: Partial<ChatMessage>) {
  state = {
    ...state,
    messages: state.messages.map((m) => (m.id === id ? { ...m, ...patch } : m))
  };
  emit();
}

loadFromStorage();

export function getChatSessionState() {
  return state;
}

export function subscribeChatSession(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function setChatStudentLevel(level: 'junior' | 'senior') {
  setState({ level });
}

export function clearChatSession() {
  setState({ messages: [] });
}

export async function sendChatQuestion(question: string) {
  const text = question.trim();
  if (!text) {
    return;
  }

  const userId = newId('user');
  const assistantId = newId('assistant');

  state = {
    ...state,
    pendingCount: state.pendingCount + 1,
    messages: [
      ...state.messages,
      { id: userId, role: 'user', content: text, status: 'done' },
      {
        id: assistantId,
        role: 'assistant',
        content: '正在思考并生成答案...（你可以切换页面，回答会继续）',
        status: 'loading'
      }
    ]
  };
  emit();

  try {
    const answer = await askQuestion(text, state.level);
    updateMessage(assistantId, {
      content: answer.content,
      answer,
      status: 'done'
    });
  } catch {
    updateMessage(assistantId, {
      content: '回答失败，请稍后重试。',
      status: 'error'
    });
  } finally {
    setState({ pendingCount: Math.max(0, state.pendingCount - 1) });
  }
}

export function useChatSession() {
  const [snapshot, setSnapshot] = useState(getChatSessionState());

  useEffect(() => {
    return subscribeChatSession(() => {
      setSnapshot(getChatSessionState());
    });
  }, []);

  return {
    state: snapshot,
    setLevel: setChatStudentLevel,
    clear: clearChatSession,
    sendQuestion: sendChatQuestion
  };
}
