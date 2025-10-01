// Sets page functionality

// Check if we're in pagination mode (server-side) or original mode (client-side)
function isPaginationMode() {
  const gridElement = document.querySelector('#grid');
  return gridElement && gridElement.getAttribute('data-grid') === 'false';
}

// Initialize filter and sort states for sets page
function initializeCollapsibleStates() {
  initializePageCollapsibleStates('sets', 'grid-filter', 'grid-sort');
}

// Setup page functionality
document.addEventListener("DOMContentLoaded", () => {
  // Initialize collapsible states (filter and sort)
  initializeCollapsibleStates();

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

      // Setup filter dropdowns for pagination mode
      setupPaginationFilterDropdowns();

      // Initialize sort button states and icons for pagination mode
      const urlParams = new URLSearchParams(window.location.search);
      const currentSort = urlParams.get('sort');
      const currentOrder = urlParams.get('order');
      window.initializeSortButtonStates(currentSort, currentOrder);

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

      // Update sort icon immediately before navigation
      updateSortIcon(newOrder);

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

      // Reset sort icon to default ascending
      updateSortIcon('asc');

      currentUrl.searchParams.set('page', '1');
      window.location.href = currentUrl.toString();
    });
  }
}

function setupPaginationFilterDropdowns() {
  // Filter dropdown functionality for pagination mode
  const filterDropdowns = document.querySelectorAll('#grid-filter select');

  filterDropdowns.forEach(dropdown => {
    dropdown.addEventListener('change', () => {
      performServerFilter();
    });
  });

  function performServerFilter() {
    const currentUrl = new URL(window.location);

    // Get all filter values
    const statusFilter = document.getElementById('grid-status')?.value || '';
    const themeFilter = document.getElementById('grid-theme')?.value || '';
    const ownerFilter = document.getElementById('grid-owner')?.value || '';
    const purchaseLocationFilter = document.getElementById('grid-purchase-location')?.value || '';
    const storageFilter = document.getElementById('grid-storage')?.value || '';
    const tagFilter = document.getElementById('grid-tag')?.value || '';

    // Update URL parameters
    if (statusFilter) {
      currentUrl.searchParams.set('status', statusFilter);
    } else {
      currentUrl.searchParams.delete('status');
    }

    if (themeFilter) {
      currentUrl.searchParams.set('theme', themeFilter);
    } else {
      currentUrl.searchParams.delete('theme');
    }

    if (ownerFilter) {
      currentUrl.searchParams.set('owner', ownerFilter);
    } else {
      currentUrl.searchParams.delete('owner');
    }

    if (purchaseLocationFilter) {
      currentUrl.searchParams.set('purchase_location', purchaseLocationFilter);
    } else {
      currentUrl.searchParams.delete('purchase_location');
    }

    if (storageFilter) {
      currentUrl.searchParams.set('storage', storageFilter);
    } else {
      currentUrl.searchParams.delete('storage');
    }

    if (tagFilter) {
      currentUrl.searchParams.set('tag', tagFilter);
    } else {
      currentUrl.searchParams.delete('tag');
    }

    // Reset to page 1 when filtering
    currentUrl.searchParams.set('page', '1');
    window.location.href = currentUrl.toString();
  }
}

// Set grouping functionality
function initializeSetGrouping() {
  const groupToggle = document.getElementById('group-identical-sets');
  if (!groupToggle) return;

  // Load saved state from localStorage
  const savedState = localStorage.getItem('groupIdenticalSets') === 'true';
  groupToggle.checked = savedState;

  // Apply grouping on page load if enabled
  if (savedState) {
    applySetGrouping();
  }

  // Listen for toggle changes
  groupToggle.addEventListener('change', function() {
    // Save state to localStorage
    localStorage.setItem('groupIdenticalSets', this.checked);

    if (this.checked) {
      applySetGrouping();
    } else {
      removeSetGrouping();
    }
  });
}

