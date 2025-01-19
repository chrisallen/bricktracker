// Sort button
class BrickGridSortButton {
    constructor(button, grid) {
        this.button = button;
        this.grid = grid;
        this.data = this.button.dataset;

        // Setup
        button.addEventListener("click", ((grid, button) => (e) => {
            grid.sort(button);
        })(grid, this));
    }

    // Active
    active() {
        this.button.classList.remove("btn-outline-primary");
        this.button.classList.add("btn-primary");
    }

    // Inactive
    inactive() {
        delete this.button.dataset.sortOrder;
        this.button.classList.remove("btn-primary");
        this.button.classList.add("btn-outline-primary");
    }

    // Toggle sorting
    toggle(order) {
        // Cleanup
        delete this.button.dataset.sortOrder;

        let icon = this.button.querySelector("i.ri");
        if (icon) {
            this.button.removeChild(icon);
        }

        // Set order
        if (order) {
            this.active();

            this.button.dataset.sortOrder = order;

            icon = document.createElement("i");
            icon.classList.add("ri", "ms-1", `ri-sort-${order}`);

            this.button.append(icon);
        }
    }
}

// Grid class
class BrickGrid {
    constructor(id) {
        this.id = id;

        // Grid elements (built based on the initial id)
        this.html_grid = document.getElementById(id);
        this.html_sort = document.getElementById(`${id}-sort`);
        this.html_search = document.getElementById(`${id}-search`);
        this.html_filter = document.getElementById(`${id}-filter`);
        this.html_theme = document.getElementById(`${id}-theme`);

        // Sort buttons
        this.html_sort_buttons = {};
        if (this.html_sort) {
            this.html_sort.querySelectorAll("button[data-sort-attribute]").forEach(button => {
                this.html_sort_buttons[button.id] = new BrickGridSortButton(button, this);
            });
        }

        // Clear button
        this.html_clear = document.querySelector("button[data-sort-clear]")
        if (this.html_clear) {
            this.html_clear.addEventListener("click", ((grid) => (e) => {
                grid.clear(e.currentTarget)
            })(this))
        }

        // Filter setup
        if (this.html_search) {
            this.html_search.addEventListener("keyup", ((grid) => () => {
                grid.filter();
            })(this));
        }

        if (this.html_filter) {
            this.html_filter.addEventListener("change", ((grid) => () => {
                grid.filter();
            })(this));
        }

        if (this.html_theme) {
            this.html_theme.addEventListener("change", ((grid) => () => {
                grid.filter();
            })(this));
        }

        // Cookie setup
        const cookies = document.cookie.split(";").reduce((acc, cookieString) => {
            const [key, value] = cookieString.split("=").map(s => s.trim().replace(/^"|"$/g, ""));
            if (key && value) {
                acc[key] = decodeURIComponent(value);
            }
            return acc;
        }, {});

        // Initial sort
        if ("sort-id" in cookies && cookies["sort-id"] in this.html_sort_buttons) {
            const current = this.html_sort_buttons[cookies["sort-id"]];

            if("sort-order" in cookies) {
                current.button.setAttribute("data-sort-order", cookies["sort-order"]);
            }

            this.sort(current, true);
        }
    }

    // Clear
    clear(current) {
        // Cleanup all
        for (const [id, button] of Object.entries(this.html_sort_buttons)) {
            button.toggle();
            button.inactive();
        }

        // Clear cookies
        document.cookie = `sort-id=""; Path=/; SameSite=strict`;
        document.cookie = `sort-order=""; Path=/; SameSite=strict`;

        // Reset sorting
        tinysort(current.dataset.sortTarget, {
            selector: "div",
            attr: "data-index",
            order: "asc",
        });

    }

    // Filter
    filter() {
        var filters = {};

        // Check if there is a search filter
        if (this.html_search && this.html_search.value != "") {
            filters["search"] = this.html_search.value.toLowerCase();
        }

        // Check if there is a set filter
        if (this.html_filter && this.html_filter.value != "") {
            if (this.html_filter.value.startsWith("-")) {
                filters["filter"] = this.html_filter.value.substring(1);
                filters["filter-target"] = "0";
            } else {
                filters["filter"] = this.html_filter.value;
                filters["filter-target"] = "1";
            }
        }

        // Check if there is a theme filter
        if (this.html_theme && this.html_theme.value != "") {
            filters["theme"] = this.html_theme.value;
        }

        // Filter all cards
        if (this.html_grid) {
            const cards = this.html_grid.querySelectorAll("div > div.card");
            cards.forEach(current => {
                // Set filter
                if ("filter" in filters) {
                    if (current.getAttribute("data-" + filters["filter"]) != filters["filter-target"]) {
                        current.parentElement.classList.add("d-none");
                        return;
                    }
                }

                // Theme filter
                if ("theme" in filters) {
                    if (current.getAttribute("data-theme") != filters["theme"]) {
                        current.parentElement.classList.add("d-none");
                        return;
                    }
                }

                // Check all searchable fields for a match
                if ("search" in filters) {
                    for (let attribute of ["data-name", "data-number", "data-parts", "data-theme", "data-year"]) {
                        if (current.getAttribute(attribute).includes(filters["search"])) {
                            current.parentElement.classList.remove("d-none");
                            return;
                        }
                    }

                    // If no match, we need to hide it
                    current.parentElement.classList.add("d-none");
                    return;
                }

                // If we passed all filters, we need to display it
                current.parentElement.classList.remove("d-none");
            })
        }
    }

    // Sort
    sort(current, no_flip=false) {
        const target = current.data.sortTarget;
        const attribute = current.data.sortAttribute;
        const natural = current.data.sortNatural;

        // Cleanup all
        for (const [id, button] of Object.entries(this.html_sort_buttons)) {
            if (button != current) {
                button.toggle();
                button.inactive();
            }
        }

        // Sort
        if (target && attribute) {
            let order = current.data.sortOrder;

            // First ordering
            if (!no_flip) {
                if(!order) {
                    if (current.data.sortDesc) {
                        order = "desc"
                    } else {
                        order = "asc"
                    }
                } else {
                    // Flip the sorting order
                    order = (order == "desc") ? "asc" : "desc";
                }
            }

            // Toggle the ordering
            current.toggle(order);

            // Store cookies
            document.cookie = `sort-id="${encodeURIComponent(current.button.id)}"; Path=/; SameSite=strict`;
            document.cookie = `sort-order="${encodeURIComponent(order)}"; Path=/; SameSite=strict`;

            // Do the sorting
            tinysort(target, {
                selector: "div",
                attr: "data-" + attribute,
                natural: natural == "true",
                order: order,
            });
        }
    }
}
