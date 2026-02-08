import { create } from 'zustand';
import { agentsApi, Agent, AgentOffice, AgentStatus, AgentType } from '@/lib/agents';
import { ApiError } from '@/lib/api';

interface AgentsState {
  agents: Agent[];
  agentOffices: Record<AgentType, AgentOffice | null>;
  agentStatuses: Record<AgentType, AgentStatus | null>;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchAgents: () => Promise<void>;
  fetchAgentOffice: (agentType: AgentType) => Promise<void>;
  fetchAgentStatus: (agentType: AgentType) => Promise<void>;
  clearError: () => void;
}

export const useAgents = create<AgentsState>((set, get) => ({
  agents: [],
  agentOffices: {
    finance: null,
    data_analyst: null,
    researcher: null,
    team_lead: null,
  },
  agentStatuses: {
    finance: null,
    data_analyst: null,
    researcher: null,
    team_lead: null,
  },
  isLoading: false,
  error: null,

  fetchAgents: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await agentsApi.listAgents();
      set({
        agents: response.agents,
        isLoading: false,
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : 'Failed to fetch agents';
      set({
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  fetchAgentOffice: async (agentType: AgentType) => {
    // Don't set global loading state for individual office fetches
    try {
      const office = await agentsApi.getAgentOffice(agentType);
      set({
        agentOffices: {
          ...get().agentOffices,
          [agentType]: office,
        },
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : `Failed to fetch ${agentType} office`;
      set({
        error: errorMessage,
      });
      throw error;
    }
  },

  fetchAgentStatus: async (agentType: AgentType) => {
    try {
      const status = await agentsApi.getAgentStatus(agentType);
      set({
        agentStatuses: {
          ...get().agentStatuses,
          [agentType]: status,
        },
      });
    } catch (error) {
      console.error(`Failed to fetch ${agentType} status:`, error);
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
