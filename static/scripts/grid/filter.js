// Grid filter
class BrickGridFilter {
    constructor(grid) {
        this.grid = grid;

        // Grid sort elements (built based on the initial id)
        this.html_search = document.getElementById(`${this.grid.id}-search`);
        this.html_status = document.getElementById(`${this.grid.id}-status`);
        this.html_theme = document.getElementById(`${this.grid.id}-theme`);

        // Filter setup
        if (this.html_search) {
            this.html_search.addEventListener("keyup", ((grid) => () => {
                grid.filter();
            })(this));
        }

        if (this.html_status) {
            this.html_status.addEventListener("change", ((grid) => () => {
                grid.filter();
            })(this));
        }

        if (this.html_theme) {
            this.html_theme.addEventListener("change", ((grid) => () => {
                grid.filter();
            })(this));
        }
    }

    // Filter
    filter() {
        var filters = {};

        // Check if there is a search filter
        if (this.html_search && this.html_search.value != "") {
            filters["search"] = this.html_search.value.toLowerCase();
        }

        // Check if there is a set filter
        if (this.html_status && this.html_status.value != "") {
            if (this.html_status.value.startsWith("-")) {
                filters["filter"] = this.html_status.value.substring(1);
                filters["filter-target"] = "0";
            } else {
                filters["filter"] = this.html_status.value;
                filters["filter-target"] = "1";
            }
        }

        // Check if there is a theme filter
        if (this.html_theme && this.html_theme.value != "") {
            filters["theme"] = this.html_theme.value;
        }

        // Filter all cards
        const cards = this.grid.html_grid.querySelectorAll(`${this.grid.target} > .card`);
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
        });
    }
}
