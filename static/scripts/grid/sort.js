// Grid sort
class BrickGridSort {
    constructor(grid) {
        this.grid = grid;

        // Grid sort elements (built based on the initial id)
        this.html_sort = document.getElementById(`${this.grid.id}-sort`);

        if (this.html_sort) {
            // Cookie names
            this.cookie_id = `${this.grid.id}-sort-id`;
            this.cookie_order = `${this.grid.id}-sort-order`;

            // Sort buttons
            this.html_sort_buttons = {};
            this.html_sort.querySelectorAll("button[data-sort-attribute]").forEach(button => {
                this.html_sort_buttons[button.id] = new BrickGridSortButton(button, this);
            });

            // Clear button
            this.html_clear = this.html_sort.querySelector("button[data-sort-clear]")
            if (this.html_clear) {
                this.html_clear.addEventListener("click", ((gridsort) => () => {
                    gridsort.clear();
                })(this))
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
            if (this.cookie_id in cookies && cookies[this.cookie_id] in this.html_sort_buttons) {
                const current = this.html_sort_buttons[cookies[this.cookie_id]];

                if(this.cookie_order in cookies) {
                    current.button.setAttribute("data-sort-order", cookies[this.cookie_order]);
                }

                this.sort(current, true);
            }
        }
    }

    // Clear sort
    clear() {
        // Cleanup all
        for (const [id, button] of Object.entries(this.html_sort_buttons)) {
            button.toggle();
            button.inactive();
        }

        // Clear cookies
        document.cookie = `${this.cookie_id}=""; Path=/; SameSite=strict`;
        document.cookie = `${this.cookie_order}=""; Path=/; SameSite=strict`;

        // Reset sorting
        tinysort(this.grid.target, {
            selector: "div",
            attr: "data-index",
            order: "asc",
        });

    }

    // Sort
    sort(current, no_flip=false) {
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
        if (attribute) {
            let order = current.data.sortOrder;

            // First ordering
            if (!no_flip) {
                if(!order) {
                    if (current.data.sortDesc) {
                        order = "desc";
                    } else {
                        order = "asc";
                    }
                } else {
                    // Flip the sorting order
                    order = (order == "desc") ? "asc" : "desc";
                }
            }

            // Toggle the ordering
            current.toggle(order);

            // Store cookies
            document.cookie = `${this.cookie_id}="${encodeURIComponent(current.button.id)}"; Path=/; SameSite=strict`;
            document.cookie = `${this.cookie_order}="${encodeURIComponent(order)}"; Path=/; SameSite=strict`;

            // Do the sorting
            tinysort(this.grid.target, {
                selector: "div",
                attr: "data-" + attribute,
                natural: natural == "true",
                order: order,
            });
        }
    }
}
