// Minifigures page functionality

// Check if we're in pagination mode (server-side) or original mode (client-side)
function isPaginationMode() {
  const tableElement = document.querySelector('#minifigures');
  return tableElement && tableElement.getAttribute('data-table') === 'false';
}

function applyFilters() {
  const ownerSelect = document.getElementById('filter-owner');
  const problemsSelect = document.getElementById('filter-problems');
  const themeSelect = document.getElementById('filter-theme');
  const yearSelect = document.getElementById('filter-year');
  const currentUrl = new URL(window.location);

  // Apply owner filter
  if (ownerSelect) {
    const selectedOwner = ownerSelect.value;
    if (selectedOwner === 'all') {
      currentUrl.searchParams.delete('owner');
    } else {
      currentUrl.searchParams.set('owner', selectedOwner);
    }
  }

  // Apply problems filter
  if (problemsSelect) {
    const selectedProblems = problemsSelect.value;
    if (selectedProblems === 'all') {
      currentUrl.searchParams.delete('problems');
    } else {
      currentUrl.searchParams.set('problems', selectedProblems);
    }
  }

  // Apply theme filter
  if (themeSelect) {
    const selectedTheme = themeSelect.value;
    if (selectedTheme === 'all') {
      currentUrl.searchParams.delete('theme');
    } else {
      currentUrl.searchParams.set('theme', selectedTheme);
    }
  }

  // Apply year filter
  if (yearSelect) {
    const selectedYear = yearSelect.value;
    if (selectedYear === 'all') {
      currentUrl.searchParams.delete('year');
    } else {
      currentUrl.searchParams.set('year', selectedYear);
    }
  }

  // Reset to page 1 when filtering in server-side pagination mode
  if (isPaginationMode()) {
    currentUrl.searchParams.set('page', '1');
  }

  // Navigate to updated URL (reload page with new filters)
  // This works for both pagination and client-side modes
  // because backend applies filters even in client-side mode
  window.location.href = currentUrl.toString();
}

// Legacy function for compatibility
function filterByOwner() {
  applyFilters();
}

// Initialize filter and sort states for minifigures page
function initializeCollapsibleStates() {
  initializePageCollapsibleStates('minifigures');
}

// Keep filters expanded after selection
function applyFiltersAndKeepOpen() {
  preserveCollapsibleStateOnChange('table-filter', 'minifigures-filter-state');
  applyFilters();
}

// Legacy function for compatibility
function filterByOwnerAndKeepOpen() {
  applyFiltersAndKeepOpen();
}

// Setup table search and sort functionality
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById('table-search');
  const searchClear = document.getElementById('table-search-clear');

  // Initialize collapsible states (filter and sort)
  initializeCollapsibleStates();

  if (searchInput && searchClear) {
    if (isPaginationMode()) {
      // PAGINATION MODE - Server-side search
      const searchForm = document.createElement('form');
      searchForm.style.display = 'none';
      searchInput.parentNode.appendChild(searchForm);
      searchForm.appendChild(searchInput.cloneNode(true));

      // Handle Enter key for search
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          performServerSearch();
        }
      });

      // Handle search button click (if exists)
      const searchButton = document.querySelector('[data-search-trigger]');
      if (searchButton) {
        searchButton.addEventListener('click', performServerSearch);
      }

      // Clear search
      searchClear.addEventListener('click', () => {
        searchInput.value = '';
        performServerSearch();
      });

      function performServerSearch() {
        const currentUrl = new URL(window.location);
        const searchQuery = searchInput.value.trim();

        if (searchQuery) {
          currentUrl.searchParams.set('search', searchQuery);
        } else {
          currentUrl.searchParams.delete('search');
        }

        // Reset to page 1 when searching
        currentUrl.searchParams.set('page', '1');
        window.location.href = currentUrl.toString();
      }

    } else {
      // ORIGINAL MODE - Client-side search with Simple DataTables
      setTimeout(() => {
        const tableElement = document.querySelector('table[data-table="true"]');
        if (tableElement && window.brickTableInstance) {
          // Enable custom search for minifigures table
          window.brickTableInstance.table.searchable = true;

          // Connect search input to table
          searchInput.addEventListener('input', (e) => {
            window.brickTableInstance.table.search(e.target.value);
          });

          // Clear search
          searchClear.addEventListener('click', () => {
            searchInput.value = '';
            window.brickTableInstance.table.search('');
          });
        }
      }, 100);
    }
  }

  // Setup sort buttons for both modes
  setupSortButtons();

  // Initialize sort button states and icons for pagination mode
  if (isPaginationMode()) {
    const urlParams = new URLSearchParams(window.location.search);
    const currentSort = urlParams.get('sort');
    const currentOrder = urlParams.get('order');
    window.initializeSortButtonStates(currentSort, currentOrder);
  }

  // Initialize clear filters button
  const clearButton = document.getElementById('table-filter-clear');
  if (clearButton) {
    clearButton.addEventListener('click', () => {
      window.clearPageFilters('minifigures', ['owner', 'problems', 'theme', 'year']);
    });
  }
});

function setupSortButtons() {
  const columnMap = {
    'name': 1,
    'parts': 2,
    'quantity': 3,
    'missing': 4,
    'damaged': 5,
    'sets': 6
  };
  // Use shared sort buttons setup from collapsible-state.js
  window.setupSharedSortButtons('minifigures', 'brickTableInstance', columnMap);
}