/// <reference types="cypress" />

// Describe block for the Portfolio Dashboard feature
describe('Portfolio Dashboard Tests', () => {
    // Runs before each test within this describe block
    beforeEach(() => {
      // Best practice: Use environment variables for credentials
      const email = Cypress.env('TEST_USER_EMAIL') || 'test_user@example.com';
      const password = Cypress.env('TEST_USER_PASSWORD') || 'TestPassword123!';
  
      // Visit the login page
      cy.visit('/login');
  
      // Find email input, type email, and assert the value
      // Using data-* attributes (e.g., data-cy="email-input") is recommended for more robust selectors
      cy.get('input[name="email"]').type(email).should('have.value', email);
  
      // Find password input, type password. Avoid asserting password value for security.
      cy.get('input[name="password"]').type(password);
  
      // Find and click the submit button
      cy.get('button[type="submit"]').click();
  
      // Verify successful login by checking the URL includes '/dashboard'
      // Adding a timeout can help with potential redirects or slow loads
      cy.url({ timeout: 10000 }).should('include', '/dashboard');
  
      // Verify a key element on the dashboard is visible to confirm login
      // Consider using a more specific selector like a data-cy attribute
      cy.contains('h1', 'Aura Dashboard', { timeout: 10000 }).should('be.visible'); // Increased timeout for page load
    });
  
    // Test case: Navigating to the portfolio view
    it('should navigate to portfolio view and verify essential components', () => {
      // Click on the portfolio link in the sidebar navigation
      // Using more specific selectors (e.g., data-cy="sidebar-portfolio-link") is preferable
      cy.get('nav').contains('a', 'Portfolio').click(); // Ensure it clicks an anchor tag
  
      // Verify the URL includes '/portfolio'
      cy.url().should('include', '/portfolio');
  
      // Verify the main heading 'Portfolio' is visible
      cy.contains('h1', 'Portfolio').should('be.visible');
  
      // Verify essential portfolio components are visible using their selectors
      // Using data-cy attributes like 'data-cy="portfolio-summary"' is recommended
      cy.get('.portfolio-summary', { timeout: 10000 }).should('be.visible'); // Wait for components to load
      cy.get('.portfolio-allocation').should('be.visible');
      cy.get('.asset-list').should('be.visible');
    });
  
    // Test case: Displaying portfolio value and performance metrics
    it('should display portfolio value and performance metrics', () => {
      // Navigate to portfolio (Consider moving navigation to a nested beforeEach if many tests need it)
      cy.get('nav').contains('a', 'Portfolio').click();
      cy.url().should('include', '/portfolio'); // Confirm navigation
  
      // Verify portfolio value element is visible and contains text (not empty)
      // Use a more specific selector if possible (e.g., data-cy="portfolio-total-value")
      cy.get('.portfolio-value')
        .should('be.visible')
        .invoke('text') // Get the text content
        .should('not.be.empty'); // Assert text is not empty
  
      // Verify performance metrics container and its contents
      // Use a more specific selector if possible (e.g., data-cy="performance-metrics")
      cy.get('.performance-metrics').within(() => {
        cy.contains('Daily Change').should('be.visible');
        cy.contains('Monthly Change').should('be.visible');
        cy.contains('YTD Return').should('be.visible');
        // Add assertions for the actual metric values if needed and predictable
        // e.g., cy.contains('.metric-value', /\d/).should('be.visible');
      });
    });
  
    // Test case: Displaying the breakdown of assets in a table
    it('should display a list/table with a breakdown of assets', () => {
      // Navigate to portfolio
      cy.get('nav').contains('a', 'Portfolio').click();
      cy.url().should('include', '/portfolio');
  
      // Verify the asset list/table is visible
      // Use a more specific selector (e.g., data-cy="asset-list-table")
      const assetListSelector = '.asset-list';
      cy.get(assetListSelector, { timeout: 10000 }).should('be.visible'); // Wait for data to load
  
      // Verify the table has a header row and at least one data row
      cy.get(`${assetListSelector} tr`).should('have.length.greaterThan', 1); // header + at least one asset
  
      // Verify the expected columns are present in the table header
      cy.get(`${assetListSelector} thead tr`).within(() => {
        cy.contains('th', 'Symbol').should('be.visible');
        cy.contains('th', 'Name').should('be.visible');
        cy.contains('th', 'Quantity').should('be.visible');
        cy.contains('th', 'Price').should('be.visible');
        cy.contains('th', 'Value').should('be.visible');
        cy.contains('th', 'Change').should('be.visible'); // Or '% Change' etc.
      });
  
      // Optional: Verify data exists in the first data row
      cy.get(`${assetListSelector} tbody tr`).first().within(() => {
        cy.get('td').should('have.length.at.least', 6); // Ensure correct number of columns
        cy.get('td').eq(0).invoke('text').should('not.be.empty'); // Symbol shouldn't be empty
        cy.get('td').eq(4).invoke('text').should('include', '$'); // Value might include currency
      });
    });
  
    // Test case: Navigating to asset details page on click
    it('should navigate to asset details when clicking on an asset row', () => {
      // Navigate to portfolio
      cy.get('nav').contains('a', 'Portfolio').click();
      cy.url().should('include', '/portfolio');
  
      // Wait for the asset list to potentially load data
      cy.get('.asset-list tbody tr', { timeout: 10000 }).should('have.length.greaterThan', 0);
  
      // Click on the first asset row in the table body
      // Using data-cy="asset-row-<asset_id>" on the row is more robust
      cy.get('.asset-list tbody tr').first().click();
  
      // Verify navigation to the asset details page (URL includes '/asset/')
      // The exact URL might vary (e.g., /asset/AAPL)
      cy.url({ timeout: 10000 }).should('include', '/asset/'); // Increased timeout for page load
  
      // Verify key components on the asset details page are visible
      // Use specific data-cy selectors for these elements
      cy.get('.asset-header', { timeout: 10000 }).should('be.visible'); // Wait for details to load
      cy.get('.price-chart').should('be.visible');
      cy.get('.trading-panel').should('be.visible');
    });
  
    // Test case: Filtering assets using a search input
    it('should filter assets by a search term', () => {
      // Navigate to portfolio
      cy.get('nav').contains('a', 'Portfolio').click();
      cy.url().should('include', '/portfolio');
  
      const assetListSelector = '.asset-list';
      const searchInputSelector = 'input[placeholder*="Search"]'; // Use data-cy="asset-search-input" if possible
  
      // Wait for the asset list to load
      cy.get(`${assetListSelector} tbody tr`, { timeout: 10000 }).should('have.length.greaterThan', 0);
  
      // Get the symbol/text from the first cell of the first row to use as a search term
      cy.get(`${assetListSelector} tbody tr`).first().find('td').first().invoke('text').then((symbol) => {
        const searchTerm = symbol.trim(); // Ensure no leading/trailing whitespace
        cy.log(`Searching for symbol: ${searchTerm}`); // Log the symbol being searched
  
        // Type the symbol into the search input
        cy.get(searchInputSelector).type(searchTerm);
  
        // Add a small wait or check for a loading indicator if filtering is async
        // cy.wait(500); // Or check for absence of loading spinner
  
        // Verify that only rows containing the search term are visible
        // This assumes filtering hides non-matching rows. Adjust if it works differently.
        cy.get(`${assetListSelector} tbody tr`).should('have.length.at.least', 1); // Should have at least one match
        cy.get(`${assetListSelector} tbody tr`).each(($row) => {
           cy.wrap($row).should('contain.text', searchTerm); // Check if row contains the term (case-insensitive)
        });
  
         // Verify the first result specifically contains the symbol
        cy.get(`${assetListSelector} tbody tr`).first().should('contain.text', searchTerm);
  
  
        // Clear the search filter
        cy.get(searchInputSelector).clear();
  
        // Add a small wait if clearing triggers async update
        // cy.wait(500);
  
        // Verify the asset list returns to showing more than one row (assuming there was more than one initially)
         cy.get(`${assetListSelector} tbody tr`).should('have.length.greaterThan', 0); // Check rows are back
      });
    });
  
    // Test case: Sorting assets by clicking column headers
    it('should sort assets when clicking on a sortable column header', () => {
      // Navigate to portfolio
      cy.get('nav').contains('a', 'Portfolio').click();
      cy.url().should('include', '/portfolio');
  
      const assetListSelector = '.asset-list';
      const valueHeaderSelector = 'th:contains("Value")'; // Use data-cy="asset-list-header-value" if possible
  
      // Wait for the asset list to load
      cy.get(`${assetListSelector} tbody tr`, { timeout: 10000 }).should('have.length.greaterThan', 1); // Need multiple assets to test sorting
  
      // Function to get the text content of the first cell (e.g., symbol) for each row
      const getFirstColumnData = (): Cypress.Chainable<string[]> => {
        const data: string[] = [];
        return cy.get(`${assetListSelector} tbody tr td:first-child`)
          .each(($el) => {
            data.push($el.text().trim());
          })
          .then(() => data); // Resolve the promise with the data array
      };
  
      // Get the initial order of assets by symbol (or another unique identifier)
      getFirstColumnData().then((initialOrder) => {
        cy.log('Initial Order:', initialOrder);
  
        // Click the 'Value' column header to sort
        cy.get(`${assetListSelector} ${valueHeaderSelector}`).click();
  
        // Add a wait or check for sort indicator/completion if sorting is asynchronous
        // cy.wait(500); or cy.get('th.sort-indicator').should('exist');
  
        // Get the sorted order
        getFirstColumnData().then((sortedOrder) => {
          cy.log('Sorted Order (1st click):', sortedOrder);
  
          // Verify the order has changed (assuming initial order wasn't already sorted by value)
          expect(sortedOrder).to.not.deep.equal(initialOrder, "Order should change after first sort click");
  
          // Optional: Click again to reverse sort (if applicable)
          cy.get(`${assetListSelector} ${valueHeaderSelector}`).click();
          // cy.wait(500); // Wait for potential re-sort
  
          getFirstColumnData().then((reverseSortedOrder) => {
            cy.log('Sorted Order (2nd click):', reverseSortedOrder);
            // Verify the order is different from the previous sort
            expect(reverseSortedOrder).to.not.deep.equal(sortedOrder, "Order should change after second sort click");
            // Optional: Verify it's the reverse of the sortedOrder or back to initialOrder if it toggles
             // expect(reverseSortedOrder).to.deep.equal(initialOrder); // If it toggles back
          });
        });
      });
    });
  });
  