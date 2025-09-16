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

function setupColorDropdown() {
  const colorSelect = document.getElementById('filter-color');
  if (!colorSelect) return;

  // Add color squares to option text
  const options = colorSelect.querySelectorAll('option[data-color-rgb]');
  options.forEach(option => {
    const colorRgb = option.dataset.colorRgb;
    const colorId = option.dataset.colorId;
    const colorName = option.textContent.trim();

    if (colorRgb && colorId !== '9999') {
      // Create a visual indicator (using Unicode square)
      option.textContent = `${colorName}`; //■
      //option.style.color = `#${colorRgb}`;
    }
  });
}

// Keep filters expanded after selection
function applyFiltersAndKeepOpen() {
  // Remember if filters were open
  const filterSection = document.getElementById('table-filter');
  const wasOpen = filterSection && filterSection.classList.contains('show');

  applyFilters();

  // Store the state to restore after page reload
  if (wasOpen) {
    sessionStorage.setItem('keepFiltersOpen', 'true');
  }
}

function setupSortButtons() {
  // Sort button functionality
  const sortButtons = document.querySelectorAll('[data-sort-attribute]');
  const clearButton = document.querySelector('[data-sort-clear]');

  sortButtons.forEach(button => {
    button.addEventListener('click', () => {
      const attribute = button.dataset.sortAttribute;
      const isDesc = button.dataset.sortDesc === 'true';

      if (isPaginationMode()) {
        // PAGINATION MODE - Server-side sorting via URL parameters
        const currentUrl = new URL(window.location);

        // Determine sort direction
        const currentSort = currentUrl.searchParams.get('sort');
        const currentOrder = currentUrl.searchParams.get('order');
        const isCurrentlyActive = currentSort === attribute;

        let newDirection;
        if (isCurrentlyActive) {
          // Toggle direction if same attribute
          newDirection = currentOrder === 'asc' ? 'desc' : 'asc';
        } else {
          // Use default direction for new attribute
          newDirection = isDesc ? 'desc' : 'asc';
        }

        // Set sort parameters and reset to first page
        currentUrl.searchParams.set('sort', attribute);
        currentUrl.searchParams.set('order', newDirection);
        currentUrl.searchParams.set('page', '1');

        // Navigate to sorted results
        window.location.href = currentUrl.toString();

      } else {
        // ORIGINAL MODE - Client-side sorting via Simple DataTables
        // Get column index based on attribute
        const columnMap = {
          'name': 1,
          'color': 2,
          'quantity': 3,
          'missing': 4,
          'damaged': 5,
          'sets': 6,
          'minifigures': 7
        };

        const columnIndex = columnMap[attribute];
        if (columnIndex !== undefined && window.partsTableInstance) {
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
          window.partsTableInstance.table.columns.sort(columnIndex, newDirection);
        }
      }
    });
  });

  if (clearButton) {
    clearButton.addEventListener('click', () => {
      if (isPaginationMode()) {
        // PAGINATION MODE - Clear server-side sorting via URL parameters
        const currentUrl = new URL(window.location);
        currentUrl.searchParams.delete('sort');
        currentUrl.searchParams.delete('order');
        currentUrl.searchParams.set('page', '1');
        window.location.href = currentUrl.toString();

      } else {
        // ORIGINAL MODE - Clear client-side sorting
        // Clear all sort buttons
        sortButtons.forEach(btn => {
          btn.classList.remove('btn-primary');
          btn.classList.add('btn-outline-primary');
          btn.removeAttribute('data-current-direction');
        });

        // Reset table sort - remove all sorting
        if (window.partsTableInstance) {
          // Destroy and recreate to clear sorting
          const tableElement = document.querySelector('#parts');
          const currentPerPage = window.partsTableInstance.table.options.perPage;
          window.partsTableInstance.table.destroy();

          setTimeout(() => {
            // Create new instance using the globally available BrickTable class
            const newInstance = new window.BrickTable(tableElement, currentPerPage);
            window.partsTableInstance = newInstance;

            // Re-enable search functionality
            newInstance.table.searchable = true;
          }, 50);
        }
      }
    });
  }
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

  // Setup color dropdown with color squares
  setupColorDropdown();

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

