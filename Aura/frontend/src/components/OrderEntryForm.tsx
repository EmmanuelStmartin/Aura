import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { placeOrder } from '../api/brokerageApi';

// Types
interface OrderFormValues {
  symbol: string;
  qty: number;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop' | 'stop_limit';
  time_in_force: 'day' | 'gtc' | 'ioc' | 'fok';
  limit_price?: number;
  stop_price?: number;
}

interface OrderEntryFormProps {
  initialSymbol?: string;
  onClose?: () => void;
  onSuccess?: (orderResponse: any) => void;
  isModal?: boolean;
}

// Styled Components
const FormContainer = styled.div<{ isModal?: boolean }>`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: ${props => props.isModal ? '0 4px 20px rgba(0, 0, 0, 0.15)' : '0 2px 4px rgba(0, 0, 0, 0.05)'};
  width: ${props => props.isModal ? '500px' : '100%'};
`;

const FormHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const FormTitle = styled.h3`
  font-size: 20px;
  color: #333;
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 20px;
  color: #666;
  cursor: pointer;
  
  &:hover {
    color: #333;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #4a90e2;
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
  }
  
  &:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: #F6465D;
  font-size: 12px;
  margin-top: 4px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
`;

const RadioButton = styled.button<{ active: boolean; variant: 'buy' | 'sell' | 'default' }>`
  flex: 1;
  padding: 10px;
  border: 1px solid ${props => 
    props.active 
      ? props.variant === 'buy' 
        ? '#0ECB81' 
        : props.variant === 'sell' 
          ? '#F6465D' 
          : '#4a90e2'
      : '#ddd'
  };
  border-radius: 4px;
  background: ${props => 
    props.active 
      ? props.variant === 'buy' 
        ? 'rgba(14, 203, 129, 0.1)' 
        : props.variant === 'sell' 
          ? 'rgba(246, 70, 93, 0.1)' 
          : 'rgba(74, 144, 226, 0.1)'
      : 'white'
  };
  color: ${props => 
    props.active 
      ? props.variant === 'buy' 
        ? '#0ECB81' 
        : props.variant === 'sell' 
          ? '#F6465D' 
          : '#4a90e2'
      : '#666'
  };
  cursor: pointer;
  font-weight: ${props => props.active ? '600' : '400'};
  
  &:hover {
    background: ${props => 
      props.variant === 'buy' 
        ? 'rgba(14, 203, 129, 0.05)' 
        : props.variant === 'sell' 
          ? 'rgba(246, 70, 93, 0.05)' 
          : 'rgba(74, 144, 226, 0.05)'
    };
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  background-color: white;
  
  &:focus {
    outline: none;
    border-color: #4a90e2;
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
  }
`;

const SummaryCard = styled.div`
  background: #f7f9fc;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
`;

const SummaryRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
    padding-top: 8px;
    border-top: 1px solid #eee;
    font-weight: 600;
  }
`;

const SummaryLabel = styled.div`
  color: #666;
`;

const SummaryValue = styled.div`
  color: #333;
  font-weight: 500;
