/**
 * Shared collapsible state management for filters and sort sections
 * Handles BK_SHOW_GRID_FILTERS and BK_SHOW_GRID_SORT configuration with user preferences
 */

// Generic state management for collapsible sections (filter and sort)
function initializeCollapsibleState(elementId, storageKey) {
  const element = document.getElementById(elementId);
  const toggleButton = document.querySelector(`[data-bs-target="#${elementId}"]`);

  if (!element || !toggleButton) return;

  // Restore state on page load
  const savedState = sessionStorage.getItem(storageKey);
  if (savedState === 'open') {
    // User explicitly opened it
    element.classList.add('show');
    toggleButton.setAttribute('aria-expanded', 'true');
  } else if (savedState === 'closed') {
    // User explicitly closed it, override template state
    element.classList.remove('show');
    toggleButton.setAttribute('aria-expanded', 'false');
  }
  // If no saved state, keep the template state (respects BK_SHOW_GRID_FILTERS/BK_SHOW_GRID_SORT)

  // Listen for toggle events
  element.addEventListener('show.bs.collapse', () => {
    sessionStorage.setItem(storageKey, 'open');
  });

  element.addEventListener('hide.bs.collapse', () => {
    sessionStorage.setItem(storageKey, 'closed');
  });
}

// Initialize filter and sort states for a specific page
function initializePageCollapsibleStates(pagePrefix, filterElementId = 'table-filter', sortElementId = 'table-sort') {
  initializeCollapsibleState(filterElementId, `${pagePrefix}-filter-state`);
  initializeCollapsibleState(sortElementId, `${pagePrefix}-sort-state`);

  // Initialize sort icons based on current URL parameters (for all pages)
  const urlParams = new URLSearchParams(window.location.search);
  const currentSort = urlParams.get('sort');
  const currentOrder = urlParams.get('order');
  if (currentSort || currentOrder) {
    updateSortIcon(currentOrder);
  }
}

// Shared function to preserve filter state during filter changes
function preserveCollapsibleStateOnChange(elementId, storageKey) {
  const element = document.getElementById(elementId);
  const wasOpen = element && element.classList.contains('show');

  // Store the state to restore after page reload
  if (wasOpen) {
    sessionStorage.setItem(storageKey, 'open');
  }
}

// Setup color dropdown with visual indicators (shared implementation)
function setupColorDropdown() {
  const colorSelect = document.getElementById('filter-color');
  if (!colorSelect) return;

  // Merge duplicate color options where one has color_rgb and the other is None
  const colorMap = new Map();
  const allOptions = colorSelect.querySelectorAll('option[data-color-id]');

  // First pass: collect all options by color_id
  allOptions.forEach(option => {
    const colorId = option.dataset.colorId;
    const colorRgb = option.dataset.colorRgb;
    const colorName = option.textContent.trim();

    if (!colorMap.has(colorId)) {
      colorMap.set(colorId, []);
    }
    colorMap.get(colorId).push({
      element: option,
      colorRgb: colorRgb,
      colorName: colorName,
      selected: option.selected
    });
  });

  // Second pass: merge duplicates, keeping the one with color_rgb
  colorMap.forEach((options, colorId) => {
    if (options.length > 1) {
      // Find option with color_rgb (not empty/null/undefined)
      const withRgb = options.find(opt => opt.colorRgb && opt.colorRgb !== 'None' && opt.colorRgb !== '');
      const withoutRgb = options.find(opt => !opt.colorRgb || opt.colorRgb === 'None' || opt.colorRgb === '');

      if (withRgb && withoutRgb) {
        // Keep the selected state from either option
        const wasSelected = withRgb.selected || withoutRgb.selected;

        // Update the option with RGB to be selected if either was selected
        if (wasSelected) {
          withRgb.element.selected = true;
        }

        // Remove the option without RGB
        withoutRgb.element.remove();
      }
    }
  });

  // Add color squares to remaining option text
  const remainingOptions = colorSelect.querySelectorAll('option[data-color-rgb]');
  remainingOptions.forEach(option => {
    const colorRgb = option.dataset.colorRgb;
    const colorId = option.dataset.colorId;
    const colorName = option.textContent.trim();

    if (colorRgb && colorRgb !== 'None' && colorRgb !== '' && colorId !== '9999') {
      // Create a visual indicator (using Unicode square)
      option.textContent = `${colorName}`; //■
      //option.style.color = `#${colorRgb}`;
    }
  });
}

