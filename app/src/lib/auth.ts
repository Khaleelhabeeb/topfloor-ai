// Authentication utilities and API calls

import { api } from './api';

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface RegisterResponse {
  id: number;
  email: string;
  created_at: string;
}

// Auth API calls
export const authApi = {
  // Register new user
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    return api.post<RegisterResponse>('/auth/register', data, {
      requiresAuth: false,
    });
  },

  // Login user
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return api.post<LoginResponse>('/auth/login', data, {
      requiresAuth: false,
    });
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    return api.get<User>('/auth/me');
  },

  // Logout (client-side only)
  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  },
};

// Token management
export const tokenManager = {
  getToken: (): string | null => {
    return localStorage.getItem('auth_token');
  },

  setToken: (token: string): void => {
    localStorage.setItem('auth_token', token);
  },

  removeToken: (): void => {
    localStorage.removeItem('auth_token');
  },

  isAuthenticated: (): boolean => {
    return !!tokenManager.getToken();
  },
};

// User management
export const userManager = {
  getUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  setUser: (user: User): void => {
    localStorage.setItem('user', JSON.stringify(user));
  },

  removeUser: (): void => {
    localStorage.removeItem('user');
  },
};
