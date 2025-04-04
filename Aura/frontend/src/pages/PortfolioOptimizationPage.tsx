// Import necessary React hooks and libraries
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Doughnut } from 'react-chartjs-2';
// Import ChartJS and required elements for Doughnut chart
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
// Removed unused imports: axiosInstance, getPositions

// --- Mock API Functions (Placeholder - replace with actual API calls) ---
// These functions simulate fetching data.
const mockPositionsData: Position[] = [
    { symbol: 'AAPL', qty: 10, avg_entry_price: 180.50, current_price: 207.83, market_value: 2078.30, unrealized_pl: 273.30, unrealized_plpc: 15.14, asset_name: 'Apple Inc.', asset_class: 'equity' },
    { symbol: 'MSFT', qty: 5, avg_entry_price: 380.20, current_price: 417.23, market_value: 2086.15, unrealized_pl: 185.15, unrealized_plpc: 9.74, asset_name: 'Microsoft Corporation', asset_class: 'equity' },
    { symbol: 'GOOGL', qty: 15, avg_entry_price: 132.75, current_price: 159.83, market_value: 2397.45, unrealized_pl: 406.20, unrealized_plpc: 20.40, asset_name: 'Alphabet Inc.', asset_class: 'equity' },
    { symbol: 'AMZN', qty: 12, avg_entry_price: 170.30, current_price: 186.13, market_value: 2233.56, unrealized_pl: 189.96, unrealized_plpc: 9.29, asset_name: 'Amazon.com Inc.', asset_class: 'equity' },
    { symbol: 'TSLA', qty: 15, avg_entry_price: 190.45, current_price: 172.82, market_value: 2592.30, unrealized_pl: -264.45, unrealized_plpc: -9.26, asset_name: 'Tesla Inc.', asset_class: 'equity' }
];

// Simulate fetching positions
const fetchMockPositions = async (): Promise<Position[]> => {
  console.log("Fetching mock positions...");
  await new Promise(resolve => setTimeout(resolve, 300)); // Simulate network delay
  return mockPositionsData;
};

// Simulate calling optimization API
const fetchMockOptimization = async (symbols: string[], goal: string): Promise<OptimizationResult> => {
    console.log(`Optimizing for ${symbols.join(', ')} with goal: ${goal}`);
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API delay

    const totalWeight = 100;
    const mockWeights: Record<string, number> = {};
    let remainingWeight = totalWeight;

    // Generate random weights that sum to 100% for selected symbols
    symbols.forEach((symbol, index) => {
        if (index === symbols.length - 1) {
            mockWeights[symbol] = remainingWeight; // Last symbol gets remaining weight
        } else {
            // Generate random weight (ensure some minimum allocation)
            const maxPossible = Math.max(5, remainingWeight - (symbols.length - 1 - index) * 5); // Ensure remaining symbols can get at least 5%
            const weight = Math.floor(Math.random() * (maxPossible - 5)) + 5;
            mockWeights[symbol] = weight;
            remainingWeight -= weight;
        }
    });

     // Ensure weights are rounded correctly and sum exactly to 100
     let currentSum = 0;
     Object.keys(mockWeights).forEach(symbol => {
         mockWeights[symbol] = parseFloat(mockWeights[symbol].toFixed(2));
         currentSum += mockWeights[symbol];
     });
     // Adjust the last weight if rounding caused a small discrepancy
     if (currentSum !== 100 && symbols.length > 0) {
        const lastSymbol = symbols[symbols.length - 1];
        mockWeights[lastSymbol] = parseFloat((mockWeights[lastSymbol] + (100 - currentSum)).toFixed(2));
     }


    // Generate mock metrics based on the goal
    let expectedReturn, expectedVolatility, sharpeRatio;
    if (goal === 'sharpe') {
        expectedReturn = parseFloat((Math.random() * 10 + 10).toFixed(2)); // Higher return focus: 10-20%
        expectedVolatility = parseFloat((Math.random() * 8 + 12).toFixed(2)); // Moderate volatility: 12-20%
        sharpeRatio = parseFloat((Math.random() * 1 + 1.0).toFixed(2)); // Higher Sharpe: 1.0-2.0
    } else { // Minimize volatility
        expectedReturn = parseFloat((Math.random() * 8 + 6).toFixed(2)); // Lower return focus: 6-14%
        expectedVolatility = parseFloat((Math.random() * 6 + 8).toFixed(2)); // Lower volatility: 8-14%
        sharpeRatio = parseFloat((Math.random() * 0.8 + 0.5).toFixed(2)); // Lower Sharpe: 0.5-1.3
    }

    const mockResult: OptimizationResult = {
        weights: mockWeights,
        expected_annual_return: expectedReturn,
        expected_volatility: expectedVolatility,
        sharpe_ratio: sharpeRatio
    };

    return mockResult;
};
// --- End Mock API Functions ---


