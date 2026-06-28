// Mass-edit of sets from the grid (Feature 4).
//
// Lets an authenticated user select several cards on the sets grid and edit
// their metadata in one pass. Each editable control is pre-filled from the
// selected cards: a shared value is shown and editable, differing values show
// "varies" and only overwrite when actually touched. Boolean metadata
// (tags/statuses/owners) is tri-state: all-on / all-off / mixed.
(function () {
    // Convert a stored purchase-date timestamp (epoch seconds) to the value
    // expected by <input type="date"> (yyyy-mm-dd), using local time since the
    // stored timestamp was built from a local midnight date.
    function tsToDateInput(ts) {
        if (!ts) return "";
        const d = new Date(parseFloat(ts) * 1000);
        if (isNaN(d.getTime())) return "";
        const m = String(d.getMonth() + 1).padStart(2, "0");
        const day = String(d.getDate()).padStart(2, "0");
        return `${d.getFullYear()}-${m}-${day}`;
    }

    // Custom date fields are stored as yyyy/mm/dd text (matching the single-set
    // editor), so just swap the separators for the date input.
    function slashToDateInput(v) {
        return v ? v.replaceAll("/", "-") : "";
    }

    // Reverse of the above: the backend (purchase date + custom date fields)
    // expects yyyy/mm/dd.
    function dateInputToSlash(v) {
        return v ? v.replaceAll("-", "/") : "";
    }

    function removeVariesOption(sel) {
        if (sel.tagName !== "SELECT") return;
        const opt = sel.querySelector('option[data-varies="true"]');
        if (opt) opt.remove();
    }

    function addVariesOption(sel) {
        removeVariesOption(sel);
        const opt = document.createElement("option");
        opt.value = "__varies__";
        opt.textContent = "— varies —";
        opt.dataset.varies = "true";
        opt.disabled = true;
        opt.selected = true;
        sel.insertBefore(opt, sel.firstChild);
        sel.value = "__varies__";
    }

    function initBulkEdit() {
        const toggle = document.getElementById("bulk-select-toggle");
        const grid = document.getElementById("grid");
        const panel = document.getElementById("bulk-edit-panel");
        const bar = document.getElementById("bulk-select-bar");

        // Only on the authenticated sets grid
        if (!toggle || !grid || !panel || !bar) return;

        const countEl = document.getElementById("bulk-select-count");
        const editCountEl = document.getElementById("bulk-edit-count");
        const openBtn = document.getElementById("bulk-edit-open");
        const applyBtn = document.getElementById("bulk-edit-apply");
        const bulkUrl = bar.dataset.bulkEditUrl;

        const selected = new Set();

        const cards = () => Array.from(grid.querySelectorAll(".card[data-set-id]"));

        // Inject a checkbox overlay into every card (revealed by CSS in select
        // mode).
        cards().forEach((card) => {
            if (card.querySelector(".bulk-select-check")) return;
            const overlay = document.createElement("div");
            overlay.className = "bulk-select-check";
            overlay.innerHTML =
                '<input type="checkbox" class="form-check-input" tabindex="-1">';
            card.appendChild(overlay);
        });

        const isSelected = (card) => card.classList.contains("bulk-selected");

        function setSelected(card, on) {
            card.classList.toggle("bulk-selected", on);
            const cb = card.querySelector(".bulk-select-check input");
            if (cb) cb.checked = on;
            if (on) selected.add(card);
            else selected.delete(card);
        }

        function refreshCount() {
            const n = selected.size;
            countEl.textContent = n;
            editCountEl.textContent = n;
            openBtn.disabled = n === 0;
        }

        function enterMode() {
            document.body.classList.add("bulk-select-mode");
            bar.classList.add("show");
            toggle.classList.add("active");
        }

        function exitMode() {
            document.body.classList.remove("bulk-select-mode");
            bar.classList.remove("show");
            toggle.classList.remove("active");
            cards().forEach((c) => setSelected(c, false));
            refreshCount();
        }

        toggle.addEventListener("click", () => {
            if (document.body.classList.contains("bulk-select-mode")) exitMode();
            else enterMode();
        });

        document
            .getElementById("bulk-select-exit")
            .addEventListener("click", exitMode);

        document
            .getElementById("bulk-select-clear")
            .addEventListener("click", () => {
                cards().forEach((c) => setSelected(c, false));
                refreshCount();
            });

        document.getElementById("bulk-select-all").addEventListener("click", () => {
            cards().forEach((c) => {
                // Skip cards hidden by client-side search/filter
                if (c.offsetParent === null) return;
                setSelected(c, true);
            });
            refreshCount();
        });

        // Clicking a card while in select mode toggles it (capture phase so it
        // wins over the card's own links).
        grid.addEventListener(
            "click",
            (e) => {
                if (!document.body.classList.contains("bulk-select-mode")) return;
                const card = e.target.closest(".card[data-set-id]");
                if (!card || !grid.contains(card)) return;
                e.preventDefault();
                e.stopPropagation();
                setSelected(card, !isSelected(card));
                refreshCount();
            },
            true,
        );

        // --- Field computation ----------------------------------------------

        function computeTristate(ctrl, cardEls) {
            const attr = "data-" + ctrl.dataset.cardAttr;
            let on = 0;
            cardEls.forEach((c) => {
                if (c.getAttribute(attr) !== null) on++;
            });
            if (on === 0) {
                ctrl.checked = false;
                ctrl.indeterminate = false;
            } else if (on === cardEls.length) {
                ctrl.checked = true;
                ctrl.indeterminate = false;
            } else {
                ctrl.checked = false;
                ctrl.indeterminate = true;
            }
        }

        function computeValue(ctrl, cardEls) {
            const attr = "data-" + ctrl.dataset.cardAttr;
            const raw = cardEls.map((c) => {
                const v = c.getAttribute(attr);
                return v === null ? "" : v;
            });
            const allEqual = raw.every((v) => v === raw[0]);
            removeVariesOption(ctrl);

            if (allEqual) {
                let v = raw[0];
                if (ctrl.type === "date") {
                    v =
                        ctrl.dataset.bulkField === "purchase_date"
                            ? tsToDateInput(v)
                            : slashToDateInput(v);
                }
                if (ctrl.tagName === "SELECT") ctrl.value = v == null ? "" : v;
                else ctrl.value = v;
                ctrl.placeholder = "";
            } else if (ctrl.tagName === "SELECT") {
                addVariesOption(ctrl);
            } else {
                ctrl.value = "";
                ctrl.placeholder = "— varies —";
            }
        }

        function computePanel(cardEls) {
            panel.querySelectorAll(".bulk-control").forEach((ctrl) => {
                if (ctrl.classList.contains("bulk-tristate")) {
                    computeTristate(ctrl, cardEls);
                } else {
                    computeValue(ctrl, cardEls);
                }
                ctrl.dataset.pristine = "true";
                ctrl.classList.remove("bulk-touched");
            });
        }

        // Touched tracking: only fields the user actually changes are applied.
        panel.querySelectorAll(".bulk-control").forEach((ctrl) => {
            const onTouch = () => {
                ctrl.dataset.pristine = "false";
                ctrl.classList.add("bulk-touched");
                removeVariesOption(ctrl);
                if (ctrl.classList.contains("bulk-tristate"))
                    ctrl.indeterminate = false;
            };
            ctrl.addEventListener("change", onTouch);
            ctrl.addEventListener("input", onTouch);
        });

        openBtn.addEventListener("click", () => {
            if (selected.size === 0) return;
            computePanel(Array.from(selected));
            bootstrap.Offcanvas.getOrCreateInstance(panel).show();
        });

        // --- Apply ----------------------------------------------------------

        applyBtn.addEventListener("click", async () => {
            const cardEls = Array.from(selected);
            if (cardEls.length === 0) return;

            // Expand consolidated cards into their real instance ids.
            const setIds = [];
            const seen = new Set();
            cardEls.forEach((c) => {
                const inst = c.getAttribute("data-instance-ids");
                const ids = inst
                    ? inst.split(/[\s,|]+/).filter(Boolean)
                    : [c.getAttribute("data-set-id")].filter(Boolean);
                ids.forEach((id) => {
                    if (!seen.has(id)) {
                        seen.add(id);
                        setIds.push(id);
                    }
                });
            });

            const changes = { tags: {}, statuses: {}, owners: {}, custom_fields: {} };

            panel.querySelectorAll(".bulk-control").forEach((ctrl) => {
                if (ctrl.dataset.pristine !== "false") return; // untouched
                const field = ctrl.dataset.bulkField;

                if (ctrl.classList.contains("bulk-tristate")) {
                    const id = ctrl.dataset.metaId;
                    const map =
                        field === "tag"
                            ? changes.tags
                            : field === "status"
                              ? changes.statuses
                              : changes.owners;
                    map[id] = ctrl.checked;
                } else if (field === "custom_field") {
                    let v = ctrl.value;
                    if (ctrl.type === "date") v = dateInputToSlash(v);
                    changes.custom_fields[ctrl.dataset.cfId] = v;
                } else if (field === "storage") {
                    changes.storage = ctrl.value;
                } else if (field === "purchase_location") {
                    changes.purchase_location = ctrl.value;
                } else if (field === "purchase_price") {
                    changes.purchase_price = ctrl.value;
                } else if (field === "purchase_date") {
                    changes.purchase_date = dateInputToSlash(ctrl.value);
                }
            });

            // Drop empty boolean/custom maps so the backend skips them.
            ["tags", "statuses", "owners", "custom_fields"].forEach((k) => {
                if (Object.keys(changes[k]).length === 0) delete changes[k];
            });

            applyBtn.disabled = true;
            try {
                const resp = await fetch(bulkUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ set_ids: setIds, changes: changes }),
                });
                if (!resp.ok)
                    throw new Error(`Response status: ${resp.status} (${resp.statusText})`);
                const json = await resp.json();
                if ("error" in json) throw new Error(json.error);
                window.location.reload();
            } catch (err) {
                applyBtn.disabled = false;
                alert("Bulk edit failed: " + err.message);
            }
        });
    }

    document.addEventListener("DOMContentLoaded", initBulkEdit);
})();
