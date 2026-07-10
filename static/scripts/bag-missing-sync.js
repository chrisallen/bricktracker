// Keeps the main Parts table's missing count equal to the sum of the per-bag
// missing inputs for that part (a part can span several bags). Bag rows carry
// data-target-missing = the main row's input id; writing the main input and
// dispatching "change" lets the existing BrickChanger persist it.
//
// The sum always wins: a manual edit of the main field is overwritten by the
// next bag edit for that part. Parts without bag inputs stay fully manual.
(() => {
    const sync = (target) => {
        const main = document.getElementById(target);
        if (!main || main.disabled) {
            return;
        }

        let sum = 0;
        document.querySelectorAll(`table[data-bag-table] tr[data-target-missing="${CSS.escape(target)}"] input[id*="-missing-"]`).forEach(input => {
            sum += parseInt(input.value, 10) || 0;
        });

        // Empty string clears the field (0 missing), matching the "clear all
        // missing" convention in parts-bulk-operations.js.
        const value = sum > 0 ? String(sum) : '';
        if (main.value !== value) {
            main.value = value;
            main.dispatchEvent(new Event('change', { bubbles: true }));
        }
    };

    const handle = (e) => {
        // Trusted "input" events fire per keystroke; the sum only needs to
        // follow once the value is committed ("change"). The untrusted case
        // is the BrickChanger clear button, which POSTs directly and only
        // dispatches a programmatic "input" event.
        if (e.type === 'input' && e.isTrusted) {
            return;
        }
        const input = e.target;
        if (!input.matches || !input.matches('input[id*="-missing-"]')) {
            return;
        }
        const row = input.closest('tr[data-target-missing]');
        if (row && input.closest('table[data-bag-table]')) {
            sync(row.dataset.targetMissing);
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        document.addEventListener('change', handle);
        document.addEventListener('input', handle);
    });
})();

// Lazy-load the bag tables the first time the Bags accordion is opened: the
// page only ships the accordion shell, the tables (hundreds of rows/inputs)
// come from the bags_tables fragment. After inserting, re-run the idempotent
// wiring helpers. The sortable library and quick-add already work through
// document-level delegation, so they pick the new tables up on their own.
(() => {
    document.addEventListener('DOMContentLoaded', () => {
        const container = document.getElementById('bags-lazy');
        const collapse = document.getElementById('bags-inventory');
        if (!container || !collapse) {
            return;
        }

        let loaded = false;
        collapse.addEventListener('show.bs.collapse', async (e) => {
            // Nested bag collapses bubble the same event up
            if (loaded || e.target !== collapse) {
                return;
            }
            loaded = true;

            try {
                const response = await fetch(container.dataset.bagsSrc);
                if (!response.ok) {
                    throw new Error(`Response status: ${response.status}`);
                }
                container.innerHTML = await response.text();

                setup_changers();
                window.initPartsTableFilters?.();
                window.initPartsBulkOperations?.();
                window.initPartsAuditModes?.();
            } catch (error) {
                console.log(error.message);
                loaded = false; // allow retry on next open
                container.innerHTML = '<div class="text-center text-danger p-3"><i class="ri-alert-line"></i> Could not load the bags. Close and reopen to retry.</div>';
            }
        });
    });
})();
