import React, { useState } from 'react';
import styled from 'styled-components';
import { useSearchParams } from 'react-router-dom';
import OrderEntryForm from '../components/OrderEntryForm';
import MainLayout from '../components/MainLayout';

// Styled Components
const FormContainer = styled.div`
  max-width: 600px;
  margin: 0 auto;
`;

const SuccessMessage = styled.div`
  margin-top: 24px;
  padding: 16px;
  background-color: rgba(14, 203, 129, 0.1);
  border: 1px solid #0ECB81;
  border-radius: 8px;
  color: #0ECB81;
  text-align: center;
`;

const OrderPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialSymbol = searchParams.get('symbol') || '';
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [orderDetails, setOrderDetails] = useState<any>(null);

  const handleOrderSuccess = (orderResponse: any) => {
    setOrderPlaced(true);
    setOrderDetails(orderResponse);
  };

  return (
    <MainLayout title="Place Order">
      <FormContainer>
        <OrderEntryForm 
          initialSymbol={initialSymbol}
          onSuccess={handleOrderSuccess}
        />
        
        {orderPlaced && orderDetails && (
          <SuccessMessage>
            Order placed successfully! Your order for {orderDetails.symbol} is now {orderDetails.status}.
          </SuccessMessage>
        )}
      </FormContainer>
    </MainLayout>
  );
};

export default OrderPage; 