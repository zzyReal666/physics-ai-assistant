import { apiClient } from './client';
import type { ExamGenerateResponse, ExamListItem } from '../../types';

export async function generateExam(payload: {
  knowledge_points: string;
  difficulty: 'easy' | 'medium' | 'hard';
  question_types: string;
  total_score: number;
  paper_type: string;
}) {
  const { data } = await apiClient.post<ExamGenerateResponse>('/exam/generate', payload);
  return data;
}

export async function fetchExamList() {
  const { data } = await apiClient.get<ExamListItem[]>('/exam');
  return data;
}

export function downloadExamLatex(url: string) {
  return `/api${url}`;
}
