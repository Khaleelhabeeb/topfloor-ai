// Tasks API client

import { api } from './api';
import { AgentType } from './agents';

export type TaskStatus = 'pending' | 'queued' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';
export type TaskType = 'chat' | 'background';

export interface Task {
  id: number;
  task_id: string;
  title: string;
  description: string;
  agent_type: AgentType;
  task_type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  input_data: Record<string, unknown> | null;
  result_data: {
    summary?: string;
    response?: string;
    render_payload?: {
      type: string;
      content: Record<string, unknown>;
    };
    session_id?: string;
    events_count?: number;
    memories_used?: number;
    context?: unknown;
  } | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface CreateTaskRequest {
  agent_type: AgentType;
  title: string;
  description: string;
  priority?: TaskPriority;
  task_type?: TaskType;
  input_data?: Record<string, unknown>;
}

export interface UpdateTaskRequest {
  status?: TaskStatus;
  priority?: TaskPriority;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page: number;
  page_size: number;
}

export interface TaskStatusResponse {
  task_id: string;
  status: TaskStatus;
  progress: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

// Tasks API calls
export const tasksApi = {
  // Create a new task
  createTask: async (request: CreateTaskRequest): Promise<Task> => {
    return api.post<Task>('/tasks', request);
  },

  // List tasks with optional filtering
  listTasks: async (params?: {
    status?: TaskStatus;
    agent_type?: AgentType;
    page?: number;
    page_size?: number;
  }): Promise<TaskListResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.agent_type) queryParams.append('agent_type', params.agent_type);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

    const query = queryParams.toString();
    return api.get<TaskListResponse>(`/tasks${query ? `?${query}` : ''}`);
  },

  // Get task details
  getTask: async (taskId: number): Promise<Task> => {
    return api.get<Task>(`/tasks/${taskId}`);
  },

  // Get task status
  getTaskStatus: async (taskId: number): Promise<TaskStatusResponse> => {
    return api.get<TaskStatusResponse>(`/tasks/${taskId}/status`);
  },

  // Update task
  updateTask: async (taskId: number, request: UpdateTaskRequest): Promise<Task> => {
    return api.patch<Task>(`/tasks/${taskId}`, request);
  },

  // Delete task
  deleteTask: async (taskId: number): Promise<void> => {
    return api.delete(`/tasks/${taskId}`);
  },

  // Get tasks for a specific agent
  getAgentTasks: async (
    agentType: AgentType,
    params?: {
      status?: TaskStatus;
      page?: number;
      page_size?: number;
    }
  ): Promise<TaskListResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

    const query = queryParams.toString();
    return api.get<TaskListResponse>(
      `/tasks/agents/${agentType}${query ? `?${query}` : ''}`
    );
  },
};
