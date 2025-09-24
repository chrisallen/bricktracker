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

// Check if pagination mode is enabled for a specific table
function isPaginationModeForTable(tableId) {
  const tableElement = document.querySelector(`#${tableId}`);
  return tableElement && tableElement.getAttribute('data-table') === 'false';
}

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