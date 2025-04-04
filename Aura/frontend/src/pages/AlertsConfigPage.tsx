import React, { useState, useEffect, useCallback } from 'react'; // Import useCallback
import styled from 'styled-components';
// Assuming these imports are correct relative to your project structure
import { useAuth } from '../hooks/useAuth';
import axiosInstance from '../api/axiosConfig';
import AlertRuleForm from '../components/AlertRuleForm';
import AlertsList from '../components/AlertsList';

// --- Types ---
interface AlertRule {
  id: string;
  name: string;
  description: string;
  user_id: string;
  symbol?: string; // Optional symbol
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  indicator: string;
  operator: 'gt' | 'lt' | 'gte' | 'lte' | 'eq' | 'neq';
  threshold: number;
  cooldown_minutes: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// --- Styled Components ---
const PageContainer = styled.div`
  padding: 24px;
  font-family: 'Inter', sans-serif; /* Added a default font */
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem; /* 24px */
  margin-bottom: 24px;
  color: #111827; /* Darker gray */
  font-weight: 600;
`;

const ContentContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;

  /* Responsive layout for smaller screens */
  @media (max-width: 992px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1); /* Subtle shadow */
`;

const FormContainer = styled(Card)``; // Inherit base card styles

const RulesContainer = styled(Card)``; // Inherit base card styles

const FormTitle = styled.h3`
  font-size: 1.125rem; /* 18px */
  margin-bottom: 24px;
  color: #374151; /* Medium gray */
  font-weight: 500;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 48px 24px; /* More padding */
  color: #6b7280; /* Lighter gray */
  font-style: italic;
`;

// Base Message Style
const MessageBase = styled.div`
  text-align: center;
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 8px;
  font-size: 0.875rem; /* 14px */
`;

const ErrorMessage = styled(MessageBase)`
  color: #dc2626; /* Red */
  background: #fee2e2; /* Light red */
  border: 1px solid #fca5a5; /* Red border */
`;

const SuccessMessage = styled(MessageBase)`
  color: #059669; /* Green */
  background: #d1fae5; /* Light green */
  border: 1px solid #6ee7b7; /* Green border */
`;

// --- Component ---
const AlertsConfigPage: React.FC = () => {
  // --- State and Hooks ---
  const { user } = useAuth(); // Get user from auth context
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]); // State for alert rules
  const [loading, setLoading] = useState(true); // Loading state for fetching rules
  const [error, setError] = useState<string | null>(null); // Error message state
  const [success, setSuccess] = useState<string | null>(null); // Success message state

  // --- Data Fetching ---
  // Memoized function to fetch alert rules from the API (or mock data)
  const fetchAlertRules = useCallback(async () => {
    // Only fetch if user is available
    if (!user) {
        setLoading(false); // Stop loading if no user
        setError("User not authenticated. Cannot load alert rules."); // Set an error message
        return;
    }

    setLoading(true); // Start loading
    setError(null); // Clear previous errors

    try {
      // --- Real API Call (Example) ---
      // console.log(`Fetching rules for user ID: ${user.id}`);
      // const response = await axiosInstance.get(`/api/v1/alerts/rules?user_id=${user.id}`);
      // setAlertRules(response.data);
      // setLoading(false);
      // --- End Real API Call ---

      // --- Mock Data (For Demo) ---
      // Simulate network delay
      setTimeout(() => {
        const mockAlertRules: AlertRule[] = [
          {
            id: '1',
            name: 'AAPL Price Alert',
            description: 'Alert when Apple stock price moves above $210',
            user_id: user.id,
            symbol: 'AAPL',
            alert_type: 'price_movement',
            severity: 'medium',
            indicator: 'close',
            operator: 'gt',
            threshold: 210,
            cooldown_minutes: 60,
            is_active: true,
            created_at: new Date(Date.now() - 86400000).toISOString(), // Yesterday
            updated_at: new Date().toISOString()
          },
          {
            id: '2',
            name: 'MSFT RSI Alert',
            description: 'Alert when Microsoft RSI goes below 30 (oversold)',
            user_id: user.id,
            symbol: 'MSFT',
            alert_type: 'technical_indicator',
            severity: 'high',
            indicator: 'rsi_14',
            operator: 'lt',
            threshold: 30,
            cooldown_minutes: 240,
            is_active: true,
            created_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
            updated_at: new Date().toISOString()
          },
          {
            id: '3',
            name: 'Market Sentiment',
            description: 'Alert when overall market sentiment becomes negative',
            user_id: user.id,
            // No symbol for market-wide alert
            alert_type: 'sentiment',
            severity: 'critical',
            indicator: 'sentiment_score',
            operator: 'lt',
            threshold: -0.5,
            cooldown_minutes: 1440, // 1 day
            is_active: false, // Example of an inactive rule
            created_at: new Date(Date.now() - 259200000).toISOString(), // 3 days ago
            updated_at: new Date(Date.now() - 86400000).toISOString() // Updated yesterday
          }
        ];
        setAlertRules(mockAlertRules); // Set state with mock data
        setLoading(false); // Stop loading
        console.log('Mock alert rules loaded.');
      }, 800); // 800ms delay
      // --- End Mock Data ---

    } catch (err) {
      console.error('Error fetching alert rules:', err);
      // Provide a more user-friendly error message
      setError('Failed to load your alert rules. Please refresh the page or try again later.');
      setLoading(false); // Stop loading on error
    }
  }, [user]); // Dependency: fetchAlertRules depends on the user object

  // --- Effect Hook ---
  // Fetch alert rules when the component mounts or when fetchAlertRules function changes (due to user changing)
  useEffect(() => {
    fetchAlertRules();
  }, [fetchAlertRules]); // Dependency: Run effect when fetchAlertRules changes

  // --- Helper Function for Clearing Messages ---
  const clearMessages = (delay: number = 5000) => {
      setTimeout(() => {
          setSuccess(null);
          setError(null);
      }, delay);
  };

  // --- Event Handlers ---
  // Handle rule creation
  const handleCreateRule = async (ruleData: Omit<AlertRule, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'is_active'>) => {
    if (!user) {
        setError("Cannot create rule: User not authenticated.");
        return;
    }

    setError(null); // Clear previous messages
    setSuccess(null);
    console.log('Attempting to create rule:', ruleData);

    try {
      // --- Real API Call (Example) ---
      // const response = await axiosInstance.post('/api/v1/alerts/rules', {
      //   ...ruleData,
      //   user_id: user.id,
      //   is_active: true // Default to active on creation
      // });
      // const newRule = response.data;
      // setAlertRules(prev => [...prev, newRule]);
      // setSuccess('Alert rule created successfully!');
      // --- End Real API Call ---

      // --- Mock API Call (For Demo) ---
      const newRule: AlertRule = {
        id: `new_${Date.now()}`, // Simple unique ID for demo
        ...ruleData,
        user_id: user.id,
        is_active: true, // New rules are active by default
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      setAlertRules(prev => [...prev, newRule]); // Add new rule to the start of the list
      setSuccess('Alert rule created successfully!');
      console.log('Mock rule created:', newRule);
      clearMessages(); // Clear success message after delay
      // --- End Mock API Call ---

    } catch (err) {
      console.error('Error creating alert rule:', err);
      setError('Failed to create the alert rule. Please check the details and try again.');
      clearMessages(); // Clear error message after delay
    }
  };

  // Handle rule deletion
  const handleDeleteRule = async (ruleId: string) => {
    setError(null); // Clear previous messages
    setSuccess(null);
    console.log(`Attempting to delete rule ID: ${ruleId}`);

    // Optimistic UI Update (Optional but good UX)
    const originalRules = [...alertRules];
    setAlertRules(prev => prev.filter(rule => rule.id !== ruleId));

    try {
      // --- Real API Call (Example) ---
      // await axiosInstance.delete(`/api/v1/alerts/rules/${ruleId}`);
      // setSuccess('Alert rule deleted successfully!');
      // console.log(`Rule ${ruleId} deleted via API.`);
      // --- End Real API Call ---

      // --- Mock API Call (For Demo) ---
       // Simulate network delay for deletion
      await new Promise(resolve => setTimeout(resolve, 500));
      setSuccess('Alert rule deleted successfully!');
      console.log(`Mock rule ${ruleId} deleted.`);
      clearMessages(); // Clear success message after delay
      // --- End Mock API Call ---

    } catch (err) {
      console.error('Error deleting alert rule:', err);
      setError('Failed to delete the alert rule. Please try again.');
      // Rollback optimistic update on error
      setAlertRules(originalRules);
      clearMessages(); // Clear error message after delay
    }
  };

  // Handle rule update (e.g., toggling active status or editing)
  const handleUpdateRule = async (ruleId: string, updates: Partial<Omit<AlertRule, 'id' | 'user_id' | 'created_at'>>) => {
    setError(null); // Clear previous messages
    setSuccess(null);
    console.log(`Attempting to update rule ID: ${ruleId} with updates:`, updates);

    // Find the original rule for potential rollback
    const originalRule = alertRules.find(rule => rule.id === ruleId);
    if (!originalRule) {
        setError("Rule not found for update.");
        return;
    }
    const originalRules = [...alertRules]; // Keep copy for rollback

    // Optimistic UI Update
    setAlertRules(prev => prev.map(rule =>
      rule.id === ruleId
        ? { ...rule, ...updates, updated_at: new Date().toISOString() } // Apply updates and set new updated_at
        : rule
    ));

    try {
      // --- Real API Call (Example) ---
      // // Don't send user_id, id, or created_at in the PATCH request body
      // const { user_id, id, created_at, ...updatePayload } = updates;
      // await axiosInstance.patch(`/api/v1/alerts/rules/${ruleId}`, {
      //     ...updatePayload,
      //     updated_at: new Date().toISOString() // Ensure server gets the timestamp if needed
      // });
      // setSuccess('Alert rule updated successfully!');
      // console.log(`Rule ${ruleId} updated via API.`);
      // --- End Real API Call ---

      // --- Mock API Call (For Demo) ---
      // Simulate network delay for update
      await new Promise(resolve => setTimeout(resolve, 500));
      setSuccess('Alert rule updated successfully!');
      console.log(`Mock rule ${ruleId} updated.`);
      clearMessages(); // Clear success message after delay
      // --- End Mock API Call ---

    } catch (err) {
      console.error('Error updating alert rule:', err);
      setError('Failed to update the alert rule. Please try again.');
      // Rollback optimistic update on error
      setAlertRules(originalRules);
      clearMessages(); // Clear error message after delay
    }
  };

  // --- Render Logic ---
  return (
    <PageContainer>
      <SectionTitle>Alert Configuration</SectionTitle>

      {/* Display Error and Success Messages */}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {success && <SuccessMessage>{success}</SuccessMessage>}

      {/* Show loading indicator or content */}
      {loading ? (
        <LoadingMessage>Loading your alert rules...</LoadingMessage>
      ) : (
        <ContentContainer>
          {/* Form for creating new rules */}
          <FormContainer>
            <FormTitle>Create New Alert Rule</FormTitle>
            {/* Pass the creation handler to the form component */}
            {/* Ensure AlertRuleForm calls onSubmit with the correct data structure */}
            <AlertRuleForm onSubmit={handleCreateRule} />
          </FormContainer>

          {/* List of existing rules */}
          <RulesContainer>
            <FormTitle>Your Alert Rules ({alertRules.length})</FormTitle>
            {/* Pass rules and handlers to the list component */}
            {/* Ensure AlertsList handles delete/update correctly */}
            <AlertsList
              rules={alertRules}
              onDelete={handleDeleteRule}
              onUpdate={handleUpdateRule} // Pass the update handler
            />
          </RulesContainer>
        </ContentContainer>
      )}
    </PageContainer>
  );
};

export default AlertsConfigPage;

// --- Placeholder Components (if not imported) ---
// These are basic placeholders. Replace with your actual components.

// interface AlertRuleFormProps {
//   onSubmit: (data: Omit<AlertRule, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'is_active'>) => void;
// }
// const AlertRuleForm: React.FC<AlertRuleFormProps> = ({ onSubmit }) => {
//   // Basic form structure - replace with your actual form fields
//   const handleSubmit = (e: React.FormEvent) => {
//       e.preventDefault();
//       // Dummy data - collect actual data from form inputs
//       const formData = {
//           name: 'Test Rule from Form',
//           description: 'A test rule.',
//           symbol: 'TEST',
//           alert_type: 'price_movement',
//           severity: 'low' as const,
//           indicator: 'close',
//           operator: 'gt' as const,
//           threshold: 100,
//           cooldown_minutes: 15,
//       };
//       onSubmit(formData);
//   };
//   return <form onSubmit={handleSubmit}><button type="submit">Create Mock Rule</button></form>;
// };

// interface AlertsListProps {
//   rules: AlertRule[];
//   onDelete: (ruleId: string) => void;
//   onUpdate: (ruleId: string, updates: Partial<AlertRule>) => void;
// }
// const AlertsList: React.FC<AlertsListProps> = ({ rules, onDelete, onUpdate }) => {
//   if (rules.length === 0) {
//       return <div>You have no active alert rules.</div>;
//   }
//   return (
//       <ul>
//           {rules.map(rule => (
//               <li key={rule.id} style={{ marginBottom: '10px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
//                   <strong>{rule.name}</strong> ({rule.symbol || 'N/A'}) - Active: {rule.is_active ? 'Yes' : 'No'}
//                   <button onClick={() => onDelete(rule.id)} style={{ marginLeft: '10px' }}>Delete</button>
//                   <button onClick={() => onUpdate(rule.id, { is_active: !rule.is_active })} style={{ marginLeft: '5px' }}>
//                       Toggle Active
//                   </button>
//               </li>
//           ))}
//       </ul>
//   );
// };

// interface AuthContextType {
//  user: { id: string; name: string } | null;
// }
// const useAuth = (): AuthContextType => {
//  // Mock implementation for context hook
//  return { user: { id: 'user123', name: 'Demo User' } };
// };

// const axiosInstance = { // Mock axios instance
//  get: (url: string) => Promise.resolve({ data: [] }), // Mock GET
//  post: (url: string, data: any) => Promise.resolve({ data: { ...data, id: `post_${Date.now()}` } }), // Mock POST
//  delete: (url: string) => Promise.resolve(), // Mock DELETE
//  patch: (url: string, data: any) => Promise.resolve({ data: { ...data, id: url.split('/').pop() } }), // Mock PATCH
// };

