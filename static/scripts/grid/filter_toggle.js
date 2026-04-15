// Filter toggle for NOT filtering
class BrickFilterToggle {
    constructor() {
        // Find all filter toggle buttons
        this.toggles = document.querySelectorAll('.filter-toggle');

        // Initialize each toggle
        this.toggles.forEach(toggle => {
            this.initializeToggle(toggle);
        });
    }

    initializeToggle(toggle) {
        const targetId = toggle.dataset.filterTarget;
        const targetSelect = document.getElementById(targetId);

        if (!targetSelect) {
            console.error(`Filter toggle: Target select #${targetId} not found`);
            return;
        }

        // Check if we need to initialize in NOT mode based on URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const filterParam = this.getFilterParamName(targetId);
        const filterValue = urlParams.get(filterParam);

        // Initialize the NOT mode flag
        if (filterValue && filterValue.startsWith('-')) {
            targetSelect.dataset.notMode = 'true';
            this.setToggleState(toggle, 'not-equals');
        } else {
            targetSelect.dataset.notMode = 'false';
            this.setToggleState(toggle, 'equals');
        }

        // Add click event listener to toggle button
        toggle.addEventListener('click', () => {
            this.handleToggleClick(toggle, targetSelect);
        });

        // Add change event listener to the select
        targetSelect.addEventListener('change', () => {
            // If select is cleared (empty value), reset toggle to equals mode
            const selectValue = targetSelect.options[targetSelect.selectedIndex]?.value || '';
            if (!selectValue) {
                targetSelect.dataset.notMode = 'false';
                this.setToggleState(toggle, 'equals');
            }
        });
    }

    getFilterParamName(selectId) {
        // Map select IDs to URL parameter names
        const mapping = {
            'grid-status': 'status',
            'grid-theme': 'theme',
            'grid-owner': 'owner',
            'grid-storage': 'storage',
            'grid-purchase-location': 'purchase_location',
            'grid-tag': 'tag',
            'grid-year': 'year'
        };
        return mapping[selectId] || selectId.replace('grid-', '');
    }

    handleToggleClick(toggle, targetSelect) {
        const selectValue = targetSelect.options[targetSelect.selectedIndex]?.value || '';

        // Don't toggle if no value is selected
        if (!selectValue) {
            return;
        }

        // Toggle the NOT mode
        const isNotMode = targetSelect.dataset.notMode === 'true';
        targetSelect.dataset.notMode = isNotMode ? 'false' : 'true';

        // Update toggle button visual state
        this.setToggleState(toggle, isNotMode ? 'equals' : 'not-equals');

        // Trigger change event on the select to update the grid filter
        targetSelect.dispatchEvent(new Event('change'));
    }

    setToggleState(toggle, mode) {
        toggle.dataset.filterMode = mode;
        const icon = toggle.querySelector('i');

        if (mode === 'not-equals') {
            // Use ≠ symbol (text character)
            icon.className = '';
            icon.textContent = '≠';
            toggle.classList.remove('btn-outline-secondary');
            toggle.classList.add('btn-outline-danger');
            toggle.title = 'NOT equals (click to toggle)';
        } else {
            // Use = symbol (text character) instead of icon
            icon.className = '';
            icon.textContent = '=';
            toggle.classList.remove('btn-outline-danger');
            toggle.classList.add('btn-outline-secondary');
            toggle.title = 'Equals (click to toggle)';
        }
    }

    // Helper method to get the actual filter value (with "-" prefix if in NOT mode)
    static getFilterValue(select) {
        const selectValue = select.options[select.selectedIndex]?.value || '';
        const isNotMode = select.dataset.notMode === 'true';

        if (selectValue && isNotMode && !selectValue.startsWith('-')) {
            return '-' + selectValue;
        }
        return selectValue;
    }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    new BrickFilterToggle();
});
