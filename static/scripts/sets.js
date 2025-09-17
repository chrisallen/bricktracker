// Sets page functionality

// Check if we're in pagination mode (server-side) or original mode (client-side)
function isPaginationMode() {
  const gridElement = document.querySelector('#grid');
  return gridElement && gridElement.getAttribute('data-grid') === 'false';
}

// Setup page functionality
document.addEventListener("DOMContentLoaded", () => {
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