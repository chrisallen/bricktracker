// Grid filter
class BrickGridFilter {
    constructor(grid) {
        this.grid = grid;

        // Grid sort elements (built based on the initial id)
        this.html_search = document.getElementById(`${this.grid.id}-search`);
        this.html_search_clear = document.getElementById(`${this.grid.id}-search-clear`);
        this.html_filter = document.getElementById(`${this.grid.id}-filter`);

        // Search setup
        if (this.html_search) {
            // Exact attributes
            if (this.html_search.dataset.searchExact) {
                this.search_exact = new Set(this.html_search.dataset.searchExact.split(",").map(el => el.trim()));
            } else {
                this.search_exact = new Set();
            }

            // List attributes
            this.search_list = [];
            if (this.html_search.dataset.searchList) {
                this.search_list = this.html_search.dataset.searchList.split(",").map(el => el.trim());
            }

            this.html_search.addEventListener("keyup", ((gridfilter) => () => {
                gridfilter.filter();
            })(this));

            if (this.html_search_clear) {
                this.html_search_clear.addEventListener("click", ((gridfilter) => () => {
                    this.html_search.value = '';
                    gridfilter.filter();
                })(this));
            }
        }

        // Filters setup
        this.selects = [];
        if (this.html_filter) {
            this.html_filter.querySelectorAll("select[data-filter]").forEach(select => {
                select.addEventListener("change", ((gridfilter) => () => {
                    gridfilter.filter();
                })(this));
                this.selects.push(select);
            });
        }

        if (this.html_theme) {
            this.html_theme.addEventListener("change", ((grid) => () => {
                grid.filter();
            })(this));
        }
    }

    // Filter
    filter() {
        let options = {
            search: undefined,
            filters: [],
        };

        // Check if there is a search filter
        if (this.html_search && this.html_search.value != "") {
            options.search = this.html_search.value.toLowerCase();
        }

        // Build filters
        for (const select of this.selects) {
            if (select.value != "") {
                // Multi-attribute filter
                switch (select.dataset.filter) {
                    // List contains values
                    case "value":
                        options.filters.push({
                            attribute: select.dataset.filterAttribute,
                            value: select.value,
                        })
                    break;

                    // List contains metadata attribute name, looking for true/false
                    case "metadata":
                        if (select.value.startsWith("-")) {
                            options.filters.push({
                                attribute: select.value.substring(1),
                                bool: true,
                                value: "0"
                            })
                        } else {
                            options.filters.push({
                                attribute: select.value,
                                bool: true,
                                value: "1"
                            })
                        }
                    break;
                }
            }
        }

        // Filter all cards
        const cards = this.grid.html_grid.querySelectorAll(`${this.grid.target} > .card`);
        cards.forEach(current => {
            // Process all filters
            for (const filter of options.filters) {
                const attribute = current.getAttribute(`data-${filter.attribute}`);

                // Bool check
                // Attribute not equal value, or undefined and value is truthy
                if (filter.bool) {
                    if ((attribute != null && attribute != filter.value) || (attribute == null && filter.value == "1")) {
                        current.parentElement.classList.add("d-none");
                        return;
                    }
                }

                // Value check
                // Attribute not equal value, or attribute undefined
                else if ((attribute != null && attribute != filter.value) || attribute == null) {
                    current.parentElement.classList.add("d-none");
                    return;
                }
            }

            // Check all searchable fields for a match
            if (options.search) {
                // Browse the whole dataset
                for (const set in current.dataset) {
                    // Exact attribute
                    if (this.search_exact.has(set)) {
                        if (current.dataset[set].includes(options.search)) {
                            current.parentElement.classList.remove("d-none");
                            return;
                        }
                    } else {
                        // List search
                        for (const list of this.search_list) {
                            if (set.startsWith(list)) {
                                if (current.dataset[set].includes(options.search)) {
                                    current.parentElement.classList.remove("d-none");
                                    return;
                                }
                            }
                        }
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