// Check if pagination mode is enabled for a specific table
function isPaginationModeForTable(tableId) {
  const tableElement = document.querySelector(`#${tableId}`);
  return tableElement && tableElement.getAttribute('data-table') === 'false';
}

// Update sort icon based on current sort direction
function updateSortIcon(sortDirection = null) {
  // Find the main sort icon (could be in grid-sort or table-sort)
  const sortIcon = document.querySelector('#grid-sort .ri-sort-asc, #grid-sort .ri-sort-desc, #table-sort .ri-sort-asc, #table-sort .ri-sort-desc');

  if (!sortIcon) return;

  // Remove existing sort classes
  sortIcon.classList.remove('ri-sort-asc', 'ri-sort-desc');

  // Add appropriate class based on sort direction
  if (sortDirection === 'desc') {
    sortIcon.classList.add('ri-sort-desc');
  } else {
    sortIcon.classList.add('ri-sort-asc');
  }
}

// Initialize sort button states and icons for pagination mode
window.initializeSortButtonStates = function(currentSort, currentOrder) {
  const sortButtons = document.querySelectorAll('[data-sort-attribute]');

  // Update main sort icon
  updateSortIcon(currentOrder);

  if (currentSort) {
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
};

// Shared sort button setup function
window.setupSharedSortButtons = function(tableId, tableInstanceGlobal, columnMap) {
  const sortButtons = document.querySelectorAll('[data-sort-attribute]');
  const clearButton = document.querySelector('[data-sort-clear]');
  const isPaginationMode = isPaginationModeForTable(tableId);

  sortButtons.forEach(button => {
    button.addEventListener('click', () => {
      const attribute = button.dataset.sortAttribute;
      const isDesc = button.dataset.sortDesc === 'true';

      if (isPaginationMode) {
        // PAGINATION MODE - Server-side sorting via URL parameters
        const currentUrl = new URL(window.location);
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
        const columnIndex = columnMap[attribute];
        const tableInstance = window[tableInstanceGlobal];

        if (columnIndex !== undefined && tableInstance) {
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
          tableInstance.table.columns.sort(columnIndex, newDirection);

          // Update sort icon to reflect new direction
          updateSortIcon(newDirection);
        }
      }
    });
  });

  if (clearButton) {
    clearButton.addEventListener('click', () => {
      if (isPaginationMode) {
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

        // Reset sort icon to default ascending
        updateSortIcon('asc');

        // Reset table sort - remove all sorting
        const tableInstance = window[tableInstanceGlobal];
        if (tableInstance) {
          const tableElement = document.querySelector(`#${tableId}`);
          const currentPerPage = tableInstance.table.options.perPage;
          tableInstance.table.destroy();

          setTimeout(() => {
            // Create new instance using the globally available BrickTable class
            const newInstance = new window.BrickTable(tableElement, currentPerPage);
            window[tableInstanceGlobal] = newInstance;

            // Re-enable search functionality
            newInstance.table.searchable = true;
          }, 50);
        }
      }
    });
  }
};

// =================================================================
// SHARED FUNCTIONS FOR PAGE-SPECIFIC OPERATIONS
// =================================================================

// Shared pagination mode detection (works for any table/grid ID)
window.isPaginationModeForPage = function(elementId, attributeName = 'data-table') {
  const element = document.querySelector(`#${elementId}`);
  return element && element.getAttribute(attributeName) === 'false';
};

// Shared URL parameter update helper
window.updateUrlParams = function(params, resetPage = true) {
  const currentUrl = new URL(window.location);

  // Apply parameter updates
  Object.entries(params).forEach(([key, value]) => {
    if (value === null || value === undefined || value === '' || value === 'all') {
      currentUrl.searchParams.delete(key);
    } else {
      currentUrl.searchParams.set(key, value);
    }
  });

  // Reset to page 1 if requested
  if (resetPage) {
    currentUrl.searchParams.set('page', '1');
  }

  // Navigate to updated URL
  window.location.href = currentUrl.toString();
};

// Shared filter application (supports owner, color, theme, year, and problems filters)
window.applyPageFilters = function(tableId) {
  const ownerSelect = document.getElementById('filter-owner');
  const colorSelect = document.getElementById('filter-color');
  const themeSelect = document.getElementById('filter-theme');
  const yearSelect = document.getElementById('filter-year');
  const problemsSelect = document.getElementById('filter-problems');
  const params = {};

  // Handle owner filter
  if (ownerSelect) {
    params.owner = ownerSelect.value;
  }

  // Handle color filter
  if (colorSelect) {
    params.color = colorSelect.value;
  }

  // Handle theme filter
  if (themeSelect) {
    params.theme = themeSelect.value;
  }

  // Handle year filter
  if (yearSelect) {
    params.year = yearSelect.value;
  }

  // Handle problems filter (for minifigures page)
  if (problemsSelect) {
    params.problems = problemsSelect.value;
  }

  // Update URL with new parameters
  window.updateUrlParams(params, true);
};

// Shared search setup for both pagination and client-side modes
window.setupPageSearch = function(tableId, searchInputId, clearButtonId, tableInstanceGlobal) {
  const searchInput = document.getElementById(searchInputId);
  const searchClear = document.getElementById(clearButtonId);

  if (!searchInput || !searchClear) return;

  const isPaginationMode = window.isPaginationModeForPage(tableId);

  if (isPaginationMode) {
    // PAGINATION MODE - Server-side search with Enter key
    searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const searchValue = e.target.value.trim();
        window.updateUrlParams({ search: searchValue }, true);
      }
    });

    // Clear search
    searchClear.addEventListener('click', () => {
      searchInput.value = '';
      window.updateUrlParams({ search: null }, true);
    });

  } else {
    // ORIGINAL MODE - Client-side instant search via Simple DataTables
    const setupClientSearch = () => {
      const tableElement = document.querySelector(`table[data-table="true"]#${tableId}`);
      const tableInstance = window[tableInstanceGlobal];

      if (tableElement && tableInstance) {
        // Enable search functionality
        tableInstance.table.searchable = true;

        // Instant search as user types
        searchInput.addEventListener('input', (e) => {
          const searchValue = e.target.value.trim();
          tableInstance.table.search(searchValue);
        });

        // Clear search
        searchClear.addEventListener('click', () => {
          searchInput.value = '';
          tableInstance.table.search('');
        });
      } else {
        // If table instance not ready, try again
        setTimeout(setupClientSearch, 100);
      }
    };

    setTimeout(setupClientSearch, 100);
  }
};

