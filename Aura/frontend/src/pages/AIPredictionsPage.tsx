import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axiosInstance from '../api/axiosConfig';

// Types
interface MarketPrediction {
  symbol: string;
  prediction: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  forecast_period: string;
  forecast_target: number;
  current_price: number;
  potential_change: number;
  reasoning: string;
  timestamp: string;
}

interface SentimentPrediction {
  symbol?: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  score: number;
  source: string;
  key_phrases: string[];
  timestamp: string;
}

// Styled Components
const PageContainer = styled.div`
  padding: 24px;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  margin-bottom: 24px;
  color: #333;
`;

const ContentContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  
  @media (max-width: 992px) {
    grid-template-columns: 1fr;
  }
`;

const SectionContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
`;

const SubTitle = styled.h3`
  font-size: 18px;
  margin-bottom: 16px;
  color: #333;
`;

const Card = styled.div`
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
`;

const CardHeader = styled.div<{ prediction?: string; sentiment?: string }>`
  padding: 16px;
  background: ${props => {
    if (props.prediction) {
      switch (props.prediction) {
        case 'bullish': return 'rgba(14, 203, 129, 0.1)';
        case 'bearish': return 'rgba(246, 70, 93, 0.1)';
        case 'neutral': return 'rgba(74, 144, 226, 0.1)';
        default: return '#f5f7fa';
      }
    }
    if (props.sentiment) {
      switch (props.sentiment) {
        case 'positive': return 'rgba(14, 203, 129, 0.1)';
        case 'negative': return 'rgba(246, 70, 93, 0.1)';
        case 'neutral': return 'rgba(74, 144, 226, 0.1)';
        default: return '#f5f7fa';
      }
    }
    return '#f5f7fa';
  }};
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CardHeaderTitle = styled.div`
  font-weight: 600;
  font-size: 16px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CardHeaderSubtitle = styled.div`
  font-size: 14px;
  color: #666;
`;

const PredictionBadge = styled.span<{ prediction: string }>`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  background-color: ${props => {
    switch (props.prediction) {
      case 'bullish': return '#0ECB81';
      case 'bearish': return '#F6465D';
      case 'neutral': return '#4a90e2';
      default: return '#4a90e2';
    }
  }};
`;

const SentimentBadge = styled.span<{ sentiment: string }>`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  background-color: ${props => {
    switch (props.sentiment) {
      case 'positive': return '#0ECB81';
      case 'negative': return '#F6465D';
      case 'neutral': return '#4a90e2';
      default: return '#4a90e2';
    }
  }};
`;

const ConfidenceBar = styled.div<{ confidence: number; type: string }>`
  height: 6px;
  width: 100%;
  background: #eee;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 8px;
  
  &::after {
    content: '';
    display: block;
    height: 100%;
    width: ${props => props.confidence}%;
    background-color: ${props => {
      if (props.type === 'market') {
        return '#4a90e2';
      }
      if (props.type === 'sentiment') {
        return props.confidence > 65 ? '#0ECB81' : 
               props.confidence > 35 ? '#4a90e2' : '#F6465D';
      }
      return '#4a90e2';
    }};
  }
`;

const ConfidenceLabel = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  display: flex;
  justify-content: space-between;
`;

const CardBody = styled.div`
  padding: 16px;
`;

const MetricRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const MetricLabel = styled.div`
  font-size: 14px;
  color: #666;
`;

const MetricValue = styled.div<{ isPositive?: boolean }>`
  font-size: 14px;
  font-weight: 500;
  color: ${props => props.isPositive === undefined ? '#333' : 
    props.isPositive ? '#0ECB81' : '#F6465D'};
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 24px;
  color: #666;
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: 16px;
  margin-bottom: 16px;
  color: #F6465D;
  background: #FFF0F0;
  border-radius: 8px;
`;

const KeyPhrasesList = styled.ul`
  margin: 8px 0 0;
  padding-left: 20px;
  
  li {
    margin-bottom: 4px;
    font-size: 14px;
  }
`;

const SearchContainer = styled.div`
  margin-bottom: 24px;
`;

const SearchInput = styled.input`
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #ddd;
  width: 300px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #4a90e2;
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
  }
