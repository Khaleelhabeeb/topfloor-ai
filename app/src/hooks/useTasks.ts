import { create } from 'zustand';
import { tasksApi, Task, CreateTaskRequest, UpdateTaskRequest, TaskStatus } from '@/lib/tasks';
import { AgentType } from '@/lib/agents';
import { ApiError } from '@/lib/api';

interface TasksState {
  tasks: Task[];
  currentTask: Task | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchTasks: (params?: { status?: TaskStatus; agent_type?: AgentType }) => Promise<void>;
  fetchAgentTasks: (agentType: AgentType, status?: TaskStatus) => Promise<void>;
  fetchTask: (taskId: number) => Promise<void>;
  createTask: (request: CreateTaskRequest) => Promise<Task>;
  updateTask: (taskId: number, request: UpdateTaskRequest) => Promise<void>;
  deleteTask: (taskId: number) => Promise<void>;
  clearError: () => void;
  clearCurrentTask: () => void;
}

export const useTasks = create<TasksState>((set, get) => ({
  tasks: [],
  currentTask: null,
  isLoading: false,
  error: null,

  fetchTasks: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tasksApi.listTasks(params);
      set({
        tasks: response.tasks,
        isLoading: false,
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : 'Failed to fetch tasks';
      set({
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  fetchAgentTasks: async (agentType, status) => {
    set({ isLoading: true, error: null });
    try {
      const response = await tasksApi.getAgentTasks(agentType, { status });
      set({
        tasks: response.tasks,
        isLoading: false,
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : `Failed to fetch ${agentType} tasks`;
      set({
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  fetchTask: async (taskId) => {
    set({ isLoading: true, error: null });
    try {
      const task = await tasksApi.getTask(taskId);
      set({
        currentTask: task,
        isLoading: false,
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : 'Failed to fetch task';
      set({
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  createTask: async (request) => {
    set({ isLoading: true, error: null });
    try {
      const task = await tasksApi.createTask(request);
      set({
        tasks: [task, ...get().tasks],
        isLoading: false,
      });
      return task;
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : 'Failed to create task';
      set({
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  updateTask: async (taskId, request) => {
    set({ isLoading: true, error: null });
    try {
      const updatedTask = await tasksApi.updateTask(taskId, request);
      set({
        tasks: get().tasks.map(t => t.id === taskId ? updatedTask : t),
        currentTask: get().currentTask?.id === taskId ? updatedTask : get().currentTask,
        isLoading: false,
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : 'Failed to update task';
      set({
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  deleteTask: async (taskId) => {
    set({ isLoading: true, error: null });
    try {
      await tasksApi.deleteTask(taskId);
      set({
        tasks: get().tasks.filter(t => t.id !== taskId),
        currentTask: get().currentTask?.id === taskId ? null : get().currentTask,
        isLoading: false,
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : 'Failed to delete task';
      set({
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  clearCurrentTask: () => {
    set({ currentTask: null });
  },
}));
