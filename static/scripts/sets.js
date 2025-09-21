// Sets page functionality

// Check if we're in pagination mode (server-side) or original mode (client-side)
function isPaginationMode() {
  const gridElement = document.querySelector('#grid');
  return gridElement && gridElement.getAttribute('data-grid') === 'false';
}

// Filter state management
function initializeFilterState() {
  const filterElement = document.getElementById('grid-filter');
  const filterToggleButton = document.querySelector('[data-bs-target="#grid-filter"]');

  if (!filterElement || !filterToggleButton) return;

  // Key for localStorage specific to sets page
  const FILTER_STATE_KEY = 'sets-filter-state';

  // Restore filter state on page load
  const savedState = localStorage.getItem(FILTER_STATE_KEY);
  if (savedState === 'open') {
    // Override the template state and show the filter
    filterElement.classList.add('show');
    filterToggleButton.setAttribute('aria-expanded', 'true');
  } else if (savedState === 'closed') {
    // Explicitly hide if it was closed by user
    filterElement.classList.remove('show');
    filterToggleButton.setAttribute('aria-expanded', 'false');
  }

  // Listen for filter toggle events
  filterElement.addEventListener('show.bs.collapse', () => {
    localStorage.setItem(FILTER_STATE_KEY, 'open');
  });

  filterElement.addEventListener('hide.bs.collapse', () => {
    localStorage.setItem(FILTER_STATE_KEY, 'closed');
  });

  // Clear state when leaving the page
  window.addEventListener('beforeunload', () => {
    // Only clear if user is navigating away from sets page
    const currentPath = window.location.pathname;
    if (!currentPath.includes('/sets')) {
      localStorage.removeItem(FILTER_STATE_KEY);
    }
  });
}

// Setup page functionality
document.addEventListener("DOMContentLoaded", () => {
  // Initialize filter state management
  initializeFilterState();

  const searchInput = document.getElementById('grid-search');
  const searchClear = document.getElementById('grid-search-clear');

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

      // Setup sort buttons for pagination mode
      setupPaginationSortButtons();

      // Setup filter dropdowns for pagination mode
      setupPaginationFilterDropdowns();

    } else {
      // ORIGINAL MODE - Grid search functionality is handled by existing grid scripts
      // No additional setup needed here
    }
  }
});

function setupPaginationSortButtons() {
  // Sort button functionality for pagination mode
  const sortButtons = document.querySelectorAll('[data-sort-attribute]');
  const clearButton = document.querySelector('[data-sort-clear]');

  sortButtons.forEach(button => {
    button.addEventListener('click', () => {
      const attribute = button.dataset.sortAttribute;
      const isDesc = button.dataset.sortDesc === 'true';

      // PAGINATION MODE - Server-side sorting
      const currentUrl = new URL(window.location);
      const currentSort = currentUrl.searchParams.get('sort');
      const currentOrder = currentUrl.searchParams.get('order');

      // Determine new sort direction
      let newOrder = isDesc ? 'desc' : 'asc';
      if (currentSort === attribute) {
        // Toggle direction if clicking the same column
        newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
      }

      currentUrl.searchParams.set('sort', attribute);
      currentUrl.searchParams.set('order', newOrder);

      // Reset to page 1 when sorting
      currentUrl.searchParams.set('page', '1');
      window.location.href = currentUrl.toString();
    });
  });

  if (clearButton) {
    clearButton.addEventListener('click', () => {
      // PAGINATION MODE - Clear server-side sorting
      const currentUrl = new URL(window.location);
      currentUrl.searchParams.delete('sort');
      currentUrl.searchParams.delete('order');
      currentUrl.searchParams.set('page', '1');
      window.location.href = currentUrl.toString();
    });
  }
}

function setupPaginationFilterDropdowns() {
  // Filter dropdown functionality for pagination mode
  const filterDropdowns = document.querySelectorAll('#grid-filter select');

  filterDropdowns.forEach(dropdown => {
    dropdown.addEventListener('change', () => {
      performServerFilter();
    });
  });

  function performServerFilter() {
    const currentUrl = new URL(window.location);

    // Get all filter values
    const statusFilter = document.getElementById('grid-status')?.value || '';
    const themeFilter = document.getElementById('grid-theme')?.value || '';
    const ownerFilter = document.getElementById('grid-owner')?.value || '';
    const purchaseLocationFilter = document.getElementById('grid-purchase-location')?.value || '';
    const storageFilter = document.getElementById('grid-storage')?.value || '';
    const tagFilter = document.getElementById('grid-tag')?.value || '';

    // Update URL parameters
    if (statusFilter) {
      currentUrl.searchParams.set('status', statusFilter);
    } else {
      currentUrl.searchParams.delete('status');
    }

    if (themeFilter) {
      currentUrl.searchParams.set('theme', themeFilter);
    } else {
      currentUrl.searchParams.delete('theme');
    }

    if (ownerFilter) {
      currentUrl.searchParams.set('owner', ownerFilter);
    } else {
      currentUrl.searchParams.delete('owner');
    }

    if (purchaseLocationFilter) {
      currentUrl.searchParams.set('purchase_location', purchaseLocationFilter);
    } else {
      currentUrl.searchParams.delete('purchase_location');
    }

    if (storageFilter) {
      currentUrl.searchParams.set('storage', storageFilter);
    } else {
      currentUrl.searchParams.delete('storage');
    }

    if (tagFilter) {
      currentUrl.searchParams.set('tag', tagFilter);
    } else {
      currentUrl.searchParams.delete('tag');
    }

    // Reset to page 1 when filtering
    currentUrl.searchParams.set('page', '1');
    window.location.href = currentUrl.toString();
  }
}