// Grid class
class BrickGrid {
    constructor(grid, target = "div#grid>div") {
        this.id = grid.id;
        this.target = target;

        // Grid elements (built based on the initial id)
        this.html_grid = document.getElementById(this.id);

        if (this.html_grid) {
            // Sort setup
            this.sort = new BrickGridSort(this);

            // Filter setup
            this.filter = new BrickGridFilter(this);
        }
    }
}

// Helper to setup the grids
const setup_grids = () => document.querySelectorAll('*[data-grid="true"]').forEach(
    el => new BrickGrid(el)
);