`;

// Format date
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

const AIPredictionsPage: React.FC = () => {
  const [marketPredictions, setMarketPredictions] = useState<MarketPrediction[]>([]);
  const [sentimentPredictions, setSentimentPredictions] = useState<SentimentPrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Fetch predictions on component mount
  useEffect(() => {
    fetchPredictions();
  }, []);
  
  // Fetch predictions from API
  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, these would be actual API calls
      // const [marketResponse, sentimentResponse] = await Promise.all([
      //   axiosInstance.post('/api/v1/predict/market-movement', { symbols: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'] }),
      //   axiosInstance.post('/api/v1/predict/sentiment', { symbols: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'] })
      // ]);
      // 
      // setMarketPredictions(marketResponse.data);
      // setSentimentPredictions(sentimentResponse.data);
      
      // For demo, use mock data
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
      
      const mockMarketPredictions: MarketPrediction[] = [
        {
          symbol: 'AAPL',
          prediction: 'bullish',
          confidence: 78,
          forecast_period: '1 week',
          forecast_target: 215.50,
          current_price: 207.83,
          potential_change: 3.69,
          reasoning: 'Strong product cycle, services growth, and share repurchases support stock price.',
          timestamp: new Date().toISOString()
        },
        {
          symbol: 'MSFT',
          prediction: 'bullish',
          confidence: 82,
          forecast_period: '1 week',
          forecast_target: 430.00,
          current_price: 417.23,
          potential_change: 3.06,
          reasoning: 'Cloud business growth and AI initiatives continue to drive revenue and margin expansion.',
          timestamp: new Date().toISOString()
        },
        {
          symbol: 'GOOGL',
          prediction: 'neutral',
          confidence: 56,
          forecast_period: '1 week',
          forecast_target: 161.25,
          current_price: 159.83,
          potential_change: 0.89,
          reasoning: 'Advertising business stable but regulatory headwinds create uncertainty.',
          timestamp: new Date().toISOString()
        },
        {
          symbol: 'AMZN',
          prediction: 'bullish',
          confidence: 74,
          forecast_period: '1 week',
          forecast_target: 193.50,
          current_price: 186.13,
          potential_change: 3.96,
          reasoning: 'Retail growth rebounding and AWS shows strong momentum with AI workloads.',
          timestamp: new Date().toISOString()
        },
        {
          symbol: 'TSLA',
          prediction: 'bearish',
          confidence: 65,
          forecast_period: '1 week',
          forecast_target: 165.20,
          current_price: 172.82,
          potential_change: -4.41,
          reasoning: 'Production challenges and price competition in EV market affecting margins.',
          timestamp: new Date().toISOString()
        }
      ];
      
      const mockSentimentPredictions: SentimentPrediction[] = [
        {
          symbol: 'AAPL',
          sentiment: 'positive',
          score: 0.72,
          source: 'news_and_social',
          key_phrases: [
            'iPhone sales exceed expectations',
            'Services revenue growth accelerates',
            'New product announcements planned'
          ],
          timestamp: new Date().toISOString()
        },
        {
          symbol: 'MSFT',
          sentiment: 'positive',
          score: 0.85,
          source: 'news_and_social',
          key_phrases: [
            'Cloud business outperforms competitors',
            'AI integration drives new customer adoption',
            'Strong enterprise demand for Microsoft products'
          ],
          timestamp: new Date().toISOString()
        },
        {
          symbol: 'GOOGL',
          sentiment: 'neutral',
          score: 0.48,
          source: 'news_and_social',
          key_phrases: [
            'Ad revenue stable but growth slowing',
            'Regulatory concerns remain a focus',
            'New AI products showing promise'
          ],
          timestamp: new Date().toISOString()
        },
        {
          symbol: 'AMZN',
          sentiment: 'positive',
          score: 0.68,
          source: 'news_and_social',
          key_phrases: [
            'E-commerce growth returning',
            'AWS winning large enterprise contracts',
            'Logistics improvements reducing costs'
          ],
          timestamp: new Date().toISOString()
        },
        {
          symbol: 'TSLA',
          sentiment: 'negative',
          score: 0.35,
          source: 'news_and_social',
          key_phrases: [
            'Production concerns in key markets',
            'Competition intensifying in EV space',
            'Demand uncertainty in China'
          ],
          timestamp: new Date().toISOString()
        },
        {
          sentiment: 'neutral',
          score: 0.52,
          source: 'news_and_social',
          key_phrases: [
            'Market volatility expected to continue',
            'Federal Reserve policy uncertainty',
            'Earnings season showing mixed results'
          ],
          timestamp: new Date().toISOString()
        }
      ];
      
      setMarketPredictions(mockMarketPredictions);
      setSentimentPredictions(mockSentimentPredictions);
    } catch (err) {
      console.error('Error fetching predictions:', err);
      setError('Failed to load AI predictions. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle search
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };
  
  // Filter predictions based on search query
  const filteredMarketPredictions = searchQuery
    ? marketPredictions.filter(pred => 
        pred.symbol.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : marketPredictions;
    
  const filteredSentimentPredictions = searchQuery
    ? sentimentPredictions.filter(pred => 
        pred.symbol?.toLowerCase().includes(searchQuery.toLowerCase()) || !pred.symbol
      )
    : sentimentPredictions;
  
  if (loading) {
    return <LoadingMessage>Loading AI predictions...</LoadingMessage>;
  }
  
  return (
    <PageContainer>
      <SectionTitle>AI Market Insights</SectionTitle>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <SearchContainer>
        <SearchInput
          type="text"
          placeholder="Filter by symbol (e.g., AAPL)"
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </SearchContainer>
      
      <ContentContainer>
        <SectionContainer>
          <SubTitle>Market Movement Predictions</SubTitle>
          
          {filteredMarketPredictions.length === 0 ? (
            <p>No market predictions found for "{searchQuery}"</p>
          ) : (
            filteredMarketPredictions.map(prediction => (
              <Card key={prediction.symbol}>
                <CardHeader prediction={prediction.prediction}>
                  <CardHeaderTitle>
                    {prediction.symbol}
                    <PredictionBadge prediction={prediction.prediction}>
                      {prediction.prediction.toUpperCase()}
                    </PredictionBadge>
                  </CardHeaderTitle>
                  <CardHeaderSubtitle>
                    {formatDate(prediction.timestamp)}
                  </CardHeaderSubtitle>
                </CardHeader>
                <CardBody>
                  <MetricRow>
                    <MetricLabel>Forecast Period</MetricLabel>
                    <MetricValue>{prediction.forecast_period}</MetricValue>
                  </MetricRow>
                  <MetricRow>
                    <MetricLabel>Current Price</MetricLabel>
                    <MetricValue>${prediction.current_price.toFixed(2)}</MetricValue>
                  </MetricRow>
                  <MetricRow>
                    <MetricLabel>Target Price</MetricLabel>
                    <MetricValue isPositive={prediction.potential_change >= 0}>
                      ${prediction.forecast_target.toFixed(2)}
                    </MetricValue>
                  </MetricRow>
                  <MetricRow>
                    <MetricLabel>Potential Change</MetricLabel>
                    <MetricValue isPositive={prediction.potential_change >= 0}>
                      {prediction.potential_change >= 0 ? '+' : ''}
                      {prediction.potential_change.toFixed(2)}%
                    </MetricValue>
                  </MetricRow>
                  <MetricRow>
                    <MetricLabel>Reasoning</MetricLabel>
                    <MetricValue>{prediction.reasoning}</MetricValue>
                  </MetricRow>
                  
                  <ConfidenceBar confidence={prediction.confidence} type="market" />
                  <ConfidenceLabel>
                    <div>Confidence</div>
                    <div>{prediction.confidence}%</div>
                  </ConfidenceLabel>
                </CardBody>
              </Card>
            ))
          )}
        </SectionContainer>
        
        <SectionContainer>
          <SubTitle>Sentiment Analysis</SubTitle>
          
          {filteredSentimentPredictions.length === 0 ? (
            <p>No sentiment predictions found for "{searchQuery}"</p>
          ) : (
            filteredSentimentPredictions.map((prediction, index) => (
              <Card key={prediction.symbol || `market-${index}`}>
                <CardHeader sentiment={prediction.sentiment}>
                  <CardHeaderTitle>
                    {prediction.symbol || 'Market Wide'}
                    <SentimentBadge sentiment={prediction.sentiment}>
                      {prediction.sentiment.toUpperCase()}
                    </SentimentBadge>
                  </CardHeaderTitle>
                  <CardHeaderSubtitle>
                    {formatDate(prediction.timestamp)}
                  </CardHeaderSubtitle>
                </CardHeader>
                <CardBody>
                  <MetricRow>
                    <MetricLabel>Source</MetricLabel>
                    <MetricValue>
                      {prediction.source === 'news_and_social' 
                        ? 'News & Social Media' 
                        : prediction.source}
                    </MetricValue>
                  </MetricRow>
                  
                  <ConfidenceBar 
                    confidence={prediction.score * 100} 
                    type="sentiment" 
                  />
                  <ConfidenceLabel>
                    <div>Sentiment Score</div>
                    <div>{(prediction.score * 100).toFixed(0)}%</div>
                  </ConfidenceLabel>
                  
                  <MetricRow>
                    <MetricLabel>Key Insights</MetricLabel>
                  </MetricRow>
                  <KeyPhrasesList>
                    {prediction.key_phrases.map((phrase, idx) => (
                      <li key={idx}>{phrase}</li>
                    ))}
                  </KeyPhrasesList>
                </CardBody>
              </Card>
            ))
          )}
        </SectionContainer>
      </ContentContainer>
    </PageContainer>
  );
};

export default AIPredictionsPage; 