import { fetchDocuments } from '../services/api/documents';

export async function useDocuments() {
  return fetchDocuments();
}
