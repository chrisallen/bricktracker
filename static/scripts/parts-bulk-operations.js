// Bulk operations for parts in set details page
class PartsBulkOperations {
    constructor(accordionId) {
        this.accordionId = accordionId;
        this.setupModal();
        this.setupEventListeners();
    }

    setupModal() {
        // Create Bootstrap modal if it doesn't exist
        if (!document.getElementById('partsConfirmModal')) {
            const modalHTML = `
                <div class="modal fade" id="partsConfirmModal" tabindex="-1" aria-labelledby="partsConfirmModalLabel" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="partsConfirmModalLabel">Confirm Action</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p id="partsConfirmModalMessage"></p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" id="partsConfirmModalConfirm">Confirm</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }
    }

    setupEventListeners() {
        // Mark all as missing (only if missing parts are not hidden)
        const markAllMissingBtn = document.getElementById(`mark-all-missing-${this.accordionId}`);
        if (markAllMissingBtn) {
            markAllMissingBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.confirmAndExecute(
                    'Mark all parts as missing?',
                    'This will set the missing count to the maximum quantity for all parts in this section.',
                    () => this.markAllMissing()
                );
            });
        }

        // Clear all missing (only if missing parts are not hidden)
        const clearAllMissingBtn = document.getElementById(`clear-all-missing-${this.accordionId}`);
        if (clearAllMissingBtn) {
            clearAllMissingBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.confirmAndExecute(
                    'Clear all missing parts?',
                    'This will clear the missing field for all parts in this section.',
                    () => this.clearAllMissing()
                );
            });
        }

        // Check all checkboxes (only if checked parts are not hidden)
        const checkAllBtn = document.getElementById(`check-all-${this.accordionId}`);
        if (checkAllBtn) {
            checkAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.checkAll();
            });
        }

        // Uncheck all checkboxes (only if checked parts are not hidden)
        const uncheckAllBtn = document.getElementById(`uncheck-all-${this.accordionId}`);
        if (uncheckAllBtn) {
            uncheckAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.uncheckAll();
            });
        }
    }

    confirmAndExecute(title, message, callback) {
        const modal = document.getElementById('partsConfirmModal');
        const modalTitle = document.getElementById('partsConfirmModalLabel');
        const modalMessage = document.getElementById('partsConfirmModalMessage');
        const confirmBtn = document.getElementById('partsConfirmModalConfirm');

        // Set modal content
        modalTitle.textContent = title;
        modalMessage.textContent = message;

        // Remove any existing event listeners and add new one
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        newConfirmBtn.addEventListener('click', () => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            modalInstance.hide();
            callback();
        });

        // Show modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }

    markAllMissing() {
        const accordionElement = document.getElementById(this.accordionId);
        if (!accordionElement) return;

        // Find all rows in this accordion
        const rows = accordionElement.querySelectorAll('tbody tr');
        rows.forEach(row => {
            // Skip rows hidden by an active header filter
            if (row.classList.contains('parts-filtered-out')) return;

            // Find the quantity cell (usually 4th column)
            const quantityCell = row.cells[3]; // Index 3 for quantity column
            const missingInput = row.querySelector('input[id*="-missing-"]');

            if (quantityCell && missingInput) {
                // Extract quantity from cell text content
                const quantityText = quantityCell.textContent.trim();
                const quantity = parseInt(quantityText) || 1; // Default to 1 if can't parse

                if (missingInput.value !== quantity.toString()) {
                    missingInput.value = quantity.toString();
                    // Trigger change event to activate BrickChanger
                    missingInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        });
    }

    clearAllMissing() {
        const accordionElement = document.getElementById(this.accordionId);
        if (!accordionElement) return;

        const missingInputs = accordionElement.querySelectorAll('input[id*="-missing-"]');
        missingInputs.forEach(input => {
            if (input.closest('tr')?.classList.contains('parts-filtered-out')) return;
            if (input.value !== '') {
                input.value = '';
                // Trigger change event to activate BrickChanger
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }

    checkAll() {
        const accordionElement = document.getElementById(this.accordionId);
        if (!accordionElement) return;

        const checkboxes = accordionElement.querySelectorAll('input[id*="-checked-"][type="checkbox"]');
        checkboxes.forEach(checkbox => {
            if (checkbox.closest('tr')?.classList.contains('parts-filtered-out')) return;
            if (!checkbox.checked) {
                checkbox.checked = true;
                // Trigger change event to activate BrickChanger
                checkbox.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }

    uncheckAll() {
        const accordionElement = document.getElementById(this.accordionId);
        if (!accordionElement) return;

        const checkboxes = accordionElement.querySelectorAll('input[id*="-checked-"][type="checkbox"]');
        checkboxes.forEach(checkbox => {
            if (checkbox.closest('tr')?.classList.contains('parts-filtered-out')) return;
            if (checkbox.checked) {
                checkbox.checked = false;
                // Trigger change event to activate BrickChanger
                checkbox.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }
}

// Initialize bulk operations for all part accordions.
// Idempotent: call again after inserting new tables (lazy-loaded bags).
const initPartsBulkOperations = () => {
    const hamburgerMenus = document.querySelectorAll('button[id^="hamburger-"]');
    hamburgerMenus.forEach(button => {
        if (button.dataset.bulkWired === 'true') {
            return;
        }
        button.dataset.bulkWired = 'true';
        const accordionId = button.id.replace('hamburger-', '');
        new PartsBulkOperations(accordionId);
    });
};
window.initPartsBulkOperations = initPartsBulkOperations;

document.addEventListener('DOMContentLoaded', initPartsBulkOperations);