// Agents API client

import { api } from './api';

export type AgentType = 'finance' | 'data_analyst' | 'researcher' | 'team_lead';

export interface Agent {
  name: string;
  agent_type: AgentType;
  description: string;
}

export interface AgentListResponse {
  agents: Agent[];
  total: number;
}

export interface AgentStatus {
  agent_type: AgentType;
  status: 'available' | 'busy' | 'idle';
  current_task_id: number | null;
  tasks_in_queue: number;
  last_active_at: string;
  updated_at?: string;
}

export interface TaskSummary {
  id?: number; // Numeric ID for API calls
  task_id: string;
  title: string;
  status: string;
  priority: string;
  created_at: string;
  completed_at: string | null;
}

export interface TaskCounts {
  pending: number;
  queued: number;
  in_progress: number;
  completed: number;
  failed: number;
  cancelled: number;
}

export interface ChatHistoryMessage {
  message_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

export interface AgentOffice {
  agent_type: AgentType;
  status: AgentStatus;
  tasks: {
    recent: TaskSummary[];
    counts: TaskCounts;
  };
  chat_history: {
    recent: ChatHistoryMessage[];
    total: number;
  };
}

export interface ChatRequest {
  message: string;
  context?: Record<string, unknown>;
}

export interface ChatResponse {
  session_id: string;
  agent_type: AgentType;
  response: string;
  metadata: {
    agent_type: AgentType;
    user_context: unknown;
    events_count: number;
  };
  created_at: string;
}

export interface ChatHistoryResponse {
  messages: ChatHistoryMessage[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PromptBuilderRequest {
  agent_type: AgentType;
}

export interface PromptBuilderResponse {
  text: string;
}

// Agents API calls
export const agentsApi = {
  // List all agents
  listAgents: async (): Promise<AgentListResponse> => {
    return api.get<AgentListResponse>('/agents');
  },

  // Get agent office data
  getAgentOffice: async (agentType: AgentType): Promise<AgentOffice> => {
    return api.get<AgentOffice>(`/agents/${agentType}/office`);
  },

  // Chat with agent
  chatWithAgent: async (
    agentType: AgentType,
    request: ChatRequest
  ): Promise<ChatResponse> => {
    return api.post<ChatResponse>(`/agents/${agentType}/chat`, request);
  },

  // Get chat history
  getChatHistory: async (
    agentType: AgentType,
    page: number = 1,
    pageSize: number = 50
  ): Promise<ChatHistoryResponse> => {
    return api.get<ChatHistoryResponse>(
      `/agents/${agentType}/history?page=${page}&page_size=${pageSize}`
    );
  },

  // Get agent status
  getAgentStatus: async (agentType: AgentType): Promise<AgentStatus> => {
    return api.get<AgentStatus>(`/agents/status/${agentType}`);
  },

  // Get prompt builder for voice chat
  getPromptBuilder: async (agentType: AgentType): Promise<PromptBuilderResponse> => {
    return api.post<PromptBuilderResponse>('/tools/prompt-builder', { agent_type: agentType });
  },
};