function applySetGrouping() {
  const grid = document.getElementById('grid');
  if (!grid) return;

  const setCards = Array.from(grid.children);
  const groupedSets = {};

  // Group sets by rebrickable_set_id
  setCards.forEach(cardCol => {
    const setCard = cardCol.querySelector('.card[data-set-id]');
    if (!setCard) return;

    const setId = setCard.getAttribute('data-set-id');
    const rebrickableId = setCard.getAttribute('data-rebrickable-id');

    if (!rebrickableId) return;

    if (!groupedSets[rebrickableId]) {
      groupedSets[rebrickableId] = [];
    }

    groupedSets[rebrickableId].push({
      cardCol: cardCol,
      setId: setId,
      rebrickableId: rebrickableId
    });
  });

  // Process each group
  Object.keys(groupedSets).forEach(rebrickableId => {
    const group = groupedSets[rebrickableId];

    if (group.length > 1) {
      createGroupedSetDisplay(group);
    }
  });
}

function createGroupedSetDisplay(setGroup) {
  const firstSet = setGroup[0];
  const firstCard = firstSet.cardCol.querySelector('.card');

  if (!firstCard) return;

  // Calculate aggregate stats
  let totalMissing = 0;
  let totalDamaged = 0;
  let allSetIds = [];

  setGroup.forEach(set => {
    const card = set.cardCol.querySelector('.card');

    // Get missing and damaged counts from existing data attributes
    const missingCount = parseInt(card.getAttribute('data-missing') || '0');
    const damagedCount = parseInt(card.getAttribute('data-damaged') || '0');

    totalMissing += missingCount;
    totalDamaged += damagedCount;
    allSetIds.push(set.setId);
  });

  // Create grouped card container
  const groupContainer = document.createElement('div');
  groupContainer.className = firstSet.cardCol.className + ' set-group-container';
  groupContainer.innerHTML = `
    <div class="card set-group-card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
          <button class="btn btn-sm btn-outline-primary me-2 group-toggle-btn"
                  type="button" data-bs-toggle="collapse"
                  data-bs-target="#group-${setGroup[0].rebrickableId}"
                  aria-expanded="false">
            <i class="ri-arrow-right-line"></i>
          </button>
          <span class="fw-bold">${firstCard.querySelector('.card-title')?.textContent || 'Set'}</span>
          <span class="badge bg-secondary ms-2">${setGroup.length} sets</span>
        </div>
        <div class="d-flex gap-1">
          ${totalMissing > 0 ? `<span class="badge bg-warning text-dark">${totalMissing} missing</span>` : ''}
          ${totalDamaged > 0 ? `<span class="badge bg-danger">${totalDamaged} damaged</span>` : ''}
        </div>
      </div>
      <div class="collapse" id="group-${setGroup[0].rebrickableId}">
        <div class="card-body">
          <div class="row set-group-items"></div>
        </div>
      </div>
    </div>
  `;

  // Add individual set cards to the group
  const groupItems = groupContainer.querySelector('.set-group-items');
  setGroup.forEach(set => {
    const itemContainer = document.createElement('div');
    itemContainer.className = 'col-12 mb-2';

    // Clone the original card but make it smaller
    const clonedCard = set.cardCol.querySelector('.card').cloneNode(true);
    clonedCard.classList.add('set-group-item');

    itemContainer.appendChild(clonedCard);
    groupItems.appendChild(itemContainer);

    // Hide the original card
    set.cardCol.style.display = 'none';
    set.cardCol.classList.add('grouped-set-hidden');
  });

  // Insert the grouped container before the first hidden set
  firstSet.cardCol.parentNode.insertBefore(groupContainer, firstSet.cardCol);

  // Add event listener to toggle arrow icon
  const toggleBtn = groupContainer.querySelector('.group-toggle-btn');
  const collapseElement = groupContainer.querySelector('.collapse');

  collapseElement.addEventListener('shown.bs.collapse', () => {
    toggleBtn.querySelector('i').className = 'ri-arrow-down-line';
  });

  collapseElement.addEventListener('hidden.bs.collapse', () => {
    toggleBtn.querySelector('i').className = 'ri-arrow-right-line';
  });
}

function removeSetGrouping() {
  // Show all hidden sets
  const hiddenSets = document.querySelectorAll('.grouped-set-hidden');
  hiddenSets.forEach(setCol => {
    setCol.style.display = '';
    setCol.classList.remove('grouped-set-hidden');
  });

  // Remove all group containers
  const groupContainers = document.querySelectorAll('.set-group-container');
  groupContainers.forEach(container => {
    container.remove();
  });
}