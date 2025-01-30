// Grid sort button
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