// **Register necessary ChartJS components**
// This step is crucial for Chart.js v3+ with react-chartjs-2
ChartJS.register(
  ArcElement, // Required for Doughnut charts
  Tooltip,    // Optional: For displaying tooltips on hover
  Legend      // Optional: For displaying the legend
);

// --- Types ---
// Defines the structure for a single portfolio position
interface Position {
  symbol: string;
  qty: number;
  avg_entry_price: number;
  current_price: number;
  market_value: number;
  unrealized_pl: number; // Unrealized Profit/Loss amount
  unrealized_plpc: number; // Unrealized Profit/Loss percentage
  asset_name?: string; // Optional: Full name of the asset
  asset_class?: string; // Optional: Type of asset (e.g., equity, crypto)
}

// Defines the structure for the optimization results received from the API
interface OptimizationResult {
  weights: Record<string, number>; // e.g., { "AAPL": 40.5, "MSFT": 59.5 }
  expected_annual_return: number; // Percentage
  expected_volatility: number; // Percentage
  sharpe_ratio: number; // Unitless ratio
}

// --- Styled Components ---
// Provides basic layout and styling for the page elements
const PageContainer = styled.div`
  padding: 24px;
  font-family: sans-serif; /* Basic font */
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  margin-bottom: 24px;
  color: #333;
  font-weight: 600;
`;

const FormContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08); /* Slightly stronger shadow */
  margin-bottom: 24px;
`;

const FormTitle = styled.h3`
  font-size: 18px;
  margin-bottom: 20px; /* More space below title */
  color: #333;
  font-weight: 600;
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

const SymbolSelectContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px; /* Slightly more gap */
  margin-top: 8px;
`;

const SymbolCheckbox = styled.div`
  display: flex;
  align-items: center;
  padding: 8px 12px; /* More padding */
  background: #f5f8ff;
  border: 1px solid #e0e8ff; /* Subtle border */
  border-radius: 4px;
  cursor: pointer;
  user-select: none; /* Prevent text selection */
  transition: background-color 0.2s ease;

  input[type="checkbox"] {
    margin-right: 8px;
    cursor: pointer;
  }

  label {
    cursor: pointer;
    font-size: 14px;
    color: #333;
  }

  &:hover {
    background: #eaf1ff;
  }
`;


const OptionsContainer = styled.div`
  display: flex;
  gap: 20px; /* More gap */

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 10px; /* Less gap in column layout */
  }
`;

const RadioOption = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 8px;

  input[type="radio"] {
    margin-right: 8px;
    cursor: pointer;
  }

  label {
    margin-bottom: 0;
    cursor: pointer;
    font-size: 14px;
    color: #333;
  }
`;

const SubmitButton = styled.button`
  padding: 12px 24px;
  background-color: #4a90e2;
  border: none;
  border-radius: 4px;
  color: white;
  font-size: 16px; /* Slightly larger font */
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: inline-flex; /* Align spinner and text */
  align-items: center;
  justify-content: center;

  &:hover:not(:disabled) { /* Only apply hover when not disabled */
    background-color: #3a7bc8;
  }

  &:disabled {
    background-color: #cccccc; /* More distinct disabled state */
    cursor: not-allowed;
    opacity: 0.7;
  }
`;

