// Per-column header filters for the accordion parts tables on the set details page.
class PartsTableFilter {
    constructor(table) {
        this.table = table;
        this.body = table.querySelector('tbody');
        this.rows = Array.from(this.body ? this.body.querySelectorAll('tr') : []);

        this.nameInput = table.querySelector('[data-parts-filter="name"]');
        this.colorSelect = table.querySelector('[data-parts-filter="color"]');
        this.missingSelect = table.querySelector('[data-parts-filter="missing"]');
        this.damagedSelect = table.querySelector('[data-parts-filter="damaged"]');
        this.checkedSelect = table.querySelector('[data-parts-filter="checked"]');
        this.clearButton = table.querySelector('[data-parts-filter-clear]');

        this.setupListeners();
        this.apply();
    }

    setupListeners() {
        const debouncedApply = this.debounce(() => this.apply(), 150);

        // Name search is debounced so typing stays smooth on big tables.
        if (this.nameInput) {
            this.nameInput.addEventListener('input', debouncedApply);
        }

        // Dropdowns re-filter immediately.
        [this.colorSelect, this.missingSelect, this.damagedSelect, this.checkedSelect].forEach(select => {
            if (select) {
                select.addEventListener('change', () => this.apply());
            }
        });

        if (this.clearButton) {
            this.clearButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.clear();
            });
        }

        // Live re-evaluation: editing a missing/damaged value or toggling a
        // checkbox in the body should re-run the active filter.
        if (this.body) {
            this.body.addEventListener('change', () => this.apply());
            this.body.addEventListener('input', debouncedApply);
        }
    }

    cellText(row, col) {
        const cell = row.querySelector(`[data-col="${col}"]`);
        if (!cell) {
            return '';
        }
        const sort = cell.getAttribute('data-sort');
        return (sort !== null ? sort : cell.textContent).trim().toLowerCase();
    }

    // Numeric value for missing/damaged, reading the live input when present.
    cellNumber(row, col) {
        const cell = row.querySelector(`[data-col="${col}"]`);
        if (!cell) {
            return 0;
        }
        const input = cell.querySelector('input');
        const raw = input ? input.value : (cell.getAttribute('data-sort') || cell.textContent);
        const value = parseInt(raw, 10);
        return Number.isNaN(value) ? 0 : value;
    }

    rowChecked(row) {
        const cell = row.querySelector('[data-col="checked"]');
        if (!cell) {
            return false;
        }
        const checkbox = cell.querySelector('input[type="checkbox"]');
        if (checkbox) {
            return checkbox.checked;
        }
        return cell.getAttribute('data-sort') === '1';
    }

    matchesNumberFilter(value, mode) {
        if (mode === 'with') {
            return value > 0;
        }
        if (mode === 'without') {
            return value === 0;
        }
        return true;
    }

    apply() {
        const nameTerm = (this.nameInput ? this.nameInput.value : '').trim().toLowerCase();
        const colorValue = (this.colorSelect ? this.colorSelect.value : '').trim().toLowerCase();
        const missingMode = this.missingSelect ? this.missingSelect.value : '';
        const damagedMode = this.damagedSelect ? this.damagedSelect.value : '';
        const checkedValue = this.checkedSelect ? this.checkedSelect.value : '';

        // Colors available among rows that pass every filter except color, so
        // the picker only offers colors still present in the current results.
        const availableColors = new Set();
        let visibleCount = 0;

        this.rows.forEach(row => {
            const passNonColor =
                (!nameTerm || this.cellText(row, 'name').includes(nameTerm)) &&
                this.matchesNumberFilter(this.cellNumber(row, 'missing'), missingMode) &&
                this.matchesNumberFilter(this.cellNumber(row, 'damaged'), damagedMode) &&
                (checkedValue === '' ||
                    (checkedValue === '1' ? this.rowChecked(row) : !this.rowChecked(row)));

            if (passNonColor) {
                const colorCell = row.querySelector('[data-col="color"]');
                if (colorCell) {
                    const name = colorCell.textContent.trim();
                    if (name) {
                        availableColors.add(name);
                    }
                }
            }

            const passColor = !colorValue || this.cellText(row, 'color') === colorValue;
            const visible = passNonColor && passColor;
            row.classList.toggle('parts-filtered-out', !visible);
            if (visible) {
                visibleCount += 1;
            }
        });

        this.updateColorOptions(availableColors);
        this.updateEmptyState(visibleCount);
    }

    // Rebuild the color dropdown from the colors currently in the results,
    // keeping the user's current selection if it is still available.
    updateColorOptions(colors) {
        if (!this.colorSelect) {
            return;
        }
        const current = this.colorSelect.value;
        const sorted = Array.from(colors).sort((a, b) => a.localeCompare(b));
        const options = ['<option value="">All colors</option>']
            .concat(sorted.map(name => `<option value="${name.toLowerCase()}">${name}</option>`));
        this.colorSelect.innerHTML = options.join('');
        // Restore selection (the <option> values are lowercased to match).
        this.colorSelect.value = sorted.some(n => n.toLowerCase() === current) ? current : '';
    }

    updateEmptyState(visibleCount) {
        if (!this.body) {
            return;
        }
        if (!this.emptyRow) {
            const columns = this.table.querySelectorAll('thead tr:first-child th').length || 1;
            this.emptyRow = document.createElement('tr');
            this.emptyRow.className = 'parts-filter-empty no-sort';
            this.emptyRow.innerHTML = `<td colspan="${columns}" class="text-center text-body-secondary py-3">No matching parts</td>`;
            this.body.appendChild(this.emptyRow);
        }
        this.emptyRow.style.display = visibleCount === 0 ? '' : 'none';
    }

    clear() {
        if (this.nameInput) { this.nameInput.value = ''; }
        [this.colorSelect, this.missingSelect, this.damagedSelect, this.checkedSelect].forEach(select => {
            if (select) {
                select.value = '';
            }
        });
        this.apply();
    }

    debounce(fn, wait) {
        let timer = null;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), wait);
        };
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('table[data-parts-filterable="true"]').forEach(table => {
        new PartsTableFilter(table);
    });
});
