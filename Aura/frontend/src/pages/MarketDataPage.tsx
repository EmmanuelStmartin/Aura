import React, { useState } from 'react';
// Removed unused 'useEffect' import as it wasn't used.
// Removed unused 'axiosInstance' import as API calls were commented out.
import styled from 'styled-components';

// --- Types ---

// Asset interface defines the structure for individual stock/asset data.
interface Asset {
  symbol: string; // Ticker symbol (e.g., AAPL)
  name: string; // Full name (e.g., Apple Inc.)
  exchange: string; // Exchange it trades on (e.g., NASDAQ)
  asset_class: string; // Type of asset (e.g., equity)
  tradable: boolean; // Whether it's currently tradable
  market_cap?: number; // Market capitalization (optional)
  current_price?: number; // Current trading price (optional)
  high_52w?: number; // 52-week high price (optional)
  low_52w?: number; // 52-week low price (optional)
  volume?: number; // Trading volume (optional)
  day_change?: number; // Change in price today (absolute value) (optional)
  day_change_percent?: number; // Change in price today (percentage) (optional)
}

// OHLCVData interface defines the structure for Open, High, Low, Close, Volume data points.
interface OHLCVData {
  timestamp: string; // ISO timestamp string
  open: number; // Opening price for the period
  high: number; // Highest price for the period
  low: number; // Lowest price for the period
  close: number; // Closing price for the period
  volume: number; // Volume traded during the period
}

// Type for the structure of the mock asset details object.
// Using an index signature to allow accessing properties by symbol string.
type MockAssetDetails = {
  [key: string]: Asset;
};

// --- Styled Components ---
// Using styled-components for CSS-in-JS styling.

const PageContainer = styled.div`
  padding: 24px;
  font-family: 'Inter', sans-serif; // Added a default font
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  margin-bottom: 24px;
  color: #333;
  font-weight: 600; // Slightly bolder title
`;

const SearchContainer = styled.div`
  margin-bottom: 24px;
  position: relative; // Needed for absolute positioning of SearchResults
`;

const SearchInput = styled.input`
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #ddd;
  width: 300px;
  font-size: 16px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease; // Smooth transitions

  &:focus {
    outline: none;
    border-color: #4a90e2;
    box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2); // Slightly larger focus ring
  }
`;

const SearchResults = styled.div`
  margin-top: 8px;
  background: white;
  border-radius: 8px;
  border: 1px solid #eee;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
  position: absolute; // Position below the input
  width: 300px; // Match input width
  z-index: 10; // Ensure it's above other content
`;

const SearchResultItem = styled.div`
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s ease; // Smooth hover effect

  &:hover {
    background: #f5f8ff;
  }

  &:last-child {
    border-bottom: none;
  }
`;

const SymbolName = styled.div`
  font-weight: 500;
  color: #333; // Explicit color
`;

const ExchangeInfo = styled.div`
  font-size: 12px;
  color: #666;
`;

const ContentContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 300px; // Main content and stats sidebar
  gap: 24px;

  @media (max-width: 992px) { // Responsive layout for smaller screens
    grid-template-columns: 1fr; // Stack columns vertically
  }
`;

const ChartContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
`;

const StatsContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  align-self: start; // Align to the top in the grid cell
`;

const TimeframeSelector = styled.div`
  display: flex;
  flex-wrap: wrap; // Allow buttons to wrap on smaller screens
  gap: 8px;
  margin-bottom: 24px;
`;

// Using boolean prop 'active' for conditional styling
const TimeframeButton = styled.button<{ active?: boolean }>`
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid ${props => props.active ? '#4a90e2' : '#ddd'};
  background: ${props => props.active ? '#e6f0ff' : 'white'};
  color: ${props => props.active ? '#4a90e2' : '#666'};
  cursor: pointer;
  font-size: 14px;
  font-weight: 500; // Slightly bolder text
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease; // Smooth transitions

  &:hover {
    background: ${props => props.active ? '#d9e8ff' : '#f5f5f5'}; // Adjusted hover background
    border-color: ${props => props.active ? '#4a90e2' : '#ccc'}; // Darker border on hover
  }

  &:focus {
    outline: none; // Remove default outline
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2); // Focus ring for accessibility
  }
