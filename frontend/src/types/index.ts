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
  deepseek_api_key: string;
  deepseek_base_url: string;
  openai_api_key: string;
  openai_base_url: string;
  zhipu_api_key: string;
  zhipu_base_url: string;
  configured_providers: {
    deepseek: boolean;
    openai: boolean;
    zhipu: boolean;
  };
  candidate_models: string[];
}

export interface ExamQuestion {
  type: string;
  title: string;
  score: number;
  answer_outline: string;
}

export interface ExamGenerateResponse {
  exam_id: string;
  title: string;
  questions: ExamQuestion[];
  latex_content: string;
  download_url: string;
  from_llm: boolean;
  model_used?: string;
}

export interface ExamListItem {
  id: string;
  title: string;
  knowledge_points: string;
  difficulty: string;
  total_score: number;
  paper_type: string;
  created_at: string;
}
