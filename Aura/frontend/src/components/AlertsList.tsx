import React, { useState } from 'react';
import styled from 'styled-components';
import AlertRuleForm from './AlertRuleForm';

// Types
interface AlertRule {
  id: string;
  name: string;
  description: string;
  user_id: string;
  symbol?: string;
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

interface AlertsListProps {
  rules: AlertRule[];
  onDelete: (ruleId: string) => void;
  onUpdate: (ruleId: string, updates: Partial<AlertRule>) => void;
}

// Styled Components
const ListContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f9f9f9;
  border-radius: 4px;
`;

const AlertCard = styled.div`
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
`;

const AlertHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #eee;
`;

const AlertTitle = styled.h4`
  margin: 0;
  font-size: 16px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const AlertActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: #4a90e2;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    text-decoration: underline;
  }
  
  &.delete {
    color: #F6465D;
  }
  
  &.toggle {
    color: ${props => props.color || '#4a90e2'};
  }
`;

const AlertBody = styled.div`
  padding: 16px;
`;

const AlertDetail = styled.div`
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const DetailLabel = styled.span`
  font-weight: 500;
  color: #555;
  margin-right: 8px;
`;

const DetailValue = styled.span`
  color: #333;
`;

const SeverityBadge = styled.span<{ severity: string }>`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  background-color: ${props => {
    switch (props.severity) {
      case 'low': return '#85C1E9';
      case 'medium': return '#F4D03F';
      case 'high': return '#E67E22';
      case 'critical': return '#F6465D';
      default: return '#85C1E9';
    }
  }};
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const ModalTitle = styled.h3`
  margin: 0;
  font-size: 20px;
  color: #333;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  line-height: 1;
  
  &:hover {
    color: #333;
  }
`;

const ConfirmModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ConfirmContent = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  text-align: center;
`;

const ConfirmText = styled.p`
  margin-bottom: 24px;
  font-size: 16px;
  color: #333;
`;

const ConfirmButtons = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
`;

const CancelButton = styled.button`
  padding: 10px 20px;
  background-color: #f1f1f1;
  border: none;
  border-radius: 4px;
  color: #333;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    background-color: #e1e1e1;
  }
`;

const DeleteButton = styled.button`
  padding: 10px 20px;
  background-color: #F6465D;
  border: none;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    background-color: #e03e55;
  }
`;

// Helper function to format operator for display
const formatOperator = (operator: string): string => {
  switch (operator) {
    case 'gt': return '>';
    case 'lt': return '<';
    case 'gte': return '≥';
    case 'lte': return '≤';
    case 'eq': return '=';
    case 'neq': return '≠';
    default: return operator;
  }
};

// Helper function to format alert type for display
const formatAlertType = (type: string): string => {
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Helper function to format indicator for display
const formatIndicator = (indicator: string): string => {
  const mapping: Record<string, string> = {
    'open': 'Open Price',
    'high': 'High Price',
    'low': 'Low Price',
    'close': 'Close Price',
    'volume': 'Volume',
    'rsi_14': 'RSI (14)',
    'macd': 'MACD',
    'ema_9': 'EMA (9)',
    'ema_20': 'EMA (20)',
    'sma_50': 'SMA (50)',
    'sma_200': 'SMA (200)',
    'bollinger_upper': 'Bollinger Upper Band',
    'bollinger_lower': 'Bollinger Lower Band',
    'sentiment_score': 'Sentiment Score',
    'social_volume': 'Social Media Volume',
    'news_sentiment': 'News Sentiment'
  };
  
  return mapping[indicator] || indicator;
};

const AlertsList: React.FC<AlertsListProps> = ({ rules, onDelete, onUpdate }) => {
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deletingRuleId, setDeletingRuleId] = useState<string | null>(null);
  
  // Handle edit button click
  const handleEditClick = (rule: AlertRule) => {
    setEditingRule(rule);
    setShowEditModal(true);
  };
  
  // Handle rule update submission
  const handleUpdateSubmit = (values: Omit<AlertRule, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'is_active'>) => {
    if (!editingRule) return;
    
    onUpdate(editingRule.id, values);
    setShowEditModal(false);
    setEditingRule(null);
  };
  
  // Handle toggle active state
  const handleToggleActive = (rule: AlertRule) => {
    onUpdate(rule.id, { is_active: !rule.is_active });
  };
  
  // Handle delete confirmation
  const handleDeleteConfirm = () => {
    if (deletingRuleId) {
      onDelete(deletingRuleId);
      setDeletingRuleId(null);
    }
  };
  
  // Render edit modal
  const renderEditModal = () => {
    if (!editingRule || !showEditModal) return null;
    
    return (
      <Modal>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>Edit Alert Rule</ModalTitle>
            <CloseButton onClick={() => setShowEditModal(false)}>×</CloseButton>
          </ModalHeader>
          <AlertRuleForm
            initialValues={{
              name: editingRule.name,
              description: editingRule.description,
              symbol: editingRule.symbol,
              alert_type: editingRule.alert_type,
              severity: editingRule.severity,
              indicator: editingRule.indicator,
              operator: editingRule.operator,
              threshold: editingRule.threshold,
              cooldown_minutes: editingRule.cooldown_minutes
            }}
            onSubmit={handleUpdateSubmit}
            submitLabel="Update Alert Rule"
          />
        </ModalContent>
      </Modal>
    );
  };
  
  // Render delete confirmation modal
  const renderDeleteModal = () => {
    if (!deletingRuleId) return null;
    
    const rule = rules.find(r => r.id === deletingRuleId);
    if (!rule) return null;
    
    return (
      <ConfirmModal>
        <ConfirmContent>
          <ConfirmText>
            Are you sure you want to delete the alert rule "{rule.name}"? This action cannot be undone.
          </ConfirmText>
          <ConfirmButtons>
            <CancelButton onClick={() => setDeletingRuleId(null)}>
              Cancel
            </CancelButton>
            <DeleteButton onClick={handleDeleteConfirm}>
              Delete
            </DeleteButton>
          </ConfirmButtons>
        </ConfirmContent>
      </ConfirmModal>
    );
  };
  
  // If no rules available
  if (rules.length === 0) {
    return (
      <EmptyState>
        No alert rules found. Create your first alert rule.
      </EmptyState>
    );
  }
  
  return (
    <ListContainer>
      {rules.map(rule => (
        <AlertCard key={rule.id}>
          <AlertHeader>
            <AlertTitle>
              {rule.symbol && <span>[{rule.symbol}]</span>}
              {rule.name}
              <SeverityBadge severity={rule.severity}>
                {rule.severity.toUpperCase()}
              </SeverityBadge>
            </AlertTitle>
            <AlertActions>
              <ActionButton 
                className="toggle"
                color={rule.is_active ? '#0ECB81' : '#F6465D'}
                onClick={() => handleToggleActive(rule)}
              >
                {rule.is_active ? 'Active' : 'Inactive'}
              </ActionButton>
              <ActionButton onClick={() => handleEditClick(rule)}>
                Edit
              </ActionButton>
              <ActionButton 
                className="delete"
                onClick={() => setDeletingRuleId(rule.id)}
              >
                Delete
              </ActionButton>
            </AlertActions>
          </AlertHeader>
          <AlertBody>
            {rule.description && (
              <AlertDetail>
                <DetailValue>{rule.description}</DetailValue>
              </AlertDetail>
            )}
            <AlertDetail>
              <DetailLabel>Type:</DetailLabel>
              <DetailValue>{formatAlertType(rule.alert_type)}</DetailValue>
            </AlertDetail>
            <AlertDetail>
              <DetailLabel>Condition:</DetailLabel>
              <DetailValue>
                {formatIndicator(rule.indicator)} {formatOperator(rule.operator)} {rule.threshold}
              </DetailValue>
            </AlertDetail>
            <AlertDetail>
              <DetailLabel>Cooldown:</DetailLabel>
              <DetailValue>
                {rule.cooldown_minutes} minute{rule.cooldown_minutes !== 1 ? 's' : ''}
              </DetailValue>
            </AlertDetail>
          </AlertBody>
        </AlertCard>
      ))}
      
      {renderEditModal()}
      {renderDeleteModal()}
    </ListContainer>
  );
};

export default AlertsList; 