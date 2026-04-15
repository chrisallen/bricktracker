// Problems page functionality - now uses shared functions

// Keep filters expanded after selection
function applyFiltersAndKeepOpen() {
  window.applyFiltersAndKeepState('problems', 'problems-filter-state');
}

// Initialize problems page
document.addEventListener("DOMContentLoaded", () => {
  // Use shared table page initialization
  window.initializeTablePage({
    pagePrefix: 'problems',
    tableId: 'problems',
    tableInstanceGlobal: 'problemsTableInstance',
    sortColumnMap: {
      'name': 1,
      'color': 2,
      //'quantity': 3,
      'missing': 3,
      'damaged': 4,
      'sets': 5,
      'minifigures': 6
    },
    hasColorDropdown: true
  });

  // Initialize clear filters button
  const clearButton = document.getElementById('table-filter-clear');
  if (clearButton) {
    clearButton.addEventListener('click', () => {
      window.clearPageFilters('problems', ['owner', 'color', 'theme', 'year', 'storage', 'tag']);
    });
  }
});