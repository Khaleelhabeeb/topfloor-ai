// CEO Dashboard state management

import { create } from 'zustand';
import { ceoApi, CEODashboardOverview, CEOActivity, CEOChatMessage } from '@/lib/ceo';

interface CEOState {
  // Dashboard data
  dashboard: CEODashboardOverview | null;
  isLoadingDashboard: boolean;
  dashboardError: string | null;

  // Activity history
  activities: CEOActivity[];
  activityTotal: number;
  activityPage: number;
  isLoadingActivity: boolean;
  activityError: string | null;

  // Chat messages
  chatMessages: CEOChatMessage[];
  isSendingMessage: boolean;
  chatError: string | null;

  // Actions
  fetchDashboard: () => Promise<void>;
  fetchActivity: (page?: number) => Promise<void>;
  sendChatMessage: (message: string, mentionedAgents: string[], context?: Record<string, unknown>) => Promise<void>;
  addLocalChatMessage: (message: CEOChatMessage) => void;
  clearChatMessages: () => void;
}

export const useCEO = create<CEOState>((set, get) => ({
  // Initial state
  dashboard: null,
  isLoadingDashboard: false,
  dashboardError: null,

  activities: [],
  activityTotal: 0,
  activityPage: 1,
  isLoadingActivity: false,
  activityError: null,

  chatMessages: [],
  isSendingMessage: false,
  chatError: null,

  // Fetch dashboard overview
  fetchDashboard: async () => {
    set({ isLoadingDashboard: true, dashboardError: null });
    try {
      const data = await ceoApi.getDashboard({
        include_tasks: true,
        include_activity: true,
        activity_limit: 10,
      });
      set({ dashboard: data, isLoadingDashboard: false });
    } catch (error) {
      console.error('Failed to fetch CEO dashboard:', error);
      set({
        dashboardError: error instanceof Error ? error.message : 'Failed to load dashboard',
        isLoadingDashboard: false,
      });
    }
  },

  // Fetch activity history
  fetchActivity: async (page = 1) => {
    set({ isLoadingActivity: true, activityError: null });
    try {
      const data = await ceoApi.getActivity({
        page,
        page_size: 20,
      });
      set({
        activities: data.activities,
        activityTotal: data.total,
        activityPage: page,
        isLoadingActivity: false,
      });
    } catch (error) {
      console.error('Failed to fetch activity history:', error);
      set({
        activityError: error instanceof Error ? error.message : 'Failed to load activity',
        isLoadingActivity: false,
      });
    }
  },

  // Send chat message
  sendChatMessage: async (message: string, mentionedAgents: string[], context?: Record<string, unknown>) => {
    set({ isSendingMessage: true, chatError: null });
    try {
      const response = await ceoApi.sendMessage({
        message,
        mentioned_agents: mentionedAgents,
        context,
      });
      
      // Add the message with responses to chat
      set((state) => ({
        chatMessages: [...state.chatMessages, response],
        isSendingMessage: false,
      }));
    } catch (error) {
      console.error('Failed to send chat message:', error);
      set({
        chatError: error instanceof Error ? error.message : 'Failed to send message',
        isSendingMessage: false,
      });
    }
  },

  // Add local chat message (for optimistic updates)
  addLocalChatMessage: (message: CEOChatMessage) => {
    set((state) => ({
      chatMessages: [...state.chatMessages, message],
    }));
  },

  // Clear chat messages
  clearChatMessages: () => {
    set({ chatMessages: [] });
  },
}));