`;

const CandlestickChart = styled.div`
  width: 100%;
  min-height: 400px; // Use min-height to prevent collapse
  margin-bottom: 24px; // Spacing below chart placeholder
  display: flex; // Use flex for centering placeholder text
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9; // Placeholder background
  border-radius: 4px;
  color: #888;
  font-size: 14px;
`;

// Removed unused VolumeChart styled component
// const VolumeChart = styled.div`
//   width: 100%;
//   height: 100px;
// `;

const StatRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center; // Vertically align items
  margin-bottom: 16px;
  padding-bottom: 8px; // Add padding below each row
  border-bottom: 1px solid #eee; // Separator line

  &:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }
`;

const StatLabel = styled.div`
  color: #666;
  font-size: 14px;
`;

// Using boolean prop 'isPositive' for conditional coloring
const StatValue = styled.div<{ isPositive?: boolean }>`
  font-weight: 500;
  font-size: 14px; // Consistent font size
  color: ${props => props.isPositive === undefined ? '#333' :
    props.isPositive ? '#0ECB81' : '#F6465D'}; // Green for positive, Red for negative
`;

const LoadingContainer = styled.div`
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
`;

const EmptyStateContainer = styled.div`
  text-align: center;
  padding: 40px;
  color: #666;
  background-color: #f9f9f9; // Light background for emphasis
  border-radius: 8px;
  font-size: 16px;
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: 16px; // Adjusted padding
  color: #F6465D; // Red text for errors
  background: #FFF0F0; // Light red background
  border: 1px solid #F6465D; // Red border
  border-radius: 8px;
  margin-bottom: 24px;
  font-size: 14px;
