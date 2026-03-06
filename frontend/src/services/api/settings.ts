import { apiClient } from './client';
import type { ModelConfig } from '../../types';

export async function fetchModelConfig() {
  const { data } = await apiClient.get<ModelConfig>('/settings/model');
  return data;
}

export async function updateModelConfig(defaultModel: string) {
  return updateModelRuntimeConfig({
    default_llm_model: defaultModel
  });
}

export async function updateModelRuntimeConfig(payload: {
  default_llm_model: string;
  deepseek_api_key?: string;
  deepseek_base_url?: string;
  openai_api_key?: string;
  openai_base_url?: string;
  zhipu_api_key?: string;
  zhipu_base_url?: string;
}) {
  const { data } = await apiClient.put<ModelConfig>('/settings/model', {
    deepseek_api_key: '',
    deepseek_base_url: '',
    openai_api_key: '',
    openai_base_url: '',
    zhipu_api_key: '',
    zhipu_base_url: '',
    ...payload
  });
  return data;
}
