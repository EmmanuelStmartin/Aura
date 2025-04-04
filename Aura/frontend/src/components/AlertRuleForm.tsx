import React, { useState } from 'react';
import styled from 'styled-components';

// Types
interface AlertRuleFormValues {
  name: string;
  description: string;
  symbol?: string;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  indicator: string;
  operator: 'gt' | 'lt' | 'gte' | 'lte' | 'eq' | 'neq';
  threshold: number;
  cooldown_minutes: number;
}

interface AlertRuleFormProps {
  initialValues?: Partial<AlertRuleFormValues>;
  onSubmit: (values: AlertRuleFormValues) => void;
  submitLabel?: string;
}

// Styled Components
const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  font-size: 14px;
  color: #555;
  margin-bottom: 6px;
`;

const Input = styled.input`
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #4a90e2;
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
  }
`;

const Textarea = styled.textarea`
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  
  &:focus {
    outline: none;
    border-color: #4a90e2;
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
  }
`;

const Select = styled.select`
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
  
  &:focus {
    outline: none;
    border-color: #4a90e2;
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
  }
`;

const SubmitButton = styled.button`
  padding: 12px;
  background-color: #4a90e2;
  border: none;
  border-radius: 4px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
  
  &:hover {
    background-color: #3a7bc8;
  }
  
  &:disabled {
    background-color: #b3b3b3;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: #F6465D;
  font-size: 12px;
  margin-top: 4px;
`;

const Hint = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 4px;
`;

const AlertRuleForm: React.FC<AlertRuleFormProps> = ({ 
  initialValues, 
  onSubmit,
  submitLabel = 'Create Alert Rule'
}) => {
  const [values, setValues] = useState<AlertRuleFormValues>({
    name: initialValues?.name || '',
    description: initialValues?.description || '',
    symbol: initialValues?.symbol || '',
    alert_type: initialValues?.alert_type || 'price_movement',
    severity: initialValues?.severity || 'medium',
    indicator: initialValues?.indicator || 'close',
    operator: initialValues?.operator || 'gt',
    threshold: initialValues?.threshold || 0,
    cooldown_minutes: initialValues?.cooldown_minutes || 60
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof AlertRuleFormValues, string>>>({});
  
  // Handle form field changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    if (name === 'threshold' || name === 'cooldown_minutes') {
      setValues(prev => ({ ...prev, [name]: parseFloat(value) }));
    } else {
      setValues(prev => ({ ...prev, [name]: value }));
    }
    
    // Clear error when field is changed
    if (errors[name as keyof AlertRuleFormValues]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };
  
  // Get indicator options based on alert type
  const getIndicatorOptions = () => {
    switch (values.alert_type) {
      case 'price_movement':
        return [
          { value: 'open', label: 'Open Price' },
          { value: 'high', label: 'High Price' },
          { value: 'low', label: 'Low Price' },
          { value: 'close', label: 'Close Price' },
          { value: 'volume', label: 'Volume' }
        ];
      case 'technical_indicator':
        return [
          { value: 'rsi_14', label: 'RSI (14)' },
          { value: 'macd', label: 'MACD' },
          { value: 'ema_9', label: 'EMA (9)' },
          { value: 'ema_20', label: 'EMA (20)' },
          { value: 'sma_50', label: 'SMA (50)' },
          { value: 'sma_200', label: 'SMA (200)' },
          { value: 'bollinger_upper', label: 'Bollinger Band (Upper)' },
          { value: 'bollinger_lower', label: 'Bollinger Band (Lower)' }
        ];
      case 'sentiment':
        return [
          { value: 'sentiment_score', label: 'Sentiment Score' },
          { value: 'social_volume', label: 'Social Media Volume' },
          { value: 'news_sentiment', label: 'News Sentiment' }
        ];
      default:
        return [];
    }
  };
  
  // Get threshold hint based on indicator
  const getThresholdHint = () => {
    switch (values.indicator) {
      case 'rsi_14':
        return 'Typical values: 30 (oversold), 70 (overbought)';
      case 'sentiment_score':
        return 'Range: -1.0 (negative) to 1.0 (positive)';
      default:
        return '';
    }
  };
  
  // Validate form
  const validateForm = () => {
    const newErrors: Partial<Record<keyof AlertRuleFormValues, string>> = {};
    
    if (!values.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (values.alert_type === 'price_movement' && !values.symbol?.trim()) {
      newErrors.symbol = 'Symbol is required for price movement alerts';
    }
    
    if (values.alert_type === 'technical_indicator' && !values.symbol?.trim()) {
      newErrors.symbol = 'Symbol is required for technical indicator alerts';
    }
    
    if (values.cooldown_minutes < 1) {
      newErrors.cooldown_minutes = 'Cooldown must be at least 1 minute';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    // Filter out empty symbol if not needed
    const submitValues = { ...values };
    if (!submitValues.symbol?.trim()) {
      delete submitValues.symbol;
    }
    
    onSubmit(submitValues as AlertRuleFormValues);
  };
  
  // Whether symbol is required based on alert type
  const isSymbolRequired = values.alert_type === 'price_movement' || values.alert_type === 'technical_indicator';
  
  return (
    <Form onSubmit={handleSubmit}>
      <FormGroup>
        <Label htmlFor="name">Alert Name *</Label>
        <Input
          id="name"
          name="name"
          value={values.name}
          onChange={handleChange}
          placeholder="E.g., AAPL Price Alert"
        />
        {errors.name && <ErrorMessage>{errors.name}</ErrorMessage>}
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          name="description"
          value={values.description}
          onChange={handleChange}
          placeholder="Describe what this alert is for"
        />
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="alert_type">Alert Type *</Label>
        <Select
          id="alert_type"
          name="alert_type"
          value={values.alert_type}
          onChange={handleChange}
        >
          <option value="price_movement">Price Movement</option>
          <option value="technical_indicator">Technical Indicator</option>
          <option value="sentiment">Market Sentiment</option>
        </Select>
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="symbol">{isSymbolRequired ? 'Symbol *' : 'Symbol (Optional)'}</Label>
        <Input
          id="symbol"
          name="symbol"
          value={values.symbol}
          onChange={handleChange}
          placeholder="E.g., AAPL, MSFT"
        />
        {errors.symbol && <ErrorMessage>{errors.symbol}</ErrorMessage>}
        {!isSymbolRequired && (
          <Hint>Leave blank for market-wide alerts</Hint>
        )}
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="severity">Severity *</Label>
        <Select
          id="severity"
          name="severity"
          value={values.severity}
          onChange={handleChange}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </Select>
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="indicator">Indicator *</Label>
        <Select
          id="indicator"
          name="indicator"
          value={values.indicator}
          onChange={handleChange}
        >
          {getIndicatorOptions().map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="operator">Condition *</Label>
        <Select
          id="operator"
          name="operator"
          value={values.operator}
          onChange={handleChange}
        >
          <option value="gt">Greater Than (&gt;)</option>
          <option value="lt">Less Than (&lt;)</option>
          <option value="gte">Greater Than or Equal (&gt;=)</option>
          <option value="lte">Less Than or Equal (&lt;=)</option>
          <option value="eq">Equal To (=)</option>
          <option value="neq">Not Equal To (≠)</option>
        </Select>
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="threshold">Threshold *</Label>
        <Input
          id="threshold"
          name="threshold"
          type="number"
          step="any"
          value={values.threshold}
          onChange={handleChange}
        />
        {getThresholdHint() && <Hint>{getThresholdHint()}</Hint>}
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="cooldown_minutes">Cooldown (minutes) *</Label>
        <Input
          id="cooldown_minutes"
          name="cooldown_minutes"
          type="number"
          min="1"
          step="1"
          value={values.cooldown_minutes}
          onChange={handleChange}
        />
        {errors.cooldown_minutes && <ErrorMessage>{errors.cooldown_minutes}</ErrorMessage>}
        <Hint>Minimum time between alerts</Hint>
      </FormGroup>
      
      <SubmitButton type="submit">{submitLabel}</SubmitButton>
    </Form>
  );
};

export default AlertRuleForm; 