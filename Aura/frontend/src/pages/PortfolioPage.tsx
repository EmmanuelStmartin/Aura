import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
// Assuming this path is correct relative to your file structure
// import { getPositions, getAccount } from '../api/brokerageApi';

// --- Mock API Functions (Replace with your actual imports) ---
// These are placeholders since I can't access '../api/brokerageApi'
const mockPositions: Position[] = [
  { symbol: 'AAPL', qty: 10, avg_entry_price: 150, current_price: 175, market_value: 1750, unrealized_pl: 250, unrealized_plpc: 16.67, asset_name: 'Apple Inc.' },
  { symbol: 'GOOGL', qty: 5, avg_entry_price: 2500, current_price: 2700, market_value: 13500, unrealized_pl: 1000, unrealized_plpc: 8.00, asset_name: 'Alphabet Inc.' },
  { symbol: 'MSFT', qty: 8, avg_entry_price: 280, current_price: 300, market_value: 2400, unrealized_pl: 160, unrealized_plpc: 7.14, asset_name: 'Microsoft Corp.' },
];
const mockAccount: Account = { id: '123', account_number: 'XYZ789', status: 'ACTIVE', buying_power: 5000, cash: 5000, portfolio_value: 17650, currency: 'USD' };

const getPositions = async (): Promise<Position[]> => {
  console.log("Fetching mock positions...");
  await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
  // To test error state:
  // throw new Error("Failed to fetch positions");
  return mockPositions;
};

const getAccount = async (): Promise<Account> => {
  console.log("Fetching mock account...");
  await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
  // To test error state:
  // throw new Error("Failed to fetch account");
  return mockAccount;
};
// --- End Mock API Functions ---


// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// Types
interface Position {
  symbol: string;
  qty: number;
  avg_entry_price: number;
  current_price: number;
  market_value: number;
  unrealized_pl: number;
  unrealized_plpc: number; // Unrealized Profit/Loss Percentage
  asset_name?: string;
  asset_class?: string;
  // Added optional chaining for safety in calculations
  day_change?: number;
  day_change_percent?: number;
}

interface Account {
  id: string;
  account_number: string;
  status: string;
  buying_power: number;
  cash: number;
  portfolio_value: number; // Note: This might differ from calculated market value
  currency: string;
}

// Styled Components (Keeping these as they are)
const PageContainer = styled.div`
  padding: 24px;
  font-family: sans-serif; /* Added a default font */
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  margin-bottom: 24px;
  color: #333;
`;

const SummaryContainer = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const SummaryCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex: 1;
`;

const SummaryLabel = styled.div`
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
`;

// Define prop types for styled components for better linting/safety
interface ValueProps {
  isPositive?: boolean;
}

const SummaryValue = styled.div<ValueProps>`
  font-size: 24px;
  font-weight: 600;
  color: ${props => props.isPositive === undefined ? '#333' :
    props.isPositive ? '#0ECB81' : '#F6465D'};
`;

const SummaryPercent = styled.span<ValueProps>`
  font-size: 16px;
  color: ${props => props.isPositive ? '#0ECB81' : '#F6465D'};
  margin-left: 8px;
`;

const ChartContainer = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;

  @media (max-width: 992px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  /* Ensure charts have space to render */
  min-height: 350px; /* Adjust as needed */
  display: flex;
  flex-direction: column;
`;

const ChartTitle = styled.h3`
  font-size: 18px;
  margin-bottom: 16px;
  color: #333;
`;

const TimeRangeSelector = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap; /* Allow buttons to wrap on smaller screens */
`;

interface TimeButtonProps {
  active?: boolean;
}

const TimeButton = styled.button<TimeButtonProps>`
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid ${props => props.active ? '#4a90e2' : '#ddd'};
  background: ${props => props.active ? '#e6f0ff' : 'white'};
  color: ${props => props.active ? '#4a90e2' : '#666'};
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease, border-color 0.2s ease; /* Smooth transition */

  &:hover {
    background: ${props => props.active ? '#d9eaff' : '#f5f5f5'}; /* Slightly different hover */
  }
`;

const TableContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow-x: auto; /* Important for responsiveness */
`;

const HoldingsTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  min-width: 800px; /* Ensure table content doesn't wrap too aggressively */
`;

const TableHead = styled.thead`
  background: #f7f9fc;
`;

const TableHeaderCell = styled.th`
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #666;
  border-bottom: 1px solid #eee;
  white-space: nowrap; /* Prevent header text wrapping */
`;

const TableRow = styled.tr`
  &:hover {
    background: #f9f9f9;
  }
  /* Ensure alternating rows aren't affected by hover */
  &:nth-child(even) {
     background-color: #fafafa;
     &:hover {
        background: #f0f0f0; /* Slightly darker hover for even rows */
     }
  }
