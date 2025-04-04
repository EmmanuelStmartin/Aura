import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import PortfolioPage from './pages/PortfolioPage';
import MarketDataPage from './pages/MarketDataPage';
import AlertsConfigPage from './pages/AlertsConfigPage';
import AIPredictionsPage from './pages/AIPredictionsPage';
import PortfolioOptimizationPage from './pages/PortfolioOptimizationPage';
import OrderPage from './pages/OrderPage';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/portfolio" element={<PortfolioPage />} />
            <Route path="/market-data" element={<MarketDataPage />} />
            <Route path="/alerts" element={<AlertsConfigPage />} />
            <Route path="/predictions" element={<AIPredictionsPage />} />
            <Route path="/optimization" element={<PortfolioOptimizationPage />} />
            <Route path="/order" element={<OrderPage />} />
          </Route>
          
          {/* Redirect to login or dashboard based on auth state */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
