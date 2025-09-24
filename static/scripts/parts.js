// Parts page functionality
function applyFilters() {
  const ownerSelect = document.getElementById('filter-owner');
  const colorSelect = document.getElementById('filter-color');
  const currentUrl = new URL(window.location);

  // Reset to first page when filters change (only for pagination mode)
  const tableElement = document.querySelector('#parts');
  if (tableElement && tableElement.getAttribute('data-table') === 'false') {
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

// setupColorDropdown is now in shared collapsible-state.js

// Initialize filter and sort states for parts page
function initializeCollapsibleStates() {
  initializePageCollapsibleStates('parts');
}

// Keep filters expanded after selection
function applyFiltersAndKeepOpen() {
  preserveCollapsibleStateOnChange('table-filter', 'parts-filter-state');
  applyFilters();
}

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
  window.setupSharedSortButtons('parts', 'partsTableInstance', columnMap);
}

// Check if pagination mode is enabled
function isPaginationMode() {
  const tableElement = document.querySelector('#parts');
  // In pagination mode, table has data-table="false"
  // In original mode, table has data-table="true"
  return tableElement && tableElement.getAttribute('data-table') === 'false';
}

// Initialize sort button states for pagination mode
function initializeSortButtonStates() {
  const currentUrl = new URL(window.location);
  const currentSort = currentUrl.searchParams.get('sort');
  const currentOrder = currentUrl.searchParams.get('order');

  if (currentSort) {
    const sortButtons = document.querySelectorAll('[data-sort-attribute]');
    sortButtons.forEach(btn => {
      // Clear all buttons first
      btn.classList.remove('btn-primary');
      btn.classList.add('btn-outline-primary');
      btn.removeAttribute('data-current-direction');

      // Set active state for current sort
      if (btn.dataset.sortAttribute === currentSort) {
        btn.classList.remove('btn-outline-primary');
        btn.classList.add('btn-primary');
        btn.dataset.currentDirection = currentOrder || 'asc';
      }
    });
  }
}

// Setup table search and sort functionality
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById('table-search');
  const searchClear = document.getElementById('table-search-clear');

  // Initialize collapsible states (filter and sort)
  initializeCollapsibleStates();

  // Setup color dropdown with color squares
  setupColorDropdown();

  if (searchInput && searchClear) {
    if (isPaginationMode()) {
      // PAGINATION MODE - Server-side search with Enter key
      // Search on Enter key press
      searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const currentUrl = new URL(window.location);
          const searchValue = e.target.value.trim();

          // Reset to first page when searching
          currentUrl.searchParams.set('page', '1');

          if (searchValue) {
            currentUrl.searchParams.set('search', searchValue);
          } else {
            currentUrl.searchParams.delete('search');
          }

          window.location.href = currentUrl.toString();
        }
      });

      // Clear search
      searchClear.addEventListener('click', () => {
        const currentUrl = new URL(window.location);
        currentUrl.searchParams.delete('search');
        currentUrl.searchParams.set('page', '1');
        window.location.href = currentUrl.toString();
      });
    } else {
      // ORIGINAL MODE - Client-side instant search via Simple DataTables
      // Wait for table to be initialized
      const setupClientSearch = () => {
        const tableElement = document.querySelector('table[data-table="true"]');
        if (tableElement && window.partsTableInstance) {
          // Enable search functionality
          window.partsTableInstance.table.searchable = true;

          // Instant search as user types
          searchInput.addEventListener('input', (e) => {
            const searchValue = e.target.value.trim();
            window.partsTableInstance.table.search(searchValue);
          });

          // Clear search
          searchClear.addEventListener('click', () => {
            searchInput.value = '';
            window.partsTableInstance.table.search('');
          });
        } else {
          // If table instance not ready, try again
          setTimeout(setupClientSearch, 100);
        }
      };

      setTimeout(setupClientSearch, 100);
    }
  }

  // Setup sort buttons
  setupSortButtons();

  // Initialize sort button states for pagination mode
  if (isPaginationMode()) {
    initializeSortButtonStates();
  }
});

