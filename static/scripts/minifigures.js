// Minifigures page functionality - now uses shared functions

// Check if we're in pagination mode (server-side) or original mode (client-side)
function isPaginationMode() {
  const tableElement = document.querySelector('#minifigures');
  return tableElement && tableElement.getAttribute('data-table') === 'false';
}

// Keep filters expanded after selection
function applyFiltersAndKeepOpen() {
  window.applyFiltersAndKeepState('minifigures', 'minifigures-filter-state');
}

// Initialize individuals filter functionality
function initializeIndividualsFilter() {
  const individualsFilterButton = document.getElementById('individuals-filter-toggle');
  if (!individualsFilterButton) return;

  // Check if the filter should be active from URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const isIndividualsFilterActive = urlParams.get('individuals') === 'only';

  // Set initial button state
  if (isIndividualsFilterActive) {
    individualsFilterButton.classList.remove('btn-outline-secondary');
    individualsFilterButton.classList.add('btn-secondary');
  }

  individualsFilterButton.addEventListener('click', () => {
    const isCurrentlyActive = individualsFilterButton.classList.contains('btn-secondary');
    const newState = !isCurrentlyActive;

    // Update button appearance
    if (newState) {
      individualsFilterButton.classList.remove('btn-outline-secondary');
      individualsFilterButton.classList.add('btn-secondary');
    } else {
      individualsFilterButton.classList.remove('btn-secondary');
      individualsFilterButton.classList.add('btn-outline-secondary');
    }

    // Update URL parameter and reload
    const currentUrl = new URL(window.location);

    if (newState) {
      currentUrl.searchParams.set('individuals', 'only');
    } else {
      currentUrl.searchParams.delete('individuals');
    }

    // Reset to page 1 when filtering in server-side pagination mode
    if (isPaginationMode()) {
      currentUrl.searchParams.set('page', '1');
    }

    // Navigate to updated URL
    window.location.href = currentUrl.toString();
  });
}

// Initialize minifigures page
document.addEventListener("DOMContentLoaded", () => {
  // Use shared table page initialization (search, sort buttons, collapsible states)
  window.initializeTablePage({
    pagePrefix: 'minifigures',
    tableId: 'minifigures',
    tableInstanceGlobal: 'brickTableInstance',
    sortColumnMap: {
      'name': 1,
      'parts': 2,
      'quantity': 3,
      'missing': 4,
      'damaged': 5,
      'sets': 6
    },
    hasColorDropdown: false
  });

  // Initialize individuals filter
  initializeIndividualsFilter();

  // Initialize clear filters button
  const clearButton = document.getElementById('table-filter-clear');
  if (clearButton) {
    clearButton.addEventListener('click', () => {
      window.clearPageFilters('minifigures', ['owner', 'problems', 'theme', 'year', 'individuals']);
    });
  }
});
