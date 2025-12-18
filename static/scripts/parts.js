// Parts page functionality - now uses shared functions

// Keep filters expanded after selection
function applyFiltersAndKeepOpen() {
  window.applyFiltersAndKeepState('parts', 'parts-filter-state');
}

// Initialize parts page
document.addEventListener("DOMContentLoaded", () => {
  // Use shared table page initialization
  window.initializeTablePage({
    pagePrefix: 'parts',
    tableId: 'parts',
    tableInstanceGlobal: 'partsTableInstance',
    sortColumnMap: {
      'name': 1,
      'color': 2,
      'quantity': 3,
      'missing': 4,
      'damaged': 5,
      'sets': 6,
      'minifigures': 7
    },
    hasColorDropdown: true
  });

  // Initialize clear filters button
  const clearButton = document.getElementById('table-filter-clear');
  if (clearButton) {
    clearButton.addEventListener('click', () => {
      window.clearPageFilters('parts', ['owner', 'color', 'theme', 'year']);
    });
  }
});

