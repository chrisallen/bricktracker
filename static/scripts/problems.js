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
      'quantity': 3,
      'missing': 4,
      'damaged': 5,
      'sets': 6,
      'minifigures': 7
    },
    hasColorDropdown: true
  });
});