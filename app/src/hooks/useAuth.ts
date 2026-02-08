import { create } from 'zustand';
import { authApi, tokenManager, userManager, User } from '@/lib/auth';
import { ApiError } from '@/lib/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  initAuth: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: userManager.getUser(),
  isAuthenticated: tokenManager.isAuthenticated(),
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      // Login and get token
      const { access_token } = await authApi.login({ email, password });
      tokenManager.setToken(access_token);

      // Fetch user data
      const user = await authApi.getCurrentUser();
      userManager.setUser(user);

      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : 'Login failed. Please try again.';
      
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  register: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      // Register user
      await authApi.register({ email, password });

      // Auto-login after registration
      const { access_token } = await authApi.login({ email, password });
      tokenManager.setToken(access_token);

      // Fetch user data
      const user = await authApi.getCurrentUser();
      userManager.setUser(user);

      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : 'Registration failed. Please try again.';
      
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  logout: () => {
    authApi.logout();
    userManager.removeUser();
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    });
  },

  clearError: () => {
    set({ error: null });
  },

  initAuth: async () => {
    const token = tokenManager.getToken();
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    set({ isLoading: true });
    try {
      const user = await authApi.getCurrentUser();
      userManager.setUser(user);
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      // Token is invalid, clear it
      tokenManager.removeToken();
      userManager.removeUser();
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
}));
