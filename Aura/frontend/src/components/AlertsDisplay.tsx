import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
// Assuming useAuth and axiosInstance are correctly set up elsewhere
// import { useAuth } from '../hooks/useAuth';
// import axiosInstance from '../api/axiosConfig';

// Mock useAuth for standalone example
const useAuth = () => ({
  user: { id: 'mockUserId', name: 'Mock User' } // Provide a mock user object
});

// Mock axiosInstance for standalone example
const axiosInstance = {
  get: (url: string) => {
    console.log(`Mock GET request to: ${url}`);
    return Promise.resolve({ data: [] }); // Return empty array for mock API calls
  },
  patch: (url: string) => {
    console.log(`Mock PATCH request to: ${url}`);
    return Promise.resolve({ data: {} });
  }
};


// --- Types ---
interface Alert {
  id: string;
  user_id: string;
  rule_id: string;
  rule_name: string;
  symbol?: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  is_read: boolean;
  created_at: string;
}

interface AlertsDisplayProps {
  maxAlerts?: number; // Maximum number of alerts to display initially
}

// --- Styled Components ---
const Container = styled.div`
  width: 100%;
  font-family: sans-serif; /* Added for better default styling */
`;

const AlertsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px; /* Limit height and enable scrolling */
  overflow-y: auto;
  padding-right: 4px; /* Add padding for scrollbar */
`;

const AlertItem = styled.div<{ severity: string; isRead: boolean }>`
  display: flex;
  padding: 12px;
  border-radius: 8px;
  background-color: ${props => {
    // Use lighter background for read alerts
    if (props.isRead) return '#f0f0f0'; // Slightly darker grey for read items

    // Background color based on severity for unread items
    switch (props.severity) {
      case 'low': return 'rgba(133, 193, 233, 0.1)'; // Light blue tint
      case 'medium': return 'rgba(244, 208, 63, 0.1)'; // Light yellow tint
      case 'high': return 'rgba(230, 126, 34, 0.1)'; // Light orange tint
      case 'critical': return 'rgba(246, 70, 93, 0.1)'; // Light red tint
      default: return 'rgba(133, 193, 233, 0.1)'; // Default to low severity color
    }
  }};
  border-left: 4px solid ${props => {
    // Left border color based on severity
    switch (props.severity) {
      case 'low': return '#85C1E9'; // Blue
      case 'medium': return '#F4D03F'; // Yellow
      case 'high': return '#E67E22'; // Orange
      case 'critical': return '#F6465D'; // Red
      default: return '#85C1E9'; // Default to low severity color
    }
  }};
  opacity: ${props => props.isRead ? 0.7 : 1}; /* Slightly fade read alerts */
  transition: background-color 0.2s ease, opacity 0.2s ease; /* Smooth transitions */
`;

const AlertContent = styled.div`
  flex: 1; /* Take remaining space */
`;

const AlertHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 4px;
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
`;

const AlertTitle = styled.div`
  font-weight: 500;
  font-size: 14px;
  color: #333;
  margin-right: 8px;
`;

const AlertSymbol = styled.span`
  font-weight: 600;
  margin-right: 4px;
  color: #555; /* Slightly different color for symbol */
`;

const AlertTime = styled.div`
  font-size: 12px;
  color: #666;
  margin-left: auto; /* Push time to the right */
  white-space: nowrap; /* Prevent time from wrapping */
  padding-left: 8px; /* Add space between title and time */
`;

const AlertMessage = styled.div`
  font-size: 14px;
  color: #444; /* Slightly darker message color */
  line-height: 1.4; /* Improve readability */
`;

const AlertActions = styled.div`
  display: flex;
  align-items: flex-start; /* Align button to the top */
  margin-left: 12px;
`;

const MarkReadButton = styled.button`
  background: none;
  border: none;
  color: #4a90e2; /* Blue link color */
  cursor: pointer;
  font-size: 12px;
  padding: 0;
  white-space: nowrap; /* Prevent button text wrapping */

  &:hover {
    text-decoration: underline;
  }

  &:disabled {
    color: #999; /* Grey out when disabled */
    cursor: default;
    text-decoration: none;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 32px 16px;
  color: #666;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px dashed #ddd; /* Add a subtle border */
`;

