// Check if we're in pagination mode (server-side) or original mode (client-side)
function isPaginationMode() {
  const tableElement = document.querySelector('#problems');
  return tableElement && tableElement.getAttribute('data-table') === 'false';
}

// Initialize filter and sort states for problems page
function initializeCollapsibleStates() {
  initializePageCollapsibleStates('problems');
}

// Apply filters with current state
function applyFilters() {
  const ownerSelect = document.getElementById('filter-owner');
  const colorSelect = document.getElementById('filter-color');
  const currentUrl = new URL(window.location);

  // Reset to first page when filters change (only for pagination mode)
  if (isPaginationMode()) {
    currentUrl.searchParams.set('page', '1');
  }

  // Handle owner filter
  if (ownerSelect) {
    const selectedOwner = ownerSelect.value;
    if (selectedOwner === 'all') {
      currentUrl.searchParams.delete('owner');
    } else {
      currentUrl.searchParams.set('owner', selectedOwner);
    }
  }

  // Handle color filter
  if (colorSelect) {
    const selectedColor = colorSelect.value;
    if (selectedColor === 'all') {
      currentUrl.searchParams.delete('color');
    } else {
      currentUrl.searchParams.set('color', selectedColor);
    }
  }

  window.location.href = currentUrl.toString();
}

// Keep filters expanded after selection
function applyFiltersAndKeepOpen() {
  preserveCollapsibleStateOnChange('table-filter', 'problems-filter-state');
  applyFilters();
}

// setupColorDropdown is now in shared collapsible-state.js

// Setup sort button functionality
function setupSortButtons() {
  const columnMap = {
    'name': 1,
    'color': 2,
    'quantity': 3,
    'missing': 4,
    'damaged': 5,
    'sets': 6,
    'minifigures': 7
  };
  // Use shared sort buttons setup from collapsible-state.js
  window.setupSharedSortButtons('problems', 'problemsTableInstance', columnMap);
}

// Problems page functionality
function setupProblemsPage() {
  // Handle search input
  const searchInput = document.getElementById('table-search');
  const clearButton = document.getElementById('table-search-clear');

  if (searchInput && clearButton) {
    let searchTimeout;

    // Search on input
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        if (isPaginationMode()) {
          // PAGINATION MODE - Server-side search via URL parameters
          const url = new URL(window.location);
          if (this.value.trim()) {
            url.searchParams.set('search', this.value.trim());
          } else {
            url.searchParams.delete('search');
          }
          url.searchParams.delete('page'); // Reset to first page
          window.location.href = url.toString();
        } else {
          // ORIGINAL MODE - Client-side instant search via Simple DataTables
          const searchValue = this.value.trim();
          const tableElement = document.querySelector('table[data-table="true"]');
          if (tableElement && window.problemsTableInstance) {
            // Enable searchable functionality
            window.problemsTableInstance.table.searchable = true;

            // Perform the search
            if (searchValue) {
              window.problemsTableInstance.table.search(searchValue);
            } else {
              // Clear search
              window.problemsTableInstance.table.search('');
            }
          }
        }
      }, 500);
    });

    // Clear search
    clearButton.addEventListener('click', function() {
      if (isPaginationMode()) {
        // PAGINATION MODE - Clear via URL parameters
        searchInput.value = '';
        const url = new URL(window.location);
        url.searchParams.delete('search');
        url.searchParams.delete('page');
        window.location.href = url.toString();
      } else {
        // ORIGINAL MODE - Clear via DataTables API
        searchInput.value = '';
        if (window.problemsTableInstance) {
          window.problemsTableInstance.table.search('');
        }
      }
    });
  }

  // Initialize collapsible states (filter and sort)
  initializeCollapsibleStates();

  // Setup sort and filter functionality (from parts.js)
  setupSortButtons();
  setupColorDropdown();

  // Update active sort button based on current URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const currentSort = urlParams.get('sort');
  const currentOrder = urlParams.get('order');

  if (currentSort) {
    const activeButton = document.querySelector(`[data-sort-attribute="${currentSort}"]`);
    if (activeButton) {
      activeButton.classList.add('active');
      // Add direction indicator
      if (currentOrder === 'desc') {
        activeButton.classList.add('btn-primary');
        activeButton.classList.remove('btn-outline-primary');
      }
    }
  }
}

// Helper function to check if we're in pagination mode
function isPaginationMode() {
  const tableElement = document.querySelector('#problems');
  return tableElement && tableElement.getAttribute('data-table') === 'false';
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', setupProblemsPage);