// Simple CSS spinner for loading indication
const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 3px solid rgba(255, 255, 255, 0.3); /* Thicker border */
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-right: 8px; /* Space between spinner and text */

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

const ResultsContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr; /* Two equal columns */
  gap: 24px;
  margin-top: 24px; /* Space above results */

  @media (max-width: 992px) {
    grid-template-columns: 1fr; /* Stack on smaller screens */
  }
`;

const ResultCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
`;

const ChartContainer = styled.div`
  height: 300px; /* Fixed height for chart area */
  margin-bottom: 16px;
  position: relative; /* Needed for chart responsiveness */
`;

const MetricsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); /* Responsive grid */
  gap: 16px;
  margin-top: 16px; /* Space above metrics */
`;

const MetricCard = styled.div`
  background: #f7f9fc;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e8edf5; /* Subtle border */
`;

const MetricLabel = styled.div`
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
`;

const MetricValue = styled.div`
  font-size: 20px;
  font-weight: 600;
  color: #333;
`;

const WeightsTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
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
  white-space: nowrap; /* Prevent header wrapping */
`;

const TableRow = styled.tr`
  &:nth-child(even) {
     background-color: #fafafa; /* Zebra striping */
  }
  &:hover {
    background: #f0f5ff; /* Subtle hover effect */
  }
`;

const TableCell = styled.td`
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
`;

// Styled span to highlight allocation changes (increase/decrease)
const AllocationChange = styled.span<{ isIncrease: boolean }>`
  color: ${props => props.isIncrease ? '#0ECB81' : '#F6465D'};
  font-weight: 500;
`;

// Message shown when no positions are available
const EmptyState = styled.div`
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f9f9f9;
  border: 1px dashed #ddd; /* Dashed border */
  border-radius: 8px;
`;

// Message shown while loading data
const LoadingMessage = styled.div`
  text-align: center;
  padding: 48px; /* More padding */
  color: #666;
  font-size: 18px;
`;

// Message shown when an error occurs
const ErrorMessage = styled.div`
  text-align: center;
  padding: 16px;
  margin-bottom: 16px;
  color: #D8000C; /* Stronger error red */
  background: #FFD2D2; /* Lighter error background */
  border: 1px solid #D8000C; /* Error border */
  border-radius: 8px;
`;

