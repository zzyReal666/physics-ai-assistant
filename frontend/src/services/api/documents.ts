import { apiClient } from './client';
import type { DocumentDetail, DocumentItem } from '../../types';

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append('file', file);
  const { data } = await apiClient.post('/documents/upload', form);
  return data;
}

export async function fetchDocuments() {
  const { data } = await apiClient.get<DocumentItem[]>('/documents');
  return data;
}

export async function fetchDocumentDetail(id: string) {
  const { data } = await apiClient.get<DocumentDetail>(`/documents/${id}`);
  return data;
}

export async function deleteDocument(id: string) {
  const { data } = await apiClient.delete<{ success: boolean; message: string }>(
    `/documents/${id}`
  );
  return data;
}
