// Minifigures page functionality
function filterByOwner() {
  const select = document.getElementById('filter-owner');
  const selectedOwner = select.value;
  const currentUrl = new URL(window.location);

  if (selectedOwner === 'all') {
    currentUrl.searchParams.delete('owner');
  } else {
    currentUrl.searchParams.set('owner', selectedOwner);
  }

  window.location.href = currentUrl.toString();
}

// Keep filters expanded after selection
function filterByOwnerAndKeepOpen() {
  // Remember if filters were open
  const filterSection = document.getElementById('table-filter');
  const wasOpen = filterSection && filterSection.classList.contains('show');

  filterByOwner();

  // Store the state to restore after page reload
  if (wasOpen) {
    sessionStorage.setItem('keepFiltersOpen', 'true');
  }
}

// Setup table search and sort functionality
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById('table-search');
  const searchClear = document.getElementById('table-search-clear');

  // Restore filter state after page load
  if (sessionStorage.getItem('keepFiltersOpen') === 'true') {
    const filterSection = document.getElementById('table-filter');
    const filterButton = document.querySelector('[data-bs-target="#table-filter"]');

    if (filterSection && filterButton) {
      filterSection.classList.add('show');
      filterButton.setAttribute('aria-expanded', 'true');
    }

    sessionStorage.removeItem('keepFiltersOpen');
  }

  if (searchInput && searchClear) {
    // Wait for table to be initialized by setup_tables
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

        // Setup sort buttons
        setupSortButtons();
      }
    }, 100);
  }
});

function setupSortButtons() {
  // Sort button functionality
  const sortButtons = document.querySelectorAll('[data-sort-attribute]');
  const clearButton = document.querySelector('[data-sort-clear]');

  sortButtons.forEach(button => {
    button.addEventListener('click', () => {
      const attribute = button.dataset.sortAttribute;
      const isDesc = button.dataset.sortDesc === 'true';

      // Get column index based on attribute
      const columnMap = {
        'name': 1,
        'parts': 2,
        'quantity': 3,
        'missing': 4,
        'damaged': 5,
        'sets': 6
      };

      const columnIndex = columnMap[attribute];
      if (columnIndex !== undefined && window.brickTableInstance) {
        // Determine sort direction
        const isCurrentlyActive = button.classList.contains('btn-primary');
        const currentDirection = button.dataset.currentDirection || (isDesc ? 'desc' : 'asc');
        const newDirection = isCurrentlyActive ?
          (currentDirection === 'asc' ? 'desc' : 'asc') :
          (isDesc ? 'desc' : 'asc');

        // Clear other active buttons
        sortButtons.forEach(btn => {
          btn.classList.remove('btn-primary');
          btn.classList.add('btn-outline-primary');
          btn.removeAttribute('data-current-direction');
        });

        // Mark this button as active
        button.classList.remove('btn-outline-primary');
        button.classList.add('btn-primary');
        button.dataset.currentDirection = newDirection;

        // Apply sort using Simple DataTables API
        window.brickTableInstance.table.columns.sort(columnIndex, newDirection);
      }
    });
  });

  if (clearButton) {
    clearButton.addEventListener('click', () => {
      // Clear all sort buttons
      sortButtons.forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
        btn.removeAttribute('data-current-direction');
      });

      // Reset table sort - remove all sorting
      if (window.brickTableInstance) {
        // Destroy and recreate to clear sorting
        const tableElement = document.querySelector('#minifigures');
        const currentPerPage = window.brickTableInstance.table.options.perPage;
        window.brickTableInstance.table.destroy();

        setTimeout(() => {
          // Create new instance using the globally available BrickTable class
          const newInstance = new window.BrickTable(tableElement, currentPerPage);
          window.brickTableInstance = newInstance;

          // Re-enable search functionality
          newInstance.table.searchable = true;
        }, 50);
      }
    });
  }
}