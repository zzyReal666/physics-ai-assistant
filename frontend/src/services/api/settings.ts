import { apiClient } from './client';
import type { ModelConfig } from '../../types';

export async function fetchModelConfig() {
  const { data } = await apiClient.get<ModelConfig>('/settings/model');
  return data;
}

export async function updateModelConfig(defaultModel: string) {
  const { data } = await apiClient.put<ModelConfig>('/settings/model', {
    default_llm_model: defaultModel
  });
  return data;
}