// Shared function to preserve filter state and apply filters
window.applyFiltersAndKeepState = function(tableId, storageKey) {
  const filterElement = document.getElementById('table-filter');
  const wasOpen = filterElement && filterElement.classList.contains('show');

  // Apply the filters
  window.applyPageFilters(tableId);

  // Store the state to restore after page reload
  if (wasOpen) {
    sessionStorage.setItem(storageKey, 'open');
  }
};

// Shared initialization for table pages (parts, problems, minifigures)
window.initializeTablePage = function(config) {
  const {
    pagePrefix,         // e.g., 'parts', 'problems', 'minifigures'
    tableId,           // e.g., 'parts', 'problems', 'minifigures'
    searchInputId = 'table-search',
    clearButtonId = 'table-search-clear',
    tableInstanceGlobal, // e.g., 'partsTableInstance', 'problemsTableInstance'
    sortColumnMap,      // Column mapping for sort buttons
    hasColorDropdown = true
  } = config;

  // Initialize collapsible states (filter and sort)
  initializePageCollapsibleStates(pagePrefix);

  // Setup search functionality
  window.setupPageSearch(tableId, searchInputId, clearButtonId, tableInstanceGlobal);

  // Setup color dropdown if needed
  if (hasColorDropdown) {
    setupColorDropdown();
  }

  // Setup sort buttons with shared functionality
  if (sortColumnMap) {
    window.setupSharedSortButtons(tableId, tableInstanceGlobal, sortColumnMap);
  }

  // Initialize sort button states and icons for pagination mode
  if (window.isPaginationModeForPage(tableId)) {
    const urlParams = new URLSearchParams(window.location.search);
    const currentSort = urlParams.get('sort');
    const currentOrder = urlParams.get('order');
    window.initializeSortButtonStates(currentSort, currentOrder);
  }
};