`;

const TableCell = styled.td`
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  vertical-align: middle; /* Align cell content vertically */
`;

const ValueCell = styled(TableCell)<ValueProps>`
  color: ${props => props.isPositive === undefined ? 'inherit' :
    props.isPositive ? '#0ECB81' : '#F6465D'};
  font-weight: 500; /* Make value cells slightly bolder */
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 48px; /* More padding */
  color: #666;
  font-size: 18px;
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: 24px;
  color: #D8000C; /* Stronger error red */
  background: #FFD2D2; /* Lighter error background */
  border: 1px solid #D8000C; /* Error border */
  border-radius: 8px;
  margin-bottom: 24px;
`;

// Define valid time range keys explicitly
type TimeRangeKey = '1D' | '1W' | '1M' | '3M' | '1Y' | 'ALL';

const PortfolioPage: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [account, setAccount] = useState<Account | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRangeKey>('1M'); // Use the specific type

  // Mock data for portfolio value chart (would be replaced with API data)
  // Using Record for better type safety
  const mockPortfolioHistory: Record<TimeRangeKey, { labels: string[]; values: number[] }> = {
    '1D': {
      labels: ['9:30', '10:30', '11:30', '12:30', '13:30', '14:30', '15:30', '16:00'],
      values: [10000, 10050, 10025, 10100, 10200, 10150, 10300, 10350]
    },
    '1W': {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      values: [10200, 10250, 10300, 10150, 10400, 10350, 10350]
    },
    '1M': {
      labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`), // More descriptive labels
      values: Array.from({ length: 30 }, (_, i) => 10000 + Math.sin(i / 5) * 500 + Math.random() * 200) // Smoother random data
    },
    '3M': {
      labels: ['Jan', 'Feb', 'Mar'],
      values: [9800, 10200, 10350]
    },
    '1Y': {
      labels: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
      values: [9500, 9600, 9800, 10000, 9900, 10100, 10300, 10200, 10400, 10300, 10100, 10350]
    },
    'ALL': {
      labels: ['2019', '2020', '2021', '2022', '2023', '2024'],
      values: [7000, 7500, 8200, 9000, 9800, 10350]
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch positions and account data concurrently
        const [positionsData, accountData] = await Promise.all([
          getPositions(),
          getAccount()
        ]);

        // Process positions
        // FIX 1: Explicitly type 'position' in the first map
        const processedPositions = positionsData.map((position: Position) => {
           // Calculate market value if not provided or zero
           const marketValue = position.market_value || (position.qty * position.current_price);
           // Mock day change data (ensure marketValue is not zero for calculation)
           const dayChange = marketValue !== 0 ? (Math.random() * 2 - 1) * marketValue * 0.02 : 0;
           return {
             ...position,
             market_value: marketValue,
             day_change: dayChange,
           };
        }).map((position) => { // Type is inferred correctly here from the previous map
           // Calculate day change percentage, handle division by zero
           const dayChangePercent = (position.market_value && position.day_change)
             ? (position.day_change / position.market_value) * 100
             : 0;
           return {
             ...position,
             day_change_percent: dayChangePercent
           };
        });

        setPositions(processedPositions);
        setAccount(accountData);
      } catch (err) {
        console.error('Error fetching portfolio data:', err);
        // Provide a more specific error message if possible
        const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.';
        setError(`Failed to load portfolio data: ${errorMessage}. Please try again later.`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Empty dependency array is correct here assuming getPositions/getAccount
    // are stable function references and don't depend on props/state.
  }, []);

  // --- Calculations ---
  const totalMarketValue = positions.reduce((sum, position) => sum + (position.market_value || 0), 0);
  const totalUnrealizedPL = positions.reduce((sum, position) => sum + (position.unrealized_pl || 0), 0);

  // Calculate total cost basis safely
  const totalCostBasis = positions.reduce((sum, position) => sum + (position.avg_entry_price * position.qty), 0);

  // FIX 4: Calculate total gain/loss percentage safely, handle division by zero
  const totalGainLossPercent = totalCostBasis !== 0
    ? (totalUnrealizedPL / totalCostBasis) * 100
    : 0; // If cost basis is 0, percentage is 0

  // --- Chart Data Preparation ---

  // FIX 2: Safely access mock history data
  const currentPortfolioHistory = mockPortfolioHistory[timeRange] || { labels: [], values: [] }; // Default to empty if key somehow invalid

  const portfolioValueChartData = {
    labels: currentPortfolioHistory.labels,
    datasets: [
      {
        label: 'Portfolio Value',
        data: currentPortfolioHistory.values,
        borderColor: '#4a90e2',
        backgroundColor: 'rgba(74, 144, 226, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4, // Smoothes the line
        pointRadius: 2,
        pointHoverRadius: 5, // Slightly larger hover radius
        pointBackgroundColor: '#4a90e2', // Color for points
      },
    ],
  };

  const allocationChartData = {
    labels: positions.map(p => p.symbol),
    datasets: [
      {
        label: 'Asset Allocation', // Added a label for clarity
        data: positions.map(p => p.market_value),
        backgroundColor: [ // More diverse color palette
          '#4a90e2', '#50e3c2', '#f5a623', '#bd10e0', '#7ed321',
          '#9013fe', '#f8e71c', '#d0021b', '#417505', '#b8e986'
        ],
        borderColor: '#ffffff', // White border for separation
        borderWidth: 2, // Slightly thicker border
        hoverOffset: 4 // Makes segment pop out slightly on hover
      },
    ],
  };

  // --- Chart Options ---
  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false, // Crucial for container sizing
    plugins: {
      legend: {
        display: false, // Legend not needed for single dataset
      },
      tooltip: {
        mode: 'index' as const, // Use const for literal type
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.7)', // Darker tooltip
        titleFont: { size: 14 },
        bodyFont: { size: 12 },
        padding: 10, // More padding
        callbacks: { // Format tooltip values
            label: function(context: any) {
                let label = context.dataset.label || '';
                if (label) {
                    label += ': ';
                }
                if (context.parsed.y !== null) {
                    label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                }
                return label;
            }
        }
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          // Format Y-axis ticks as currency
          callback: (value: number | string) =>
            typeof value === 'number' ? `$${value.toLocaleString('en-US')}` : value,
          color: '#666', // Axis label color
        },
        grid: {
          color: '#eee', // Lighter grid lines
        },
      },
      x: {
        ticks: {
          color: '#666',
           maxRotation: 0, // Prevent label rotation if possible
           autoSkip: true, // Automatically skip labels if too crowded
           maxTicksLimit: 10 // Limit number of visible ticks
        },
        grid: {
          display: false, // Hide vertical grid lines
        },
      },
    },
    // FIX 3: Removed redundant height property here
  };

  const doughnutChartOptions = {
    responsive: true,
    maintainAspectRatio: false, // Crucial for container sizing
    plugins: {
      legend: {
        position: 'right' as const, // Use const for literal type
        labels: {
          boxWidth: 12,
          padding: 15,
          color: '#333', // Legend text color
        },
      },
      tooltip: {
         backgroundColor: 'rgba(0, 0, 0, 0.7)',
         titleFont: { size: 14 },
         bodyFont: { size: 12 },
         padding: 10,
        callbacks: {
          label: (context: any) => { // Use 'any' carefully or define a specific type
            const value = context.raw as number;
            // Handle totalMarketValue being zero
            const percent = totalMarketValue !== 0
              ? ((value / totalMarketValue) * 100).toFixed(1)
              : '0.0';
            const formattedValue = value.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            });
            return `${context.label}: $${formattedValue} (${percent}%)`;
          },
        },
      },
    },
    cutout: '60%', // Creates the doughnut hole
     // FIX 3: Removed redundant height property here
  };

  // Helper function for formatting currency
  const formatCurrency = (value: number | undefined | null): string => {
      if (value === undefined || value === null) return '$0.00';
      return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

    // Helper function for formatting percentage
  const formatPercent = (value: number | undefined | null, addPlusSign = false): string => {
      if (value === undefined || value === null || isNaN(value)) return '0.00%';
      const sign = value >= 0 ? (addPlusSign ? '+' : '') : '-';
      return `${sign}${Math.abs(value).toFixed(2)}%`;
  };


  return (
    <PageContainer>
      <SectionTitle>Portfolio Overview</SectionTitle> {/* More descriptive title */}

      {/* Error Message Display */}
      {error && <ErrorMessage>{error}</ErrorMessage>}

      {/* Loading State */}
      {loading ? (
        <LoadingMessage>Loading portfolio data...</LoadingMessage>
      ) : (
        <>
          {/* Summary Section */}
          <SummaryContainer>
            <SummaryCard>
              <SummaryLabel>Portfolio Value</SummaryLabel>
              <SummaryValue>
                {formatCurrency(totalMarketValue)}
              </SummaryValue>
            </SummaryCard>

            <SummaryCard>
              <SummaryLabel>Total Gain/Loss</SummaryLabel>
              <SummaryValue isPositive={totalUnrealizedPL >= 0}>
                 {/* Show sign based on actual value */}
                 {totalUnrealizedPL >= 0 ? '+' : '-'}
                 {formatCurrency(Math.abs(totalUnrealizedPL))}
                <SummaryPercent isPositive={totalUnrealizedPL >= 0}>
                   {formatPercent(totalGainLossPercent)}
                </SummaryPercent>
              </SummaryValue>
            </SummaryCard>

            <SummaryCard>
              <SummaryLabel>Buying Power</SummaryLabel>
              <SummaryValue>
                 {/* Use optional chaining and nullish coalescing for safety */}
                {formatCurrency(account?.buying_power)}
              </SummaryValue>
            </SummaryCard>
          </SummaryContainer>

          {/* Charts Section */}
          <ChartContainer>
            <ChartCard>
              <ChartTitle>Portfolio Value Trend</ChartTitle>
              <TimeRangeSelector>
                {(['1D', '1W', '1M', '3M', '1Y', 'ALL'] as TimeRangeKey[]).map(range => (
                  <TimeButton
                    key={range}
                    active={timeRange === range}
                    onClick={() => setTimeRange(range)}
                  >
                    {range}
                  </TimeButton>
                ))}
              </TimeRangeSelector>
              {/* Ensure chart has data before rendering */}
              {portfolioValueChartData.labels.length > 0 ? (
                 <div style={{ flexGrow: 1, position: 'relative' }}> {/* Added container for sizing */}
                    <Line
                        data={portfolioValueChartData}
                        options={lineChartOptions}
                        /* FIX 3: Removed redundant height prop */
                    />
                 </div>
              ) : (
                 <LoadingMessage>No historical data available for this range.</LoadingMessage>
              )}
            </ChartCard>

            <ChartCard>
              <ChartTitle>Asset Allocation</ChartTitle>
               {/* Ensure chart has data before rendering */}
              {allocationChartData.labels.length > 0 ? (
                 <div style={{ flexGrow: 1, position: 'relative' }}> {/* Added container for sizing */}
                    <Doughnut
                        data={allocationChartData}
                        options={doughnutChartOptions}
                        /* FIX 3: Removed redundant height prop */
                    />
                 </div>
              ) : (
                 <LoadingMessage>No assets to display.</LoadingMessage>
              )}
            </ChartCard>
          </ChartContainer>

          {/* Holdings Table Section */}
          <SectionTitle>Holdings</SectionTitle>
          <TableContainer>
            <HoldingsTable>
              <TableHead>
                <tr>
                  <TableHeaderCell>Symbol</TableHeaderCell>
                  <TableHeaderCell>Name</TableHeaderCell>
                  <TableHeaderCell>Shares</TableHeaderCell>
                  <TableHeaderCell>Avg Cost</TableHeaderCell>
                  <TableHeaderCell>Current Price</TableHeaderCell>
                  <TableHeaderCell>Market Value</TableHeaderCell>
                  <TableHeaderCell>Day's Gain/Loss</TableHeaderCell>
                  <TableHeaderCell>Total Gain/Loss</TableHeaderCell>
                  <TableHeaderCell>% Return</TableHeaderCell>
                </tr>
              </TableHead>
              <tbody>
                {positions.length > 0 ? positions.map((position) => (
                  <TableRow key={position.symbol}>
                    <TableCell>{position.symbol}</TableCell>
                    <TableCell>{position.asset_name || position.symbol}</TableCell> {/* Fallback to symbol */}
                    <TableCell>{position.qty.toLocaleString('en-US')}</TableCell>
                    <TableCell>{formatCurrency(position.avg_entry_price)}</TableCell>
                    <TableCell>{formatCurrency(position.current_price)}</TableCell>
                    <TableCell>{formatCurrency(position.market_value)}</TableCell>
                    <ValueCell isPositive={position.day_change !== undefined && position.day_change >= 0}>
                      {position.day_change !== undefined && position.day_change >= 0 ? '+' : '-'}
                      {formatCurrency(Math.abs(position.day_change || 0))}
                      {' '}
                      ({formatPercent(position.day_change_percent)})
                    </ValueCell>
                     <ValueCell isPositive={position.unrealized_pl >= 0}>
                       {position.unrealized_pl >= 0 ? '+' : '-'}
                       {formatCurrency(Math.abs(position.unrealized_pl))}
                    </ValueCell>
                    <ValueCell isPositive={position.unrealized_plpc >= 0}>
                       {formatPercent(position.unrealized_plpc, true)} {/* Add plus sign */}
                    </ValueCell>
                  </TableRow>
                )) : (
                   <TableRow>
                      <TableCell colSpan={9} style={{ textAlign: 'center', color: '#666' }}>
                         You currently have no holdings.
                      </TableCell>
                   </TableRow>
                )}
              </tbody>
            </HoldingsTable>
          </TableContainer>
        </>
      )}
    </PageContainer>
  );
};

export default PortfolioPage;
