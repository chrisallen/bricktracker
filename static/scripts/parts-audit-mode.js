// Audit mode: a focused, keyboard-driven modal that walks the visible parts of
// one accordion parts table, letting you check each part off and record missing
// counts without hunting for tiny checkboxes.
//
// Saving reuses the existing BrickChanger auto-save: set the value on the row's
// missing input / checked checkbox and dispatch a "change" event, exactly like
// parts-bulk-operations.js does.
class PartsAuditMode {
    constructor(accordionId) {
        this.accordionId = accordionId;
        this.trigger = document.getElementById(`audit-mode-${accordionId}`);
        if (!this.trigger) {
            return;
        }

        this.rows = [];
        this.index = 0;
        this.mode = 'missing'; // 'missing' or 'found'

        this.setupModal();
        this.cacheElements();
        this.setupEventListeners();
    }

    // Build the shared modal once and reuse it across every accordion.
    setupModal() {
        if (document.getElementById('partsAuditModal')) {
            return;
        }

        const modalHTML = `
            <div class="modal fade" id="partsAuditModal" tabindex="-1" aria-labelledby="partsAuditModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header d-block">
                            <div class="d-flex align-items-center">
                                <h5 class="modal-title mb-0" id="partsAuditModalLabel"><i class="ri-eye-line me-2"></i>Audit parts</h5>
                                <span class="ms-auto me-3 text-secondary"><span id="audit-position">0 / 0</span></span>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="progress mt-2" role="progressbar" style="height: 6px;">
                                <div id="audit-progress-bar" class="progress-bar" style="width: 0%;"></div>
                            </div>
                            <small class="text-secondary"><span id="audit-checked-count">0</span> checked</small>
                        </div>
                        <div class="modal-body text-center">
                            <div class="mb-2">
                                <img id="audit-image" class="img-fluid border rounded audit-image" alt="">
                            </div>
                            <div class="mb-1">Quantity <span id="audit-qty">0</span></div>
                            <div class="mb-3"><span id="audit-name" class="fs-6"></span> <span id="audit-color" class="text-secondary ms-1"></span></div>

                            <div id="audit-input-area">
                                <div class="btn-group mb-2" role="group" aria-label="Audit mode">
                                    <button type="button" class="btn btn-sm" id="audit-mode-missing">Missing</button>
                                    <button type="button" class="btn btn-sm" id="audit-mode-found">Found</button>
                                </div>
                                <div class="row justify-content-center mb-1">
                                    <div class="col-auto">
                                        <div class="input-group">
                                            <span class="input-group-text" id="audit-input-label">Missing</span>
                                            <input type="number" inputmode="numeric" pattern="[0-9]*" min="0" class="form-control text-center" id="audit-number" style="max-width: 6rem;" autocomplete="off">
                                        </div>
                                    </div>
                                </div>
                                <small class="text-secondary">type a number</small>
                            </div>
                            <div id="audit-no-input" class="text-secondary d-none">This section only tracks checked status.</div>
                        </div>
                        <div class="modal-footer d-flex">
                            <button type="button" class="btn btn-outline-secondary" id="audit-prev"><i class="ri-arrow-left-line"></i> Prev</button>
                            <button type="button" class="btn btn-primary ms-auto" id="audit-next">Check &amp; Next <i class="ri-arrow-right-line"></i></button>
                        </div>
                        <div class="modal-footer py-1">
                            <small class="text-secondary w-100 text-center">
                                ←/→ move · type number · Enter / Space save+next
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    cacheElements() {
        this.modalEl = document.getElementById('partsAuditModal');
        this.modal = bootstrap.Modal.getOrCreateInstance(this.modalEl);
        this.el = {
            position: document.getElementById('audit-position'),
            progress: document.getElementById('audit-progress-bar'),
            checkedCount: document.getElementById('audit-checked-count'),
            image: document.getElementById('audit-image'),
            name: document.getElementById('audit-name'),
            color: document.getElementById('audit-color'),
            qty: document.getElementById('audit-qty'),
            inputArea: document.getElementById('audit-input-area'),
            noInput: document.getElementById('audit-no-input'),
            modeMissing: document.getElementById('audit-mode-missing'),
            modeFound: document.getElementById('audit-mode-found'),
            inputLabel: document.getElementById('audit-input-label'),
            number: document.getElementById('audit-number'),
            prev: document.getElementById('audit-prev'),
            next: document.getElementById('audit-next'),
        };
    }

    setupEventListeners() {
        this.trigger.addEventListener('click', (e) => {
            e.preventDefault();
            this.start();
        });

        // These shared-modal controls get wired by whichever instance is created
        // first; subsequent instances just re-point the handlers at the active one
        // via the `activeInstance` lookup performed inside start().
        if (this.modalEl.dataset.auditWired === 'true') {
            return;
        }
        this.modalEl.dataset.auditWired = 'true';

        this.el.prev.addEventListener('click', () => PartsAuditMode.active && PartsAuditMode.active.go(-1));
        this.el.next.addEventListener('click', () => PartsAuditMode.active && PartsAuditMode.active.commitAndNext());

        this.el.modeMissing.addEventListener('click', () => PartsAuditMode.active && PartsAuditMode.active.setMode('missing'));
        this.el.modeFound.addEventListener('click', () => PartsAuditMode.active && PartsAuditMode.active.setMode('found'));

        // Keyboard handling in the capture phase so navigation keys win over the
        // focused number input's default cursor movement.
        this.modalEl.addEventListener('keydown', (e) => {
            const active = PartsAuditMode.active;
            if (!active) {
                return;
            }
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    active.go(-1);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    active.go(1);
                    break;
                case 'Enter':
                    e.preventDefault();
                    active.commitAndNext();
                    break;
                case ' ':
                case 'Spacebar':
                    e.preventDefault();
                    active.commitAndNext();
                    break;
                // digits / Backspace fall through to the number input
            }
        }, true);

        // Focus the number box whenever the modal opens (desktop only).
        this.modalEl.addEventListener('shown.bs.modal', () => {
            const active = PartsAuditMode.active;
            if (active) {
                active.focusInput();
            }
        });
    }

    // On phones we never auto-focus the number box: doing so pops the keyboard
    // and scrolls the part image off-screen. The audit flow there is touch
    // driven (tap the field only when entering a count, then Check & Next), so
    // the image stays visible while you identify the part.
    isMobileLayout() {
        return window.matchMedia('(max-width: 575.98px)').matches;
    }

    focusInput() {
        if (this.isMobileLayout()) {
            return;
        }
        if (this.el.number && !this.el.inputArea.classList.contains('d-none')) {
            this.el.number.focus();
            this.el.number.select();
        }
    }

    start() {
        const accordion = document.getElementById(this.accordionId);
        if (!accordion) {
            return;
        }

        // Snapshot the currently visible rows in DOM (sort) order. Using a
        // snapshot means saving (which re-runs the header filter) can't drop the
        // row we are sitting on.
        this.rows = Array.from(accordion.querySelectorAll('tbody tr')).filter(
            row => !row.classList.contains('parts-filtered-out') && row.offsetParent !== null
        );

        if (!this.rows.length) {
            return;
        }

        PartsAuditMode.active = this;
        this.index = 0;
        this.render();
        this.modal.show();
    }

    setMode(mode) {
        this.mode = mode;
        this.render();
        this.focusInput();
    }

    currentRow() {
        return this.rows[this.index];
    }

    neededQty(row) {
        const cell = row.querySelector('[data-col="quantity"]');
        const value = cell ? parseInt(cell.textContent.trim(), 10) : NaN;
        return Number.isNaN(value) ? 1 : value;
    }

    missingInput(row) {
        // ids look like "part-missing-...-{id}" / "individual-part-missing-...",
        // so match the same "-missing-" fragment parts-bulk-operations.js uses.
        return row.querySelector('input[id*="-missing-"]');
    }

    checkedBox(row) {
        return row.querySelector('input[id*="-checked-"][type="checkbox"]');
    }

    render() {
        const row = this.currentRow();
        if (!row) {
            return;
        }

        // Image: prefer the full-size lightbox target, fall back to the thumbnail.
        const link = row.querySelector('a[data-lightbox]');
        const img = row.querySelector('td img');
        this.el.image.src = (link && link.getAttribute('href')) || (img && img.getAttribute('src')) || '';

        const nameLink = row.querySelector('[data-col="name"] a');
        this.el.name.textContent = nameLink ? nameLink.textContent.trim() : '';

        const colorCell = row.querySelector('[data-col="color"]');
        this.el.color.innerHTML = colorCell ? colorCell.innerHTML : '';

        const needed = this.neededQty(row);
        this.el.qty.textContent = needed;

        // Toggle the input area depending on whether this table tracks missing.
        const missing = this.missingInput(row);
        if (missing) {
            this.el.inputArea.classList.remove('d-none');
            this.el.noInput.classList.add('d-none');

            // Mode button styling.
            this.el.modeMissing.className = 'btn btn-sm ' + (this.mode === 'missing' ? 'btn-primary' : 'btn-outline-secondary');
            this.el.modeFound.className = 'btn btn-sm ' + (this.mode === 'found' ? 'btn-primary' : 'btn-outline-secondary');
            this.el.inputLabel.textContent = this.mode === 'found' ? 'Found' : 'Missing';

            // Prefill: missing mode shows the current missing value, found starts empty.
            this.el.number.value = this.mode === 'missing' ? (missing.value || '') : '';

            // Remember what the box started with so a commit that didn't change
            // the number leaves the missing field (and the database) untouched.
            this.originalNumber = this.el.number.value.trim();
        } else {
            this.el.inputArea.classList.add('d-none');
            this.el.noInput.classList.remove('d-none');
            this.originalNumber = '';
        }

        this.updateProgress();
    }

    updateProgress() {
        const total = this.rows.length;
        this.el.position.textContent = `${this.index + 1} / ${total}`;
        this.el.progress.style.width = total ? `${Math.round(((this.index + 1) / total) * 100)}%` : '0%';

        const checked = this.rows.filter(row => {
            const box = this.checkedBox(row);
            return box && box.checked;
        }).length;
        this.el.checkedCount.textContent = checked;
    }

    // Plain navigation (arrows / Prev) — clamps, never saves or closes.
    go(delta) {
        const next = this.index + delta;
        if (next < 0 || next >= this.rows.length) {
            return;
        }
        this.index = next;
        this.render();
        this.focusInput();
    }

    setMissingValue(input, value) {
        if (input.value !== value) {
            input.value = value;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    check(row) {
        const box = this.checkedBox(row);
        if (box && !box.checked) {
            box.checked = true;
            box.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    // Enter / Space: record the typed number per mode, tick checked, advance.
    // If the number box is unchanged from what the part loaded with, we leave the
    // missing field (and the database) completely alone and only tick checked, so
    // glancing past a part never triggers a redundant POST.
    commitAndNext() {
        const row = this.currentRow();
        if (!row) {
            return;
        }

        const input = this.missingInput(row);
        if (input) {
            const typed = this.el.number.value.trim();
            if (typed !== this.originalNumber) {
                const number = parseInt(typed, 10) || 0;
                let missing;
                if (this.mode === 'found') {
                    missing = Math.max(0, this.neededQty(row) - number);
                } else {
                    missing = Math.max(0, number);
                }
                // Empty string clears the field (0 missing), matching the
                // "clear all missing" convention in parts-bulk-operations.js.
                this.setMissingValue(input, missing > 0 ? String(missing) : '');
            }
        }

        this.check(row);
        this.advance();
    }

    // Move forward after a commit; close the modal once the last part is done.
    advance() {
        this.updateProgress();
        if (this.index + 1 >= this.rows.length) {
            this.modal.hide();
            return;
        }
        this.index += 1;
        this.render();
        this.focusInput();
    }
}

PartsAuditMode.active = null;

// Wire up an instance per accordion that exposes an audit menu item.
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[id^="audit-mode-"]').forEach(item => {
        const accordionId = item.id.replace('audit-mode-', '');
        new PartsAuditMode(accordionId);
    });
});
