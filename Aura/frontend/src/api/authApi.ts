import axiosInstance from './axiosConfig';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await axiosInstance.post<AuthResponse>('/api/v1/auth/login', credentials);
  return response.data;
};

export const register = async (userData: RegisterData): Promise<AuthResponse> => {
  const response = await axiosInstance.post<AuthResponse>('/api/v1/auth/register', userData);
  return response.data;
};

export const logout = async (): Promise<void> => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const getUserProfile = async (): Promise<any> => {
  const response = await axiosInstance.get('/api/v1/users/me');
  return response.data;
};

export const updateUserProfile = async (profileData: any): Promise<any> => {
  const response = await axiosInstance.put('/api/v1/users/me', profileData);
  return response.data;
}; 