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

  // Setup sort and filter functionality (from parts.js)
  setupSortButtons();
  setupColorDropdown();

  // Restore filter state if needed
  const keepFiltersOpen = sessionStorage.getItem('keepFiltersOpen');
  if (keepFiltersOpen === 'true') {
    const filterSection = document.getElementById('table-filter');
    if (filterSection && !filterSection.classList.contains('show')) {
      filterSection.classList.add('show');
    }
    sessionStorage.removeItem('keepFiltersOpen');
  }

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