const LoadingState = styled.div`
  text-align: center;
  padding: 32px 16px;
  color: #666;
`;

const HeaderRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px; /* Increased margin */
  padding-bottom: 8px; /* Add padding below header */
  border-bottom: 1px solid #eee; /* Add separator line */
`;

const Title = styled.h3`
  margin: 0;
  font-size: 18px;
  color: #333;
  font-weight: 600; /* Make title bolder */
`;

const MarkAllReadButton = styled.button`
  background: none;
  border: none;
  color: #4a90e2;
  cursor: pointer;
  font-size: 14px;
  margin-left: 16px; /* Add space if both buttons are shown */

  &:hover {
    text-decoration: underline;
  }

  &:disabled {
    color: #999;
    cursor: default;
    text-decoration: none;
  }
`;

const SeeAllLink = styled.a`
  color: #4a90e2;
  text-decoration: none;
  font-size: 14px;

  &:hover {
    text-decoration: underline;
  }
`;

// --- Helper Functions ---

/**
 * Formats a date string into a relative time string (e.g., "5m ago", "2h ago").
 * @param dateString - The ISO date string to format.
 * @returns A relative time string.
 */
const formatRelativeTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();

    const seconds = Math.floor(diffMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  } catch (error) {
    console.error("Error formatting date:", dateString, error);
    return 'Invalid date'; // Handle potential invalid date strings
  }
};

// --- Mock WebSocket ---
// In a real app, this would use an actual WebSocket connection library.
class MockWebSocket {
  private callbacks: Record<string, (event?: any) => void> = {};
  private userId: string;
  private interval: NodeJS.Timeout | null = null;

  constructor(userId: string) {
    this.userId = userId;
  }

  addEventListener(event: string, callback: (event?: any) => void) {
    this.callbacks[event] = callback;
  }

  removeEventListener(event: string) {
    delete this.callbacks[event];
  }

  connect() {
    console.log(`[Mock WebSocket] Connecting for user: ${this.userId}`);
    // Simulate connection opening
    setTimeout(() => {
        if (this.callbacks.open) {
            this.callbacks.open();
        }
        console.log(`[Mock WebSocket] Connected to /ws/alerts/${this.userId}`);
    }, 50); // Short delay to simulate async connection


    // Simulate receiving alerts periodically
    this.interval = setInterval(() => {
      if (Math.random() < 0.2) { // 20% chance of getting an alert
        const mockAlert = this.generateMockAlert();
        if (this.callbacks.message) {
          console.log('[Mock WebSocket] Sending mock alert:', mockAlert);
          this.callbacks.message({ data: JSON.stringify(mockAlert) });
        }
      }
    }, 15000); // Send mock alerts more frequently (every 15s) for demo
  }

  disconnect() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    // Simulate connection closing
     if (this.callbacks.close) {
        this.callbacks.close();
     }
    console.log('[Mock WebSocket] Disconnected');
  }

  // Generates a single mock alert object
  private generateMockAlert(): Alert {
    const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META'];
    const severities: Alert['severity'][] = ['low', 'medium', 'high', 'critical'];
    const ruleNames = [
      'Price Movement Alert', 'RSI Alert', 'Volume Spike',
      'Sentiment Change', 'Moving Average Crossover', 'Earnings Reminder'
    ];

    const severity = severities[Math.floor(Math.random() * severities.length)];
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    const ruleName = ruleNames[Math.floor(Math.random() * ruleNames.length)];

    let message = '';
    // Generate more varied messages
    switch (ruleName) {
        case 'Price Movement Alert':
            message = `${symbol} price ${Math.random() > 0.5 ? 'up' : 'down'} ${(Math.random() * 5 + 1).toFixed(1)}% in the last hour.`;
            break;
        case 'RSI Alert':
            message = `${symbol} RSI (${Math.floor(Math.random() * 70 + 15)}) approaching ${Math.random() > 0.5 ? 'overbought' : 'oversold'} levels.`;
            break;
        case 'Volume Spike':
            message = `Unusual volume detected for ${symbol}: ${(Math.random() * 200 + 100).toFixed(0)}% above 10-day average.`;
            break;
        case 'Sentiment Change':
            message = `Market sentiment for ${symbol} has shifted ${Math.random() > 0.5 ? 'positive' : 'negative'} based on recent news.`;
            break;
        case 'Moving Average Crossover':
            message = `${symbol}: ${Math.random() > 0.5 ? '50-day MA crossed above 200-day MA (Golden Cross)' : '50-day MA crossed below 200-day MA (Death Cross)'}.`;
            break;
        case 'Earnings Reminder':
            message = `${symbol} reports earnings ${Math.random() > 0.5 ? 'tomorrow' : 'today after market close'}.`;
            break;
        default:
             message = `Generic alert for ${symbol}.`;
    }

    return {
      id: `alert_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`, // More unique ID
      user_id: this.userId,
      rule_id: `rule_${Math.floor(Math.random() * 100)}`,
      rule_name: ruleName,
      symbol,
      message,
      severity,
      is_read: false, // New alerts are always unread
      created_at: new Date().toISOString()
    };
  }
}

// --- React Component ---
const AlertsDisplay: React.FC<AlertsDisplayProps> = ({ maxAlerts = 5 }) => {
  const { user } = useAuth(); // Get user from auth context
  const [alerts, setAlerts] = useState<Alert[]>([]); // State for storing alerts
  const [loading, setLoading] = useState(true); // State for loading status
  const [error, setError] = useState<string | null>(null); // State for error messages

  // --- Callbacks (Memoized Functions) ---

  /**
   * Fetches initial alerts from the API (or generates mock data).
   * Memoized with useCallback to prevent re-creation on every render.
   */
  const fetchAlerts = useCallback(async () => {
    if (!user) return; // Don't fetch if no user

    console.log('Fetching initial alerts...');
    setLoading(true);
    setError(null);

    try {
      // --- REAL API CALL (Commented out for demo) ---
      // const response = await axiosInstance.get(
      //   `/api/v1/alerts?user_id=${user.id}&limit=${maxAlerts}&sort=created_at:desc` // Fetch latest alerts
      // );
      // const fetchedAlerts = response.data as Alert[];
      // setAlerts(fetchedAlerts);
      // console.log('Fetched alerts:', fetchedAlerts);
      // --- END REAL API CALL ---

      // --- MOCK DATA GENERATION (For Demo) ---
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 750));
      const mockAlerts: Alert[] = Array.from({ length: Math.floor(Math.random() * maxAlerts) + 1 }, (_, i) => {
        const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META'];
        const severities: Alert['severity'][] = ['low', 'medium', 'high', 'critical'];
        const ruleNames = [
          'Price Movement Alert', 'RSI Alert', 'Volume Spike',
          'Sentiment Change', 'Moving Average Crossover', 'Earnings Reminder'
        ];
        const severity = severities[Math.floor(Math.random() * severities.length)];
        const symbol = symbols[Math.floor(Math.random() * symbols.length)];
        const ruleName = ruleNames[Math.floor(Math.random() * ruleNames.length)];
        let message = `Mock message for ${symbol} - ${ruleName}`; // Simplified mock message
        const createdDate = new Date();
        createdDate.setMinutes(createdDate.getMinutes() - Math.floor(Math.random() * 120)); // Random time in last 2 hours

        return {
          id: `init_${Date.now() - i * 1000}_${i}`,
          user_id: user.id,
          rule_id: `rule_${Math.floor(Math.random() * 100)}`,
          rule_name: ruleName,
          symbol,
          message,
          severity,
          is_read: Math.random() > 0.7, // 30% chance of being initially read
          created_at: createdDate.toISOString()
        };
      });
       // Sort mock alerts by date, newest first
      mockAlerts.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setAlerts(mockAlerts);
      console.log('Generated mock alerts:', mockAlerts);
      // --- END MOCK DATA ---

    } catch (err: any) {
      console.error('Error fetching alerts:', err);
      setError(`Failed to load alerts. ${err.message || ''}`); // Provide more error context
    } finally {
      setLoading(false); // Ensure loading is set to false in all cases
    }
  }, [user, maxAlerts]); // Dependencies: refetch if user or maxAlerts changes

  /**
   * Shows a browser notification for a new alert.
   * Requests permission if not already granted.
   * Memoized with useCallback.
   */
  const showNotification = useCallback((alert: Alert) => {
    if (!('Notification' in window)) {
      console.warn('Browser does not support notifications.');
      return;
    }

    const notify = () => {
        new Notification(`Aura AI Alert: ${alert.symbol || alert.rule_name}`, {
            body: alert.message,
            icon: '/logo192.png', // Ensure this path is correct relative to your public folder
            tag: alert.id // Use alert ID as tag to prevent duplicate notifications for the same alert
        });
    };

    if (Notification.permission === 'granted') {
      notify();
    } else if (Notification.permission !== 'denied') {
      // Request permission
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          notify();
        }
      });
    }
     // If permission is denied, do nothing.
  }, []); // No dependencies needed for this function


  // --- WebSocket Effect ---
  useEffect(() => {
    if (!user) return; // Don't run effect if no user

    // Fetch initial alerts when component mounts or user/maxAlerts change
    fetchAlerts();

    // Set up WebSocket connection
    const ws = new MockWebSocket(user.id);

    const handleOpen = () => {
      console.log('WebSocket connection established');
    };

    const handleMessage = (event: { data: string }) => {
      try {
        const newAlert = JSON.parse(event.data) as Alert;
        console.log('Received new alert via WebSocket:', newAlert);
        // Add new alert to the beginning of the list, maintaining maxAlerts limit
        setAlerts(prev => [newAlert, ...prev].slice(0, maxAlerts));

        // Show browser notification for the new unread alert
        showNotification(newAlert);
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    const handleError = (event: any) => {
      console.error('WebSocket error:', event);
      setError('Alert service connection issue. Real-time updates may be unavailable.');
    };

    const handleClose = () => {
        console.log('WebSocket connection closed.');
        // Optionally attempt to reconnect here or notify the user
    };

    // Add event listeners
    ws.addEventListener('open', handleOpen);
    ws.addEventListener('message', handleMessage);
    ws.addEventListener('error', handleError);
    ws.addEventListener('close', handleClose);

    // Connect to WebSocket
    ws.connect();

    // Clean up function: disconnect WebSocket when component unmounts or dependencies change
    return () => {
      console.log('Cleaning up WebSocket connection...');
      ws.disconnect();
      // Remove listeners explicitly (good practice though MockWebSocket handles it)
      ws.removeEventListener('open');
      ws.removeEventListener('message');
      ws.removeEventListener('error');
      ws.removeEventListener('close');
    };
    // **FIX:** Added fetchAlerts and showNotification to the dependency array.
    // These functions are defined outside the effect but used inside.
    // They are memoized with useCallback to prevent unnecessary effect runs.
  }, [user, maxAlerts, fetchAlerts, showNotification]);


  /**
   * Marks a specific alert as read.
   * Memoized with useCallback.
   */
  const markAsRead = useCallback(async (alertId: string) => {
    console.log(`Marking alert ${alertId} as read (locally)`);
    // Optimistically update the UI first
    setAlerts(prev => prev.map(alert =>
      alert.id === alertId ? { ...alert, is_read: true } : alert
    ));

    try {
      // --- REAL API CALL (Commented out for demo) ---
      // await axiosInstance.patch(`/api/v1/alerts/${alertId}/mark-as-read`);
      // console.log(`Successfully marked alert ${alertId} as read on server`);
      // --- END REAL API CALL ---

       // Simulate API delay for mock
       await new Promise(resolve => setTimeout(resolve, 300));

    } catch (err) {
      console.error(`Error marking alert ${alertId} as read:`, err);
      // Revert optimistic update on error
      setAlerts(prev => prev.map(alert =>
        alert.id === alertId ? { ...alert, is_read: false } : alert // Revert state
      ));
      // Optionally show an error message to the user
      setError(`Failed to mark alert ${alertId} as read.`);
    }
  }, []); // No external dependencies needed besides setAlerts (implicitly stable)


  /**
   * Marks all currently displayed unread alerts as read.
   * Memoized with useCallback.
   */
  const markAllAsRead = useCallback(async () => {
    const unreadAlerts = alerts.filter(a => !a.is_read);
    const unreadAlertIds = unreadAlerts.map(a => a.id);

    if (unreadAlertIds.length === 0) return; // No unread alerts to mark

    console.log(`Marking ${unreadAlertIds.length} alerts as read (locally)`);

    // Optimistically update UI
    const previousAlerts = alerts; // Store previous state for potential rollback
    setAlerts(prev => prev.map(alert => ({ ...alert, is_read: true })));

    try {
      // --- REAL API CALL (Commented out for demo) ---
      // In a real app, prefer a single bulk update endpoint if available
      // await axiosInstance.post(`/api/v1/alerts/mark-all-as-read`, { user_id: user?.id });
      // Or, if bulk endpoint isn't available:
      // await Promise.all(unreadAlertIds.map(id =>
      //   axiosInstance.patch(`/api/v1/alerts/${id}/mark-as-read`)
      // ));
      // console.log(`Successfully marked ${unreadAlertIds.length} alerts as read on server`);
      // --- END REAL API CALL ---

       // Simulate API delay for mock
       await new Promise(resolve => setTimeout(resolve, 500));

    } catch (err) {
      console.error('Error marking all alerts as read:', err);
      // Revert optimistic update on error
      setAlerts(previousAlerts);
      setError('Failed to mark all alerts as read.'); // Show error message
    }
  }, [alerts]); // Dependency: needs current alerts state to find unread IDs


  // Calculate count of unread alerts
  const unreadCount = alerts.filter(a => !a.is_read).length;

  // --- Render Logic ---

  // Loading state
  if (loading) {
    return <LoadingState>Loading alerts...</LoadingState>;
  }

  // Main component render
  return (
    <Container>
      {/* Header Section */}
      <HeaderRow>
        <Title>Alerts {unreadCount > 0 && `(${unreadCount})`}</Title>
        <div>
          {/* Show "Mark all read" only if there are unread alerts */}
          {unreadCount > 0 && (
            <MarkAllReadButton onClick={markAllAsRead} disabled={unreadCount === 0}>
              Mark all read
            </MarkAllReadButton>
          )}
          {/* Optionally add a "See All" link if needed */}
          {/* <SeeAllLink href="/alerts" style={{ marginLeft: '16px' }}>See all</SeeAllLink> */}
        </div>
      </HeaderRow>

      {/* Error Display */}
      {error && <EmptyState style={{ color: 'red', borderColor: 'red' }}>{error}</EmptyState>}

      {/* Alerts List or Empty State */}
      {!error && alerts.length === 0 ? (
        <EmptyState>You have no recent alerts.</EmptyState>
      ) : (
        <AlertsList>
          {alerts.map(alert => (
            <AlertItem key={alert.id} severity={alert.severity} isRead={alert.is_read}>
              {/* Alert Main Content */}
              <AlertContent>
                <AlertHeader>
                  <AlertTitle>
                    {/* Display symbol if available */}
                    {alert.symbol && <AlertSymbol>[{alert.symbol}]</AlertSymbol>}
                    {alert.rule_name}
                  </AlertTitle>
                  {/* Relative time, pushed to the right */}
                  <AlertTime>{formatRelativeTime(alert.created_at)}</AlertTime>
                </AlertHeader>
                <AlertMessage>{alert.message}</AlertMessage>
              </AlertContent>
              {/* Actions (Mark as Read button) */}
              <AlertActions>
                {!alert.is_read && (
                  <MarkReadButton onClick={() => markAsRead(alert.id)}>
                    Mark read
                  </MarkReadButton>
                )}
              </AlertActions>
            </AlertItem>
          ))}
        </AlertsList>
      )}

      {/* Footer Link (Optional) */}
      {alerts.length > 0 && (
         <HeaderRow style={{ marginTop: '16px', justifyContent: 'flex-end', borderBottom: 'none', paddingBottom: 0 }}>
           <SeeAllLink href="/alerts">See all alerts</SeeAllLink>
         </HeaderRow>
       )}
    </Container>
  );
};

export default AlertsDisplay;

// Example of how to use it (requires styled-components)
// You would typically render this within your App component structure
// const App = () => (
//   <div style={{ maxWidth: '600px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
//     <AlertsDisplay maxAlerts={7} />
//   </div>
// );
// export default App; // If using as a standalone example
 