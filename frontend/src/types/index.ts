export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  created_at: string;
}

export interface DocumentChunk {
  index: string;
  content: string;
}

export interface DocumentDetail extends DocumentItem {
  stored_filename: string;
  chunk_count: number;
  chunks: DocumentChunk[];
}

export interface ChatReference {
  source: string;
  content: string;
}

export interface ChatAnswer {
  content: string;
  model_used?: string;
  from_llm: boolean;
  references: ChatReference[];
}

export interface TeachingPlanResponse {
  topic: string;
  plan_markdown: string;
  model_used?: string;
  from_llm: boolean;
}

export interface ModelConfig {
  default_llm_model: string;
  configured_providers: {
    deepseek: boolean;
    openai: boolean;
    zhipu: boolean;
  };
  candidate_models: string[];
}
