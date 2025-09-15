// Parts page functionality
function applyFilters() {
  const ownerSelect = document.getElementById('filter-owner');
  const colorSelect = document.getElementById('filter-color');
  const currentUrl = new URL(window.location);

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
    // Wait for table to be initialized by setup_tables
    const setupSearch = () => {
      const tableElement = document.querySelector('table[data-table="true"]');
      if (tableElement && window.partsTableInstance) {
        // Enable custom search for parts table
        window.partsTableInstance.table.searchable = true;

        // Connect search input to table
        searchInput.addEventListener('input', (e) => {
          window.partsTableInstance.table.search(e.target.value);
        });

        // Clear search
        searchClear.addEventListener('click', () => {
          searchInput.value = '';
          window.partsTableInstance.table.search('');
        });

        // Setup sort buttons
        setupSortButtons();
      } else {
        // If table instance not ready, try again
        setTimeout(setupSearch, 100);
      }
    };

    setTimeout(setupSearch, 100);
  }
});