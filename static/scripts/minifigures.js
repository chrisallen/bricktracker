// Minifigures page functionality

// Check if we're in pagination mode (server-side) or original mode (client-side)
function isPaginationMode() {
  const tableElement = document.querySelector('#minifigures');
  return tableElement && tableElement.getAttribute('data-table') === 'false';
}

function filterByOwner() {
  const select = document.getElementById('filter-owner');
  const selectedOwner = select.value;
  const currentUrl = new URL(window.location);

  if (selectedOwner === 'all') {
    currentUrl.searchParams.delete('owner');
  } else {
    currentUrl.searchParams.set('owner', selectedOwner);
  }

  // Reset to page 1 when filtering
  if (isPaginationMode()) {
    currentUrl.searchParams.set('page', '1');
  }

  window.location.href = currentUrl.toString();
}

// Initialize filter and sort states for minifigures page
function initializeCollapsibleStates() {
  initializePageCollapsibleStates('minifigures');
}

// Keep filters expanded after selection
function filterByOwnerAndKeepOpen() {
  preserveCollapsibleStateOnChange('table-filter', 'minifigures-filter-state');
  filterByOwner();
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