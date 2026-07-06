export interface Question {
  id: string;
  question: string;
}

export interface AgentInput {
  focus_group_description: string;
  persona_count: number;
  questions: Question[];
  review_guidance: string;
}

export interface Persona {
  id: string;
  name: string;
  bio: string;
  demographics: string;
}

export interface Annotation {
  timestamp_sec: number;
  comment: string;
  score: number;
}

export interface QuestionResponse {
  question_id: string;
  answer: string;
  score: number;
}

export interface ContentReview {
  persona_id: string;
  answers: QuestionResponse[];
  annotations: Annotation[];
}

export interface AgentState {
  run_id: string;
  user_prompt: string;
  content_cache_key: string;
  agent_input: AgentInput | null;
  personas: Persona[];
  reviews: ContentReview[];
  is_complete: boolean;
}