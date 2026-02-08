// CEO API client

import { api } from './api';

// Dashboard Overview Types
export interface CEODashboardOverview {
  overview: {
    total_tasks: number;
    completed_tasks: number;
    in_progress_tasks: number;
    pending_tasks: number;
    average_progress: number;
    last_updated: string;
  };
  tasks_by_agent: Array<{
    agent_id: string;
    agent_type: string;
    agent_name: string;
    agent_role: string;
    task_count: number;
    tasks: Array<{
      id: string;
      title: string;
      status: string;
      priority: string;
      progress: number;
      due_date: string;
      created_at: string;
      updated_at: string;
    }>;
  }>;
  recent_activity: Array<{
    id: string;
    timestamp: string;
    action_type: string;
    action: string;
    details: string;
    actor: string;
    target_agent?: string;
    metadata?: Record<string, unknown>;
  }>;
}

// Activity History Types
export interface CEOActivity {
  id: string;
  timestamp: string;
  action_type: string;
  action: string;
  details: string;
  actor: string;
  target_agent?: string;
  metadata?: Record<string, unknown>;
}

export interface CEOActivityResponse {
  activities: CEOActivity[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Chat Types
export interface CEOChatMessage {
  message_id: string;
  sender: string;
  message: string;
  mentioned_agents: string[];
  timestamp: string;
  status: string;
  agent_responses?: Array<{
    agent_id: string;
    agent_name: string;
    response: string;
    timestamp: string;
    response_time_seconds: number;
  }>;
}

export interface CEOChatRequest {
  message: string;
  mentioned_agents: string[];
  context?: Record<string, unknown>;
}

export interface CEOChatHistoryResponse {
  messages: CEOChatMessage[];
  total: number;
  page: number;
  page_size: number;
}

// CEO API calls
export const ceoApi = {
  // Get dashboard overview
  getDashboard: async (params?: {
    include_tasks?: boolean;
    include_activity?: boolean;
    activity_limit?: number;
  }): Promise<CEODashboardOverview> => {
    const queryParams = new URLSearchParams();
    if (params?.include_tasks !== undefined) {
      queryParams.append('include_tasks', params.include_tasks.toString());
    }
    if (params?.include_activity !== undefined) {
      queryParams.append('include_activity', params.include_activity.toString());
    }
    if (params?.activity_limit) {
      queryParams.append('activity_limit', params.activity_limit.toString());
    }
    
    const query = queryParams.toString();
    return api.get<CEODashboardOverview>(
      `/ceo/dashboard${query ? `?${query}` : ''}`
    );
  },

  // Get activity history
  getActivity: async (params?: {
    page?: number;
    page_size?: number;
    action_type?: string;
    date_from?: string;
    date_to?: string;
    agent_id?: string;
  }): Promise<CEOActivityResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.action_type) queryParams.append('action_type', params.action_type);
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);
    if (params?.agent_id) queryParams.append('agent_id', params.agent_id);
    
    const query = queryParams.toString();
    return api.get<CEOActivityResponse>(
      `/ceo/activity${query ? `?${query}` : ''}`
    );
  },

  // Send chat message
  sendMessage: async (request: CEOChatRequest): Promise<CEOChatMessage> => {
    return api.post<CEOChatMessage>('/ceo/chat', request);
  },

  // Get chat history
  getChatHistory: async (params?: {
    page?: number;
    page_size?: number;
    agent_id?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<CEOChatHistoryResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.agent_id) queryParams.append('agent_id', params.agent_id);
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);
    
    const query = queryParams.toString();
    return api.get<CEOChatHistoryResponse>(
      `/ceo/chat/history${query ? `?${query}` : ''}`
    );
  },
};
