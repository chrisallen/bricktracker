class BrickTable {
    constructor(table, per_page) {
        const columns = [];
        const no_sort_and_filter = [];
        const no_sort = [];
        const number = [];

        // Read the table header for parameters
        table.querySelectorAll('th').forEach((th, index) => {
            if (th.dataset.tableNoSortAndFilter) {
                no_sort_and_filter.push(index);
            }

            if (th.dataset.tableNoSort) {
                no_sort.push(index);
            }

            if (th.dataset.tableNumber) {
                number.push(index);
            }
        });

        if (no_sort_and_filter.length) {
            columns.push({ select: no_sort_and_filter, sortable: false, searchable: false });
        }

        if (no_sort.length) {
            columns.push({ select: no_sort, sortable: false });
        }

        if (number.length) {
            columns.push({ select: number, type: "number", searchable: false });
        }

        this.table = new simpleDatatables.DataTable(`#${table.id}`, {
            columns: columns,
            pagerDelta: 1,
            perPage: per_page,
            perPageSelect: [10, 25, 50, 100, 500, 1000],
            searchable: true,
            searchMethod: (table => (terms, cell, row, column, source) => table.search(terms, cell, row, column, source))(this),
            searchQuerySeparator: "",
            tableRender: () => {
              baguetteBox.run("[data-lightbox]");
            },
            pagerRender: () => {
              baguetteBox.run("[data-lightbox]");
            }
        });
    }

    // Custom search method
    // Very simplistic but will exclude pill links
    search(terms, cell, row, column, source) {
        // Create a searchable string from the data stack ignoring data-search="exclude"
        const search = this.buildSearch(cell.data).filter(data => data != "").join(" ");

        // Search it
        for (const term of terms) {
            if (search.includes(term)) {
                return true;
            }
        }

        return false;
    }

    // Build the search string
    buildSearch(dataList) {
        let search = [];

        for (const data of dataList) {
            // Exclude
            if (data.attributes && data.attributes['data-search'] && data.attributes['data-search'] == 'exclude') {
                continue;
            }

            // Childnodes
            if (data.childNodes) {
                search = search.concat(this.buildSearch(data.childNodes));
            }

            // Data
            if(data.data) {
                search.push(data.data.trim().toLowerCase());
            }
        }

        return search;
    }
}

// Helper to setup the tables
const setup_tables = (per_page) => document.querySelectorAll('table[data-table="true"]').forEach(
    el => new BrickTable(el, per_page)
);
