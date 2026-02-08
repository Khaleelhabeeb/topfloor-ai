import { create } from 'zustand';
import { Employee, CEOFolder } from '@/data/employees';

export type GameMode = 'exploring' | 'video-call' | 'ceo-desk' | 'folder-view';
export type VideoCallMode = 'interface' | 'live-call';

interface ChatMessage {
  sender: string;
  text: string;
  time: string;
  isUser?: boolean;
}

interface GameState {
  mode: GameMode;
  videoCallMode: VideoCallMode;
  currentEmployee: Employee | null;
  currentFolder: CEOFolder | null;
  chatMessages: Record<string, ChatMessage[]>;
  playerPosition: { x: number; z: number };
  insideDoor: string | null;
  nearChair: boolean;
  isSeated: boolean;
  
  // Actions
  setMode: (mode: GameMode) => void;
  setVideoCallMode: (mode: VideoCallMode) => void;
  enterVideoCall: (employee: Employee) => void;
  exitVideoCall: () => void;
  enterCEODesk: () => void;
  exitCEODesk: () => void;
  openFolder: (folder: CEOFolder) => void;
  closeFolder: () => void;
  addChatMessage: (employeeId: string, message: ChatMessage) => void;
  setPlayerPosition: (position: { x: number; z: number }) => void;
  setInsideDoor: (doorId: string | null) => void;
  setNearChair: (near: boolean) => void;
  setIsSeated: (seated: boolean) => void;
}

export const useGameState = create<GameState>((set, get) => ({
  mode: 'exploring',
  videoCallMode: 'interface',
  currentEmployee: null,
  currentFolder: null,
  chatMessages: {},
  playerPosition: { x: 0, z: 0 },
  insideDoor: null,
  nearChair: false,
  isSeated: false,

  setMode: (mode) => set({ mode }),
  setVideoCallMode: (videoCallMode) => set({ videoCallMode }),

  enterVideoCall: (employee) => {
    const currentMessages = get().chatMessages[employee.id] || [...employee.initialMessages];
    set({
      mode: 'video-call',
      videoCallMode: 'interface',
      currentEmployee: employee,
      chatMessages: {
        ...get().chatMessages,
        [employee.id]: currentMessages,
      },
    });
  },

  exitVideoCall: () => set({
    mode: 'exploring',
    videoCallMode: 'interface',
    currentEmployee: null,
  }),

  enterCEODesk: () => set({
    mode: 'ceo-desk',
    isSeated: true,
  }),

  exitCEODesk: () => set({
    mode: 'exploring',
    isSeated: false,
    currentFolder: null,
  }),

  openFolder: (folder) => set({
    mode: 'folder-view',
    currentFolder: folder,
  }),

  closeFolder: () => set({
    mode: 'ceo-desk',
    currentFolder: null,
  }),

  addChatMessage: (employeeId, message) => {
    const currentMessages = get().chatMessages[employeeId] || [];
    set({
      chatMessages: {
        ...get().chatMessages,
        [employeeId]: [...currentMessages, message],
      },
    });
  },

  setPlayerPosition: (position) => set({ playerPosition: position }),
  setInsideDoor: (doorId) => set({ insideDoor: doorId }),
  setNearChair: (near) => set({ nearChair: near }),
  setIsSeated: (seated) => set({ isSeated: seated }),
}));