// --- React Component ---
const PortfolioOptimizationPage: React.FC = () => {
  // State for portfolio positions
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true); // Loading state for initial position fetch
  const [error, setError] = useState<string | null>(null); // General error messages

  // State for the optimization form
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]); // Symbols chosen by the user
  const [optimizationGoal, setOptimizationGoal] = useState<string>('sharpe'); // 'sharpe' or 'volatility'
  const [isSubmitting, setIsSubmitting] = useState(false); // Loading state for optimization API call

  // State for storing the optimization results
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);

  // Fetch initial portfolio positions when the component mounts
  useEffect(() => {
    // Define the async function to fetch positions
    const loadPositions = async () => {
      setLoading(true);
      setError(null);
      setOptimizationResult(null); // Clear previous results

      try {
        // Replace with your actual API call:
        // const positionsData = await getPositions();
        const positionsData = await fetchMockPositions(); // Using mock function

        setPositions(positionsData);

        // Default to selecting all available symbols for optimization
        setSelectedSymbols(positionsData.map(pos => pos.symbol));

      } catch (err) {
        console.error('Error fetching positions:', err);
        const message = err instanceof Error ? err.message : 'An unknown error occurred.';
        setError(`Failed to load portfolio positions: ${message}. Please try again.`);
      } finally {
        setLoading(false);
      }
    };

    loadPositions();
    // Empty dependency array means this runs once on mount
  }, []);

  // --- Event Handlers ---

  // Toggles the selection state of a symbol checkbox
  const handleSymbolChange = (symbol: string) => {
    setSelectedSymbols(prev =>
      prev.includes(symbol)
        ? prev.filter(s => s !== symbol) // Remove if already selected
        : [...prev, symbol] // Add if not selected
    );
     // Clear previous results when selections change
     setOptimizationResult(null);
     setError(null); // Clear errors too
  };

  // Updates the optimization goal when a radio button is changed
  const handleGoalChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOptimizationGoal(e.target.value);
     // Clear previous results when goal changes
     setOptimizationResult(null);
     setError(null);
  };

  // Handles the form submission to run the portfolio optimization
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevent default form submission

    // Basic validation
    if (selectedSymbols.length < 2) {
      setError('Please select at least 2 symbols for optimization.');
      return;
    }

    // Set loading state and clear previous results/errors
    setIsSubmitting(true);
    setError(null);
    setOptimizationResult(null);

    try {
      // Replace with your actual API call:
      // const endpoint = optimizationGoal === 'sharpe'
      //   ? '/api/v1/optimize/maximize-sharpe'
      //   : '/api/v1/optimize/minimize-volatility';
      // const response = await axiosInstance.post(endpoint, { symbols: selectedSymbols });
      // setOptimizationResult(response.data);

      // Using mock function:
      const resultData = await fetchMockOptimization(selectedSymbols, optimizationGoal);
      setOptimizationResult(resultData);

    } catch (err) {
      console.error('Error optimizing portfolio:', err);
       const message = err instanceof Error ? err.message : 'An unknown error occurred.';
      setError(`Failed to optimize portfolio: ${message}. Please try again.`);
    } finally {
      setIsSubmitting(false); // Reset loading state
    }
  };

  // --- Data Calculation & Preparation ---

  // Calculates the difference between current and optimized allocations
  const calculateAllocationChanges = (): Record<string, number> => {
    if (!optimizationResult) return {}; // Return empty if no results

    const currentWeights: Record<string, number> = {};
    const totalValue = positions.reduce((sum, pos) => sum + (pos.market_value || 0), 0);

    // Calculate current weights only if totalValue is positive
    if (totalValue > 0) {
        positions.forEach(pos => {
            currentWeights[pos.symbol] = (pos.market_value / totalValue) * 100;
        });
    }


    const changes: Record<string, number> = {};
    // Calculate the difference for each symbol in the optimization result
    Object.keys(optimizationResult.weights).forEach(symbol => {
      const optimizedWeight = optimizationResult.weights[symbol] || 0;
      const currentWeight = currentWeights[symbol] || 0; // Default to 0 if not currently held
      changes[symbol] = optimizedWeight - currentWeight;
    });

    return changes;
  };

  // Prepares data for the 'Current Allocation' Doughnut chart
  const getCurrentAllocationChartData = () => {
    const totalValue = positions.reduce((sum, pos) => sum + (pos.market_value || 0), 0);

    // Return null if total value is zero to prevent chart errors
    if (totalValue <= 0) {
        return null;
    }

    const labels = positions.map(pos => pos.symbol);
    const data = positions.map(pos =>
        parseFloat(((pos.market_value / totalValue) * 100).toFixed(2))
    );

    return {
      labels: labels,
      datasets: [
        {
          label: 'Current Allocation %', // Add label
          data: data,
          backgroundColor: [ // Use a consistent color palette
            '#4a90e2', '#50e3c2', '#f5a623', '#bd10e0', '#7ed321',
            '#9013fe', '#f8e71c', '#d0021b', '#417505', '#b8e986'
          ],
          borderColor: '#ffffff', // White border for separation
          borderWidth: 1,
        },
      ],
    };
  };

  // Prepares data for the 'Optimized Allocation' Doughnut chart
  const getOptimizedAllocationChartData = () => {
    if (!optimizationResult) return null; // Return null if no results

    const labels = Object.keys(optimizationResult.weights);
    const data = Object.values(optimizationResult.weights);

     // Return null if there's no data to display
     if (labels.length === 0) {
        return null;
     }

    return {
      labels: labels,
      datasets: [
        {
          label: 'Optimized Allocation %', // Add label
          data: data,
          backgroundColor: [ // Use the same palette for consistency
            '#4a90e2', '#50e3c2', '#f5a623', '#bd10e0', '#7ed321',
            '#9013fe', '#f8e71c', '#d0021b', '#417505', '#b8e986'
          ],
           borderColor: '#ffffff',
          borderWidth: 1,
        },
      ],
    };
  };

  // Common options for both Doughnut charts
  const doughnutChartOptions = {
    responsive: true,
    maintainAspectRatio: false, // Important for sizing within container
    plugins: {
      legend: {
        position: 'right' as const, // Position legend to the right
        labels: {
          boxWidth: 12,
          padding: 15,
          font: { size: 12 } // Adjust font size
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.7)', // Darker tooltip
        callbacks: {
          // Format tooltip label to show percentage
          label: (context: any) => { // Use 'any' or define specific Chart.js types
            const label = context.label || '';
            const value = context.raw || 0;
            return `${label}: ${value.toFixed(2)}%`; // Show 2 decimal places
          }
        }
      }
    },
    cutout: '60%' // Percentage of the center cut out
  };

  // Calculate changes (memoize if performance becomes an issue)
  const allocationChanges = calculateAllocationChanges();
  const currentAllocationData = getCurrentAllocationChartData();
  const optimizedAllocationData = getOptimizedAllocationChartData();


  // --- Render Logic ---

  // Show loading message while fetching initial positions
  if (loading) {
    return <LoadingMessage>Loading portfolio data...</LoadingMessage>;
  }

  // Main component render
  return (
    <PageContainer>
      <SectionTitle>Portfolio Optimization</SectionTitle>

      {/* Display general error messages */}
      {error && <ErrorMessage>{error}</ErrorMessage>}

      {/* Show empty state if no positions are loaded */}
      {positions.length === 0 && !loading ? (
        <EmptyState>
          No positions found in your portfolio. Add assets to use the optimization tool.
        </EmptyState>
      ) : (
        // Render form and results if positions exist
        <>
          {/* Optimization Form */}
          <FormContainer>
            <FormTitle>Optimization Parameters</FormTitle>
            <form onSubmit={handleSubmit}>
              {/* Symbol Selection */}
              <FormGroup>
                <Label>Select Assets to Optimize (minimum 2)</Label>
                <SymbolSelectContainer>
                  {positions.map(position => (
                    <SymbolCheckbox key={position.symbol}>
                      <input
                        type="checkbox"
                        id={`symbol-${position.symbol}`}
                        value={position.symbol} // Added value attribute
                        checked={selectedSymbols.includes(position.symbol)}
                        onChange={() => handleSymbolChange(position.symbol)}
                      />
                      <label htmlFor={`symbol-${position.symbol}`}>{position.symbol}</label>
                    </SymbolCheckbox>
                  ))}
                </SymbolSelectContainer>
              </FormGroup>

              {/* Optimization Goal Selection */}
              <FormGroup>
                <Label>Optimization Goal</Label>
                <OptionsContainer>
                  <RadioOption>
                    <input
                      type="radio"
                      id="goal-sharpe"
                      name="optimizationGoal" // Consistent name attribute
                      value="sharpe"
                      checked={optimizationGoal === 'sharpe'}
                      onChange={handleGoalChange}
                    />
                    <label htmlFor="goal-sharpe">Maximize Sharpe Ratio (Risk-Adjusted Return)</label>
                  </RadioOption>
                  <RadioOption>
                    <input
                      type="radio"
                      id="goal-volatility"
                      name="optimizationGoal" // Consistent name attribute
                      value="volatility"
                      checked={optimizationGoal === 'volatility'}
                      onChange={handleGoalChange}
                    />
                    <label htmlFor="goal-volatility">Minimize Volatility (Risk)</label>
                  </RadioOption>
                </OptionsContainer>
              </FormGroup>

              {/* Submit Button */}
              <SubmitButton type="submit" disabled={isSubmitting || selectedSymbols.length < 2}>
                {isSubmitting && <LoadingSpinner />}
                {isSubmitting ? 'Optimizing...' : 'Optimize Portfolio'}
              </SubmitButton>
            </form>
          </FormContainer>

          {/* Results Section - Only shown after successful optimization */}
          {optimizationResult && (
            <ResultsContainer>
              {/* Current Allocation Chart */}
              <ResultCard>
                <FormTitle>Current Allocation</FormTitle>
                <ChartContainer>
                  {currentAllocationData ? (
                     <Doughnut data={currentAllocationData} options={doughnutChartOptions} />
                  ) : (
                     <EmptyState>No current allocation data to display.</EmptyState>
                  )}
                </ChartContainer>
              </ResultCard>

              {/* Optimized Allocation Chart & Metrics */}
              <ResultCard>
                <FormTitle>Optimized Allocation ({optimizationGoal === 'sharpe' ? 'Max Sharpe' : 'Min Volatility'})</FormTitle>
                 <ChartContainer>
                   {optimizedAllocationData ? (
                      <Doughnut data={optimizedAllocationData} options={doughnutChartOptions} />
                   ) : (
                      <EmptyState>No optimized allocation data to display.</EmptyState>
                   )}
                 </ChartContainer>

                {/* Key Metrics */}
                <MetricsContainer>
                  <MetricCard>
                    <MetricLabel>Expected Annual Return</MetricLabel>
                    <MetricValue>{optimizationResult.expected_annual_return.toFixed(2)}%</MetricValue>
                  </MetricCard>
                  <MetricCard>
                    <MetricLabel>Expected Volatility</MetricLabel>
                    <MetricValue>{optimizationResult.expected_volatility.toFixed(2)}%</MetricValue>
                  </MetricCard>
                  <MetricCard>
                    <MetricLabel>Sharpe Ratio</MetricLabel>
                    <MetricValue>{optimizationResult.sharpe_ratio.toFixed(2)}</MetricValue>
                  </MetricCard>
                </MetricsContainer>
              </ResultCard>

              {/* Allocation Changes Table */}
              <ResultCard style={{ gridColumn: '1 / -1' }}> {/* Span full width */}
                <FormTitle>Allocation Changes</FormTitle>
                <div style={{ overflowX: 'auto' }}> {/* Make table scrollable */}
                    <WeightsTable>
                    <TableHead>
                        <tr>
                        <TableHeaderCell>Symbol</TableHeaderCell>
                        <TableHeaderCell>Current Weight</TableHeaderCell>
                        <TableHeaderCell>Optimized Weight</TableHeaderCell>
                        <TableHeaderCell>Change</TableHeaderCell>
                        </tr>
                    </TableHead>
                    <tbody>
                        {Object.keys(allocationChanges).map(symbol => {
                        // Find the position to get current weight (handle case where it might not exist)
                        const position = positions.find(p => p.symbol === symbol);
                        const totalValue = positions.reduce((sum, pos) => sum + (pos.market_value || 0), 0);
                        const currentWeightValue = position && totalValue > 0 ? (position.market_value / totalValue) * 100 : 0;

                        const optimizedWeightValue = optimizationResult.weights[symbol] || 0;
                        const changeValue = allocationChanges[symbol] || 0;
                        const isIncrease = changeValue >= 0;

                        return (
                            <TableRow key={symbol}>
                            <TableCell>{symbol}</TableCell>
                            <TableCell>{currentWeightValue.toFixed(2)}%</TableCell>
                            <TableCell>{optimizedWeightValue.toFixed(2)}%</TableCell>
                            <TableCell>
                                <AllocationChange isIncrease={isIncrease}>
                                {isIncrease ? '+' : ''}{changeValue.toFixed(2)}%
                                </AllocationChange>
                            </TableCell>
                            </TableRow>
                        );
                        })}
                    </tbody>
                    </WeightsTable>
                </div>
              </ResultCard>
            </ResultsContainer>
          )}
        </>
      )}
    </PageContainer>
  );
};

export default PortfolioOptimizationPage;