`;

// --- React Component ---

const MarketDataPage: React.FC = () => {
  // --- State Hooks ---
  const [searchQuery, setSearchQuery] = useState(''); // Current text in the search input
  const [searchResults, setSearchResults] = useState<Asset[]>([]); // Assets matching the search query
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null); // The asset currently being viewed
  const [timeframe, setTimeframe] = useState<string>('1d'); // Selected chart timeframe (e.g., '1d', '1h')
  const [ohlcvData, setOhlcvData] = useState<OHLCVData[]>([]); // OHLCV data for the selected asset and timeframe
  const [loading, setLoading] = useState(false); // Indicates if data is currently being fetched
  const [error, setError] = useState<string | null>(null); // Stores any error messages
  const [showSearchResults, setShowSearchResults] = useState(false); // Controls visibility of the search results dropdown

  // --- Mock Data ---
  // Using a typed object for mock data to avoid 'any'.
  const mockAssetDetails: MockAssetDetails = {
    AAPL: {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      exchange: 'NASDAQ',
      asset_class: 'equity',
      tradable: true,
      market_cap: 2950000000000,
      current_price: 207.83,
      high_52w: 214.42,
      low_52w: 164.57,
      volume: 52124000,
      day_change: 3.45,
      day_change_percent: 1.69
    },
    MSFT: {
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      exchange: 'NASDAQ',
      asset_class: 'equity',
      tradable: true,
      market_cap: 3050000000000,
      current_price: 417.23,
      high_52w: 430.82,
      low_52w: 309.45,
      volume: 19850000,
      day_change: -1.18,
      day_change_percent: -0.28
    },
    GOOGL: {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      exchange: 'NASDAQ',
      asset_class: 'equity',
      tradable: true,
      market_cap: 1980000000000,
      current_price: 159.83,
      high_52w: 163.79,
      low_52w: 100.71,
      volume: 18250000,
      day_change: 1.23,
      day_change_percent: 0.78
    }
  };

  // --- Data Fetching Functions (Async) ---

  // Simulates searching for assets based on a query.
  const searchAssets = async (query: string) => {
    if (!query.trim()) { // Ignore empty or whitespace-only queries
      setSearchResults([]);
      setShowSearchResults(false); // Hide results if query is cleared
      return;
    }

    // No need to set loading/error here as it's a quick filter
    // setLoading(true);
    // setError(null);

    try {
      // --- Real API Call (Commented Out) ---
      // console.log(`Searching for: ${query}`);
      // const response = await axiosInstance.post('/api/v1/market-data/assets/search', { query });
      // setSearchResults(response.data);
      // --- End Real API Call ---

      // --- Mock Implementation ---
      // Filter the mock data based on symbol or name match (case-insensitive).
      const mockResults = Object.values(mockAssetDetails).filter(asset =>
        asset.symbol.toLowerCase().includes(query.toLowerCase()) ||
        asset.name.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(mockResults);
      setShowSearchResults(mockResults.length > 0); // Show results only if there are any
      // --- End Mock Implementation ---

    } catch (err) {
      console.error('Error searching assets:', err);
      setError('Failed to search for assets. Please try again.');
      setSearchResults([]); // Clear results on error
      setShowSearchResults(false);
    } finally {
      // setLoading(false); // Only needed if using actual async loading state
    }
  };

  // Simulates fetching OHLCV data for a given symbol and timeframe.
  const fetchOHLCVData = async (symbol: string, currentTf: string) => {
    setLoading(true); // Indicate loading started
    setError(null); // Clear previous errors
    setOhlcvData([]); // Clear previous chart data

    try {
      // --- Real API Call (Commented Out) ---
      // console.log(`Fetching OHLCV for ${symbol}, timeframe: ${currentTf}`);
      // const response = await axiosInstance.post('/api/v1/market-data/fetch', {
      //   symbol,
      //   timeframe: currentTf,
      //   limit: 100 // Example limit
      // });
      // setOhlcvData(response.data);
      // --- End Real API Call ---

      // --- Mock Implementation ---
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 500));

      const now = new Date();
      const mockData: OHLCVData[] = [];
      // Safely access basePrice using the defined type for mockAssetDetails
      const basePrice = mockAssetDetails[symbol]?.current_price ?? 100; // Use nullish coalescing for default
      const volatility = 0.02; // 2% volatility for mock data generation

      let startTime: Date;
      let timeIncrement: number; // Milliseconds

      // Determine start time and increment based on the selected timeframe
      switch (currentTf) {
        case '1m':
          startTime = new Date(now.getTime() - 60 * 60 * 1000); // 1 hour ago
          timeIncrement = 60 * 1000; // 1 minute
          break;
        case '5m':
          startTime = new Date(now.getTime() - 5 * 60 * 60 * 1000); // 5 hours ago
          timeIncrement = 5 * 60 * 1000; // 5 minutes
          break;
        case '15m':
          startTime = new Date(now.getTime() - 15 * 60 * 60 * 1000); // 15 hours ago
          timeIncrement = 15 * 60 * 1000; // 15 minutes
          break;
        case '1h':
          startTime = new Date(now.getTime() - 100 * 60 * 60 * 1000); // 100 hours ago
          timeIncrement = 60 * 60 * 1000; // 1 hour
          break;
        case '1w':
          startTime = new Date(now.getTime() - 100 * 7 * 24 * 60 * 60 * 1000); // 100 weeks ago
          timeIncrement = 7 * 24 * 60 * 60 * 1000; // 1 week
          break;
        case '1d': // Default to '1d'
        default:
          startTime = new Date(now.getTime() - 100 * 24 * 60 * 60 * 1000); // 100 days ago
          timeIncrement = 24 * 60 * 60 * 1000; // 1 day
          break;
      }

      let lastClose = basePrice;

      // Generate 100 data points for the chart
      for (let i = 0; i < 100; i++) {
        const timestamp = new Date(startTime.getTime() + i * timeIncrement);
        const changePercent = (Math.random() - 0.5) * 2 * volatility; // Random change +/- volatility
        const open = lastClose;
        const close = open * (1 + changePercent);
        // Ensure high is >= max(open, close) and low is <= min(open, close)
        const high = Math.max(open, close) * (1 + Math.random() * volatility * 0.5);
        const low = Math.min(open, close) * (1 - Math.random() * volatility * 0.5);
        const volume = Math.floor(Math.random() * 10000000) + 1000000; // Random volume

        mockData.push({
          timestamp: timestamp.toISOString(), // Use ISO string format
          open: parseFloat(open.toFixed(2)), // Format to 2 decimal places
          high: parseFloat(high.toFixed(2)),
          low: parseFloat(low.toFixed(2)),
          close: parseFloat(close.toFixed(2)),
          volume
        });

        lastClose = close; // Next open price starts from the current close
      }
      setOhlcvData(mockData);
      // --- End Mock Implementation ---

    } catch (err) {
      console.error('Error fetching OHLCV data:', err);
      setError('Failed to fetch market data. Please try again.');
      setOhlcvData([]); // Clear data on error
    } finally {
      setLoading(false); // Indicate loading finished
    }
  };

  // --- Event Handlers ---

  // Handles changes in the search input field.
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);

    // Trigger search only if query is long enough (e.g., 2+ characters)
    if (query.length >= 1) { // Reduced threshold to 1 for faster feedback
      searchAssets(query); // Debouncing could be added here for performance
    } else {
      setSearchResults([]); // Clear results if query is too short
      setShowSearchResults(false);
    }
  };

  // Handles selecting an asset from the search results.
  const handleAssetSelect = (asset: Asset) => {
    // Use mock details if available, otherwise use the basic asset info
    const detailedAsset = mockAssetDetails[asset.symbol] || asset;
    setSelectedAsset(detailedAsset);
    setSearchQuery(detailedAsset.symbol); // Update input to show selected symbol
    setShowSearchResults(false); // Hide search results dropdown
    fetchOHLCVData(detailedAsset.symbol, timeframe); // Fetch data for the selected asset
  };

  // Handles changing the timeframe for the chart.
  const handleTimeframeChange = (newTimeframe: string) => {
    setTimeframe(newTimeframe); // Update state
    if (selectedAsset) {
      // Fetch new data only if an asset is currently selected
      fetchOHLCVData(selectedAsset.symbol, newTimeframe);
    }
  };

  // --- Helper Functions ---

  // Formats large numbers (like market cap) into billions or trillions.
  const formatMarketCap = (value?: number): string => {
    if (value === undefined || value === null) return 'N/A';
    if (value >= 1e12) {
      return `${(value / 1e12).toFixed(2)}T`; // Trillions
    }
    if (value >= 1e9) {
      return `${(value / 1e9).toFixed(2)}B`; // Billions
    }
    if (value >= 1e6) {
      return `${(value / 1e6).toFixed(2)}M`; // Millions
    }
    return value.toLocaleString('en-US'); // Smaller numbers
  };

  // Formats numbers with commas and fixed decimal places.
  const formatNumber = (value?: number, minimumFractionDigits = 2, maximumFractionDigits = 2): string => {
    if (value === undefined || value === null) return 'N/A';
    return value.toLocaleString('en-US', {
      minimumFractionDigits,
      maximumFractionDigits,
    });
  };

  // --- Render Logic ---

  // Renders the placeholder for the candlestick chart.
  const renderCandlestickChart = () => {
    // In a real app, this would integrate a charting library (e.g., Lightweight Charts, Recharts).
    // It would receive ohlcvData and render the actual chart.
    if (loading) {
      return <div>Loading chart data...</div>; // Show loading state within the chart area
    }
    if (!selectedAsset || ohlcvData.length === 0) {
      return <div>No chart data available for the selected timeframe.</div>;
    }

    // Placeholder content demonstrating data is available
    return (
      <div>
        <div>Candlestick Chart Placeholder</div>
        <div>Symbol: {selectedAsset.symbol}</div>
        <div>Timeframe: {timeframe.toUpperCase()}</div>
        <div>Data Points: {ohlcvData.length}</div>
        {ohlcvData.length > 0 && (
          <div>
            Time Range: {new Date(ohlcvData[0].timestamp).toLocaleDateString()} - {new Date(ohlcvData[ohlcvData.length - 1].timestamp).toLocaleDateString()}
          </div>
        )}
      </div>
    );
  };

  return (
    <PageContainer>
      <SectionTitle>Market Data</SectionTitle>

      {/* Display error message if any error occurred */}
      {error && <ErrorMessage>{error}</ErrorMessage>}

      {/* Search Input and Results Dropdown */}
      <SearchContainer>
        <SearchInput
          type="text"
          placeholder="Search symbol or name (e.g., AAPL, Apple)"
          value={searchQuery}
          onChange={handleSearchChange}
          // Delay hiding results on blur to allow clicking an item
          onBlur={() => setTimeout(() => setShowSearchResults(false), 200)}
          // Show results on focus if there's already a query and results
          onFocus={() => searchQuery.length >= 1 && searchResults.length > 0 && setShowSearchResults(true)}
        />

        {/* Display search results dropdown if conditions met */}
        {showSearchResults && searchResults.length > 0 && (
          <SearchResults>
            {searchResults.map(asset => (
              <SearchResultItem
                key={asset.symbol} // Unique key for each item
                // Use onMouseDown instead of onClick to fire before onBlur
                onMouseDown={() => handleAssetSelect(asset)}
              >
                <SymbolName>{asset.symbol}</SymbolName>
                <ExchangeInfo>{asset.name} • {asset.exchange}</ExchangeInfo>
              </SearchResultItem>
            ))}
          </SearchResults>
        )}
      </SearchContainer>

      {/* Loading Indicator */}
      {loading && <LoadingContainer>Loading data...</LoadingContainer>}

      {/* Empty State (when no asset is selected and not loading) */}
      {!loading && !selectedAsset && (
        <EmptyStateContainer>
          Search for a symbol or company name to view market data and charts.
        </EmptyStateContainer>
      )}

      {/* Main Content (Chart and Stats - shown only when an asset is selected and not loading) */}
      {!loading && selectedAsset && (
        <ContentContainer>
          {/* Chart Area */}
          <ChartContainer>
            {/* Timeframe Selection Buttons */}
            <TimeframeSelector>
              {['1m', '5m', '15m', '1h', '1d', '1w'].map(tf => (
                <TimeframeButton
                  key={tf}
                  active={timeframe === tf} // Highlight the active button
                  onClick={() => handleTimeframeChange(tf)}
                >
                  {tf.toUpperCase()} {/* Display timeframe labels */}
                </TimeframeButton>
              ))}
            </TimeframeSelector>

            {/* Candlestick Chart Placeholder */}
            <CandlestickChart>
              {renderCandlestickChart()}
            </CandlestickChart>
            {/* Volume chart could be added here similarly */}
          </ChartContainer>

          {/* Statistics Sidebar */}
          <StatsContainer>
            {/* Asset Header Info */}
            <SectionTitle style={{ marginBottom: '8px', fontSize: '20px' }}>{selectedAsset.symbol}</SectionTitle>
            <div style={{ fontSize: '14px', color: '#555', marginBottom: '4px' }}>{selectedAsset.name}</div>
            <div style={{ fontSize: '12px', color: '#777', marginBottom: '24px' }}>{selectedAsset.exchange} • {selectedAsset.asset_class}</div>

            {/* Key Statistics */}
            <StatRow>
              <StatLabel>Price</StatLabel>
              {/* Use helper function for safe formatting */}
              <StatValue>${formatNumber(selectedAsset.current_price)}</StatValue>
            </StatRow>

            <StatRow>
              <StatLabel>Day Change</StatLabel>
              {/* Safely check day_change_percent using nullish coalescing */}
              <StatValue isPositive={(selectedAsset.day_change_percent ?? 0) >= 0}>
                {/* Show '+' sign for positive changes */}
                {(selectedAsset.day_change_percent ?? 0) >= 0 ? '+' : ''}{formatNumber(selectedAsset.day_change_percent, 2, 2)}%
                {' ('}
                {(selectedAsset.day_change ?? 0) >= 0 ? '+' : ''}${formatNumber(Math.abs(selectedAsset.day_change ?? 0), 2, 2)}
                {')'}
              </StatValue>
            </StatRow>

            <StatRow>
              <StatLabel>Volume</StatLabel>
              {/* Format volume with commas */}
              <StatValue>{formatNumber(selectedAsset.volume, 0, 0)}</StatValue>
            </StatRow>

            <StatRow>
              <StatLabel>Market Cap</StatLabel>
              {/* Use helper function for T/B/M formatting */}
              <StatValue>{formatMarketCap(selectedAsset.market_cap)}</StatValue>
            </StatRow>

            <StatRow>
              <StatLabel>52 Week High</StatLabel>
              <StatValue>${formatNumber(selectedAsset.high_52w)}</StatValue>
            </StatRow>

            <StatRow>
              <StatLabel>52 Week Low</StatLabel>
              <StatValue>${formatNumber(selectedAsset.low_52w)}</StatValue>
            </StatRow>

          </StatsContainer>
        </ContentContainer>
      )}
    </PageContainer>
  );
};

export default MarketDataPage; // Export the component for use elsewhere
