import axiosInstance from './axiosConfig';

// Get user portfolio positions
export const getPositions = async () => {
  const response = await axiosInstance.get('/api/v1/brokerage/positions');
  return response.data;
};

// Get order history
export const getOrders = async (status?: string) => {
  const params = status ? { status } : {};
  const response = await axiosInstance.get('/api/v1/brokerage/orders', { params });
  return response.data;
};

// Place a new order
export const placeOrder = async (orderData: {
  symbol: string;
  qty: number;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop' | 'stop_limit';
  time_in_force: 'day' | 'gtc' | 'ioc' | 'fok';
  limit_price?: number;
  stop_price?: number;
}) => {
  const response = await axiosInstance.post('/api/v1/brokerage/orders', orderData);
  return response.data;
};

// Cancel an order
export const cancelOrder = async (orderId: string) => {
  const response = await axiosInstance.delete(`/api/v1/brokerage/orders/${orderId}`);
  return response.data;
};

// Get account information
export const getAccount = async () => {
  const response = await axiosInstance.get('/api/v1/brokerage/account');
  return response.data;
}; 