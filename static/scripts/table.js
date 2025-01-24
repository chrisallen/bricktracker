class BrickTable {
    constructor(id, per_page, no_sort = [], number = []) {
        const columns = [];

        if (no_sort.length) {
            columns.push({ select: no_sort, sortable: false, searchable: false });
        }

        if (number.length) {
            columns.push({ select: number, type: "number", searchable: false });
        }

        this.table = new simpleDatatables.DataTable(`#${id}`, {
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
