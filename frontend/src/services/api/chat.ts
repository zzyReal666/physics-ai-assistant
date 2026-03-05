import { apiClient } from './client';
import type { ChatAnswer } from '../../types';

export async function askQuestion(question: string, studentLevel: 'junior' | 'senior') {
  const { data } = await apiClient.post<ChatAnswer>('/chat/ask', {
    question,
    student_level: studentLevel
  });
  return data;
}
