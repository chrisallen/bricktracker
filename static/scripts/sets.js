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

  // Initialize duplicate filter functionality
  initializeDuplicateFilter();

  // Initialize clear filters button
  initializeClearFiltersButton();

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

      // Initialize filter dropdowns from URL parameters
      initializeFilterDropdowns();

      // Initialize sort button states and icons for pagination mode
      const urlParams = new URLSearchParams(window.location.search);
      const currentSort = urlParams.get('sort');
      const currentOrder = urlParams.get('order');
      window.initializeSortButtonStates(currentSort, currentOrder);

    } else {
      // ORIGINAL MODE - Client-side filtering with grid scripts
      // Initialize filter dropdowns from URL parameters for client-side mode too
      initializeClientSideFilterDropdowns();
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

function initializeFilterDropdowns() {
  // Set filter dropdown values from URL parameters
  const urlParams = new URLSearchParams(window.location.search);

  // Set each filter dropdown value if the parameter exists
  const yearParam = urlParams.get('year');
  if (yearParam) {
    const yearDropdown = document.getElementById('grid-year');
    if (yearDropdown) {
      yearDropdown.value = yearParam;
    }
  }

  const themeParam = urlParams.get('theme');
  if (themeParam) {
    const themeDropdown = document.getElementById('grid-theme');
    if (themeDropdown) {
      // Try to set the theme value directly first (for theme names)
      themeDropdown.value = themeParam;

      // If that didn't work and the param is numeric (theme ID),
      // try to find the corresponding theme name by looking at cards
      if (themeDropdown.value !== themeParam && /^\d+$/.test(themeParam)) {
        // Look for a card with this theme ID and get its theme name
        const cardWithTheme = document.querySelector(`[data-theme-id="${themeParam}"]`);
        if (cardWithTheme) {
          const themeName = cardWithTheme.getAttribute('data-theme');
          if (themeName) {
            themeDropdown.value = themeName;
          }
        }
      }
    }
  }

  const statusParam = urlParams.get('status');
  if (statusParam) {
    const statusDropdown = document.getElementById('grid-status');
    if (statusDropdown) {
      statusDropdown.value = statusParam;
    }
  }

  const ownerParam = urlParams.get('owner');
  if (ownerParam) {
    const ownerDropdown = document.getElementById('grid-owner');
    if (ownerDropdown) {
      ownerDropdown.value = ownerParam;
    }
  }

  const purchaseLocationParam = urlParams.get('purchase_location');
  if (purchaseLocationParam) {
    const purchaseLocationDropdown = document.getElementById('grid-purchase-location');
    if (purchaseLocationDropdown) {
      purchaseLocationDropdown.value = purchaseLocationParam;
    }
  }

  const storageParam = urlParams.get('storage');
  if (storageParam) {
    const storageDropdown = document.getElementById('grid-storage');
    if (storageDropdown) {
      storageDropdown.value = storageParam;
    }
  }

  const tagParam = urlParams.get('tag');
  if (tagParam) {
    const tagDropdown = document.getElementById('grid-tag');
    if (tagDropdown) {
      tagDropdown.value = tagParam;
    }
  }
}

function initializeClientSideFilterDropdowns() {
  // Set filter dropdown values from URL parameters and trigger filtering for client-side mode
  const urlParams = new URLSearchParams(window.location.search);
  let needsFiltering = false;

  // Check if we have any filter parameters to avoid flash of all content
  const hasFilterParams = urlParams.has('year') || urlParams.has('theme') || urlParams.has('storage') || urlParams.has('purchase_location');

  // If we have filter parameters, temporarily hide the grid to prevent flash
  if (hasFilterParams) {
    const gridElement = document.querySelector('#grid');
    if (gridElement && gridElement.getAttribute('data-grid') === 'true') {
      gridElement.style.opacity = '0';
    }
  }

  // Set year filter if parameter exists
  const yearParam = urlParams.get('year');
  if (yearParam) {
    const yearDropdown = document.getElementById('grid-year');
    if (yearDropdown) {
      yearDropdown.value = yearParam;
      needsFiltering = true;
    }
  }

  // Set theme filter - handle both theme names and theme IDs
  const themeParam = urlParams.get('theme');
  if (themeParam) {
    const themeDropdown = document.getElementById('grid-theme');
    if (themeDropdown) {
      if (/^\d+$/.test(themeParam)) {
        // Theme parameter is an ID, need to convert to theme name by looking at cards
        const themeNameFromId = findThemeNameById(themeParam);
        if (themeNameFromId) {
          themeDropdown.value = themeNameFromId;
          needsFiltering = true;
        }
      } else {
        // Theme parameter is already a name
        themeDropdown.value = themeParam.toLowerCase();
        needsFiltering = true;
      }
    }
  }

  // Set storage filter if parameter exists
  const storageParam = urlParams.get('storage');
  if (storageParam) {
    const storageDropdown = document.getElementById('grid-storage');
    if (storageDropdown) {
      storageDropdown.value = storageParam;
      needsFiltering = true;
    }
  }

  // Set purchase location filter if parameter exists
  const purchaseLocationParam = urlParams.get('purchase_location');
  if (purchaseLocationParam) {
    const purchaseLocationDropdown = document.getElementById('grid-purchase-location');
    if (purchaseLocationDropdown) {
      purchaseLocationDropdown.value = purchaseLocationParam;
      needsFiltering = true;
    }
  }

  // Trigger filtering if any parameters were set
  if (needsFiltering) {
    // Try to trigger filtering immediately
    const tryToFilter = () => {
      const gridElement = document.querySelector('#grid');
      if (gridElement && gridElement.getAttribute('data-grid') === 'true' && window.gridInstances) {
        const gridInstance = window.gridInstances[gridElement.id];
        if (gridInstance && gridInstance.filter) {
          // This is client-side mode, trigger the filter directly
          gridInstance.filter.filter();

          // Show the grid again after filtering
          if (hasFilterParams) {
            gridElement.style.opacity = '1';
            gridElement.style.transition = 'opacity 0.2s ease-in-out';
          }

          return true;
        }
      }
      return false;
    };

    // Try filtering immediately
    if (!tryToFilter()) {
      // If not ready, try again with a shorter delay
      setTimeout(() => {
        if (!tryToFilter()) {
          // Final attempt with longer delay
          setTimeout(tryToFilter, 100);
        }
      }, 50);
    }
  }
}

function findThemeNameById(themeId) {
  // Look through all cards to find the theme name for this theme ID
  const cards = document.querySelectorAll('.card[data-theme-id]');
  for (const card of cards) {
    if (card.getAttribute('data-theme-id') === themeId) {
      return card.getAttribute('data-theme');
    }
  }
  return null;
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
    const yearFilter = document.getElementById('grid-year')?.value || '';
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

    if (yearFilter) {
      currentUrl.searchParams.set('year', yearFilter);
    } else {
      currentUrl.searchParams.delete('year');
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

// Initialize duplicate/consolidated filter functionality
function initializeDuplicateFilter() {
  const duplicateFilterButton = document.getElementById('duplicate-filter-toggle');
  if (!duplicateFilterButton) return;

  // Check if the filter should be active from URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const isDuplicateFilterActive = urlParams.get('duplicate') === 'true';

  // Set initial button state
  if (isDuplicateFilterActive) {
    duplicateFilterButton.classList.remove('btn-outline-secondary');
    duplicateFilterButton.classList.add('btn-secondary');
  }

  duplicateFilterButton.addEventListener('click', () => {
    const isCurrentlyActive = duplicateFilterButton.classList.contains('btn-secondary');
    const newState = !isCurrentlyActive;

    // Update button appearance
    if (newState) {
      duplicateFilterButton.classList.remove('btn-outline-secondary');
      duplicateFilterButton.classList.add('btn-secondary');
    } else {
      duplicateFilterButton.classList.remove('btn-secondary');
      duplicateFilterButton.classList.add('btn-outline-secondary');
    }

    if (isPaginationMode()) {
      // SERVER-SIDE MODE - Update URL parameter
      performDuplicateFilterServer(newState);
    } else {
      // CLIENT-SIDE MODE - Apply filtering directly
      applyDuplicateFilter(newState);
    }
  });
}

// Server-side duplicate filter
function performDuplicateFilterServer(showOnlyDuplicates) {
  const currentUrl = new URL(window.location);

  if (showOnlyDuplicates) {
    currentUrl.searchParams.set('duplicate', 'true');
  } else {
    currentUrl.searchParams.delete('duplicate');
  }

  // Reset to page 1 when filtering
  currentUrl.searchParams.set('page', '1');
  window.location.href = currentUrl.toString();
}

// Apply duplicate/consolidated filter
function applyDuplicateFilter(showOnlyDuplicates) {
  // Get the grid container and all column containers (not just the cards)
  const gridContainer = document.getElementById('grid');
  if (!gridContainer) {
    console.warn('Grid container not found');
    return;
  }

  // Try multiple selectors to find column containers
  let columnContainers = gridContainer.querySelectorAll('.col-md-6');
  if (columnContainers.length === 0) {
    columnContainers = gridContainer.querySelectorAll('[class*="col-"]');
  }

  if (!showOnlyDuplicates) {
    // Show all column containers by removing the duplicate-filter-hidden class
    columnContainers.forEach(col => {
      col.classList.remove('duplicate-filter-hidden');
    });
    // Trigger the existing grid filter to refresh
    triggerGridRefresh();
    return;
  }

  // Check if we're in consolidated mode by looking for data-instance-count
  const consolidatedMode = document.querySelector('[data-instance-count]') !== null;

  if (consolidatedMode) {
    // CONSOLIDATED MODE: Show only sets with instance count > 1
    columnContainers.forEach(col => {
      const card = col.querySelector('[data-set-id]');
      if (card) {
        const instanceCount = parseInt(card.dataset.instanceCount || '1');
        if (instanceCount > 1) {
          col.classList.remove('duplicate-filter-hidden');
        } else {
          col.classList.add('duplicate-filter-hidden');
        }
      }
    });
  } else {
    // NON-CONSOLIDATED MODE: Show only sets that appear multiple times
    const setByCounts = {};

    // Count occurrences of each set
    columnContainers.forEach(col => {
      const card = col.querySelector('[data-set-id]');
      if (card) {
        const rebrickableId = card.dataset.rebrickableId;
        if (rebrickableId) {
          setByCounts[rebrickableId] = (setByCounts[rebrickableId] || 0) + 1;
        }
      }
    });

    // Show/hide based on count
    columnContainers.forEach(col => {
      const card = col.querySelector('[data-set-id]');
      if (card) {
        const rebrickableId = card.dataset.rebrickableId;
        if (rebrickableId && setByCounts[rebrickableId] > 1) {
          col.classList.remove('duplicate-filter-hidden');
        } else {
          col.classList.add('duplicate-filter-hidden');
        }
      }
    });
  }

  // Trigger the existing grid filter to refresh and respect our duplicate filter
  triggerGridRefresh();
}

// Helper function to trigger grid filter refresh
function triggerGridRefresh() {
  // Check if we have a grid instance with filter capability
  if (window.gridInstances) {
    const gridElement = document.getElementById('grid');
    if (gridElement && window.gridInstances[gridElement.id]) {
      const gridInstance = window.gridInstances[gridElement.id];
      if (gridInstance.filter) {
        // Trigger the existing filter to refresh
        gridInstance.filter.filter();
      }
    }
  }
}

// Initialize clear filters button functionality
function initializeClearFiltersButton() {
  const clearFiltersButton = document.getElementById('grid-filter-clear');
  if (!clearFiltersButton) return;

  clearFiltersButton.addEventListener('click', () => {
    if (isPaginationMode()) {
      // SERVER-SIDE PAGINATION MODE: Remove filter parameters from URL
      const currentUrl = new URL(window.location);

      // Remove all filter parameters
      const filterParams = ['status', 'theme', 'year', 'owner', 'purchase_location', 'storage', 'tag', 'duplicate'];
      filterParams.forEach(param => {
        currentUrl.searchParams.delete(param);
      });

      // Reset to page 1
      currentUrl.searchParams.set('page', '1');

      // Navigate to cleaned URL
      window.location.href = currentUrl.toString();
    } else {
      // CLIENT-SIDE MODE: Reset all filter dropdowns to empty string
      const filterDropdowns = [
        'grid-status',
        'grid-theme',
        'grid-year',
        'grid-owner',
        'grid-purchase-location',
        'grid-storage',
        'grid-tag'
      ];

      filterDropdowns.forEach(dropdownId => {
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
          dropdown.value = '';
        }
      });

      // Clear duplicate filter if active
      const duplicateButton = document.getElementById('duplicate-filter-toggle');
      if (duplicateButton && duplicateButton.classList.contains('btn-secondary')) {
        duplicateButton.classList.remove('btn-secondary');
        duplicateButton.classList.add('btn-outline-secondary');
        applyDuplicateFilter(false);
      }

      // Trigger filtering if grid instance exists
      triggerGridRefresh();
    }
  });
}