`;

const SubmitButton = styled.button<{ variant: 'buy' | 'sell' }>`
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background-color: ${props => props.variant === 'buy' ? '#0ECB81' : '#F6465D'};
  cursor: pointer;
  
  &:hover {
    background-color: ${props => props.variant === 'buy' ? '#0bb974' : '#e03e55'};
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-right: 8px;
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

const ModalOverlay = styled.div`
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

const SuccessMessage = styled.div`
  margin-top: 16px;
  padding: 12px;
  background-color: rgba(14, 203, 129, 0.1);
  border: 1px solid #0ECB81;
  border-radius: 4px;
  color: #0ECB81;
  text-align: center;
`;

const OrderEntryForm: React.FC<OrderEntryFormProps> = ({ 
  initialSymbol = '', 
  onClose, 
  onSuccess,
  isModal = false
}) => {
  // Form state
  const [formValues, setFormValues] = useState<OrderFormValues>({
    symbol: initialSymbol,
    qty: 0,
    side: 'buy',
    type: 'market',
    time_in_force: 'day',
  });
  
  // Validation and UI state
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Mock price for estimation (in a real app, would fetch from API)
  const [estimatedPrice, setEstimatedPrice] = useState<number | null>(null);
  
  // Update symbol if initialSymbol prop changes
  useEffect(() => {
    if (initialSymbol && initialSymbol !== formValues.symbol) {
      setFormValues(prev => ({ ...prev, symbol: initialSymbol }));
      fetchSymbolPrice(initialSymbol);
    }
  }, [initialSymbol]);
  
  // When symbol changes, fetch current price
  useEffect(() => {
    if (formValues.symbol.trim()) {
      fetchSymbolPrice(formValues.symbol);
    } else {
      setEstimatedPrice(null);
    }
  }, [formValues.symbol]);
  
  // Mock function to fetch symbol price (in a real app, would call API)
  const fetchSymbolPrice = (symbol: string) => {
    // Simulate API call with timeout
    setTimeout(() => {
      // Mock prices for some common symbols
      const mockPrices: Record<string, number> = {
        'AAPL': 207.83,
        'MSFT': 417.23,
        'GOOGL': 159.83,
        'AMZN': 186.13,
        'META': 496.17,
        'TSLA': 172.82,
        'NVDA': 894.52,
      };
      
      const price = mockPrices[symbol.toUpperCase()] || 
        (Math.random() * 500 + 50).toFixed(2) as unknown as number;
      
      setEstimatedPrice(price);
    }, 300);
  };
  
  // Handle form field changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // Convert numeric values
    if (name === 'qty' || name === 'limit_price' || name === 'stop_price') {
      const numValue = value === '' ? undefined : parseFloat(value);
      setFormValues(prev => ({ ...prev, [name]: numValue }));
    } else {
      setFormValues(prev => ({ ...prev, [name]: value }));
    }
    
    // Clear error when field is changed
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };
  
  // Handle order type change (radio buttons)
  const handleSideChange = (side: 'buy' | 'sell') => {
    setFormValues(prev => ({ ...prev, side }));
  };
  
  // Handle order type change (dropdown)
  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const type = e.target.value as OrderFormValues['type'];
    
    // Reset price fields when order type changes
    if (type === 'market') {
      setFormValues(prev => ({ 
        ...prev, 
        type,
        limit_price: undefined,
        stop_price: undefined 
      }));
    } else if (type === 'limit') {
      setFormValues(prev => ({ 
        ...prev, 
        type,
        limit_price: estimatedPrice || undefined,
        stop_price: undefined
      }));
    } else if (type === 'stop') {
      setFormValues(prev => ({ 
        ...prev, 
        type,
        limit_price: undefined,
        stop_price: estimatedPrice || undefined
      }));
    } else if (type === 'stop_limit') {
      setFormValues(prev => ({ 
        ...prev, 
        type,
        limit_price: estimatedPrice || undefined,
        stop_price: estimatedPrice || undefined
      }));
    }
  };
  
  // Validate form
  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    // Symbol is required
    if (!formValues.symbol.trim()) {
      newErrors.symbol = 'Symbol is required';
    }
    
    // Quantity is required and must be positive
    if (!formValues.qty) {
      newErrors.qty = 'Quantity is required';
    } else if (formValues.qty <= 0) {
      newErrors.qty = 'Quantity must be greater than 0';
    } else if (!Number.isInteger(formValues.qty)) {
      newErrors.qty = 'Quantity must be a whole number';
    }
    
    // Limit price is required for limit and stop-limit orders
    if ((formValues.type === 'limit' || formValues.type === 'stop_limit') && 
        (!formValues.limit_price || formValues.limit_price <= 0)) {
      newErrors.limit_price = 'Limit price is required and must be greater than 0';
    }
    
    // Stop price is required for stop and stop-limit orders
    if ((formValues.type === 'stop' || formValues.type === 'stop_limit') && 
        (!formValues.stop_price || formValues.stop_price <= 0)) {
      newErrors.stop_price = 'Stop price is required and must be greater than 0';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Calculate estimated cost/proceeds
  const calculateEstimatedValue = () => {
    if (!formValues.qty || !estimatedPrice) return null;
    
    const price = getEstimationPrice();
    return formValues.qty * price;
  };
  
  // Get price for estimation based on order type
  const getEstimationPrice = () => {
    if (!estimatedPrice) return 0;
    
    if (formValues.type === 'limit' && formValues.limit_price) {
      return formValues.limit_price;
    } else if (formValues.type === 'stop' && formValues.stop_price) {
      return formValues.stop_price;
    } else if (formValues.type === 'stop_limit' && formValues.limit_price) {
      return formValues.limit_price;
    }
    
    return estimatedPrice;
  };
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setSuccessMessage(null);
    
    try {
      // Prepare order data
      const orderData = {
        ...formValues,
        qty: Number(formValues.qty), // Ensure quantity is number
      };
      
      // Remove undefined fields
      Object.keys(orderData).forEach((key) => {
        if ((orderData as any)[key] === undefined) {
          delete (orderData as any)[key];
        }
      });
      
      // Submit order
      const response = await placeOrder(orderData);
      
      // Show success message
      setSuccessMessage(`Order placed successfully! Order ID: ${response.id}`);
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess(response);
      }
      
      // Reset form if not in modal (if in modal, user will close it)
      if (!isModal) {
        setFormValues({
          symbol: '',
          qty: 0,
          side: 'buy',
          type: 'market',
          time_in_force: 'day',
        });
      }
    } catch (error) {
      console.error('Error placing order:', error);
      
      // Handle API error
      const errorMessage = error instanceof Error ? error.message : 'Failed to place order. Please try again.';
      setErrors({ submit: errorMessage });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Render form
  const renderForm = () => (
    <form onSubmit={handleSubmit}>
      <FormGroup>
        <Label htmlFor="symbol">Symbol</Label>
        <Input
          id="symbol"
          name="symbol"
          value={formValues.symbol}
          onChange={handleChange}
          placeholder="Enter symbol (e.g., AAPL)"
          disabled={!!initialSymbol}
        />
        {errors.symbol && <ErrorMessage>{errors.symbol}</ErrorMessage>}
      </FormGroup>
      
      <FormGroup>
        <Label>Side</Label>
        <ButtonGroup>
          <RadioButton 
            type="button"
            active={formValues.side === 'buy'} 
            variant="buy"
            onClick={() => handleSideChange('buy')}
          >
            Buy
          </RadioButton>
          <RadioButton 
            type="button"
            active={formValues.side === 'sell'} 
            variant="sell"
            onClick={() => handleSideChange('sell')}
          >
            Sell
          </RadioButton>
        </ButtonGroup>
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="type">Order Type</Label>
        <Select
          id="type"
          name="type"
          value={formValues.type}
          onChange={handleTypeChange}
        >
          <option value="market">Market</option>
          <option value="limit">Limit</option>
          <option value="stop">Stop</option>
          <option value="stop_limit">Stop Limit</option>
        </Select>
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="qty">Quantity</Label>
        <Input
          id="qty"
          name="qty"
          type="number"
          min="1"
          step="1"
          value={formValues.qty || ''}
          onChange={handleChange}
          placeholder="Enter quantity"
        />
        {errors.qty && <ErrorMessage>{errors.qty}</ErrorMessage>}
      </FormGroup>
      
      {(formValues.type === 'limit' || formValues.type === 'stop_limit') && (
        <FormGroup>
          <Label htmlFor="limit_price">Limit Price</Label>
          <Input
            id="limit_price"
            name="limit_price"
            type="number"
            min="0.01"
            step="0.01"
            value={formValues.limit_price || ''}
            onChange={handleChange}
            placeholder="Enter limit price"
          />
          {errors.limit_price && <ErrorMessage>{errors.limit_price}</ErrorMessage>}
        </FormGroup>
      )}
      
      {(formValues.type === 'stop' || formValues.type === 'stop_limit') && (
        <FormGroup>
          <Label htmlFor="stop_price">Stop Price</Label>
          <Input
            id="stop_price"
            name="stop_price"
            type="number"
            min="0.01"
            step="0.01"
            value={formValues.stop_price || ''}
            onChange={handleChange}
            placeholder="Enter stop price"
          />
          {errors.stop_price && <ErrorMessage>{errors.stop_price}</ErrorMessage>}
        </FormGroup>
      )}
      
      <FormGroup>
        <Label htmlFor="time_in_force">Time in Force</Label>
        <Select
          id="time_in_force"
          name="time_in_force"
          value={formValues.time_in_force}
          onChange={handleChange}
        >
          <option value="day">Day</option>
          <option value="gtc">Good Till Canceled</option>
          <option value="ioc">Immediate or Cancel</option>
          <option value="fok">Fill or Kill</option>
        </Select>
      </FormGroup>
      
      {formValues.qty > 0 && estimatedPrice && (
        <SummaryCard>
          <SummaryRow>
            <SummaryLabel>Symbol</SummaryLabel>
            <SummaryValue>{formValues.symbol.toUpperCase()}</SummaryValue>
          </SummaryRow>
          <SummaryRow>
            <SummaryLabel>Order Type</SummaryLabel>
            <SummaryValue>
              {formValues.side.charAt(0).toUpperCase() + formValues.side.slice(1)}{' '}
              {formValues.type.charAt(0).toUpperCase() + formValues.type.slice(1).replace('_', ' ')}
            </SummaryValue>
          </SummaryRow>
          <SummaryRow>
            <SummaryLabel>Quantity</SummaryLabel>
            <SummaryValue>{formValues.qty}</SummaryValue>
          </SummaryRow>
          <SummaryRow>
            <SummaryLabel>Estimated Price</SummaryLabel>
            <SummaryValue>${getEstimationPrice().toFixed(2)}</SummaryValue>
          </SummaryRow>
          <SummaryRow>
            <SummaryLabel>Estimated {formValues.side === 'buy' ? 'Cost' : 'Proceeds'}</SummaryLabel>
            <SummaryValue>${calculateEstimatedValue()?.toFixed(2)}</SummaryValue>
          </SummaryRow>
        </SummaryCard>
      )}
      
      {errors.submit && <ErrorMessage>{errors.submit}</ErrorMessage>}
      
      {successMessage && <SuccessMessage>{successMessage}</SuccessMessage>}
      
      <SubmitButton 
        type="submit" 
        variant={formValues.side} 
        disabled={isSubmitting}
      >
        {isSubmitting && <LoadingSpinner />}
        {isSubmitting ? 'Processing...' : `${formValues.side === 'buy' ? 'Buy' : 'Sell'} ${formValues.symbol.toUpperCase()}`}
      </SubmitButton>
    </form>
  );
  
  // If it's a modal, wrap in modal overlay
  if (isModal) {
    return (
      <ModalOverlay>
        <FormContainer isModal>
          <FormHeader>
            <FormTitle>Place Order</FormTitle>
            {onClose && <CloseButton onClick={onClose}>×</CloseButton>}
          </FormHeader>
          {renderForm()}
        </FormContainer>
      </ModalOverlay>
    );
  }
  
  // Regular component (not modal)
  return (
    <FormContainer>
      <FormHeader>
        <FormTitle>Place Order</FormTitle>
      </FormHeader>
      {renderForm()}
    </FormContainer>
  );
};

export default OrderEntryForm; 