import axiosInstance from './axiosConfig';

// Get all user alerts
export const getAlerts = async () => {
  const response = await axiosInstance.get('/api/v1/alerts');
  return response.data;
};

// Create a new alert
export const createAlert = async (alertData: {
  symbol: string;
  type: 'price' | 'technical' | 'news';
  condition: 'above' | 'below' | 'percent_change';
  value: number;
  active: boolean;
}) => {
  const response = await axiosInstance.post('/api/v1/alerts', alertData);
  return response.data;
};

// Update an existing alert
export const updateAlert = async (alertId: string, alertData: Partial<{
  symbol: string;
  type: 'price' | 'technical' | 'news';
  condition: 'above' | 'below' | 'percent_change';
  value: number;
  active: boolean;
}>) => {
  const response = await axiosInstance.put(`/api/v1/alerts/${alertId}`, alertData);
  return response.data;
};

// Delete an alert
export const deleteAlert = async (alertId: string) => {
  const response = await axiosInstance.delete(`/api/v1/alerts/${alertId}`);
  return response.data;
};

// Setup WebSocket connection for real-time alerts
export const setupAlertWebSocket = (userId: string, onMessage: (data: any) => void) => {
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const wsUrl = API_URL.replace('http', 'ws') + `/ws/alerts/${userId}`;
  
  const socket = new WebSocket(wsUrl);
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  
  socket.onclose = () => {
    console.log('Alert WebSocket connection closed');
    // Attempt to reconnect after a delay
    setTimeout(() => setupAlertWebSocket(userId, onMessage), 5000);
  };
  
  socket.onerror = (error) => {
    console.error('Alert WebSocket error:', error);
    socket.close();
  };
  
  return socket;
}; 