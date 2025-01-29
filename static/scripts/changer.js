// Generic state changer with visual feedback
class BrickChanger {
    constructor(prefix, id, url, parent = undefined) {
        this.prefix = prefix
        this.html_element = document.getElementById(`${prefix}-${id}`);
        this.html_clear = document.getElementById(`clear-${prefix}-${id}`);
        this.html_status = document.getElementById(`status-${prefix}-${id}`);
        this.html_type = this.html_element.getAttribute("type");
        this.url = url;

        if (parent) {
            this.html_parent = document.getElementById(`${parent}-${id}`);
            this.parent_dataset = `data-${prefix}`
        }

        // Register an event depending on the type
        if (this.html_type == "checkbox") {
            var listener = "change";
        } else if(this.html_type == "text") {
            var listener = "change";
        } else {
            throw Error("Unsupported input type for BrickChanger");
        }

        this.html_element.addEventListener(listener, ((changer) => (e) => {
            changer.change();
        })(this));

        if (this.html_clear) {
            this.html_clear.addEventListener("click", ((changer) => (e) => {
                changer.html_element.value = "";
                changer.change();
            })(this));
        }
    }

    // Clean the status
    status_clean() {
        if (this.html_status) {
            const to_remove = Array.from(
                this.html_status.classList.values()
            ).filter(
                (name) => name.startsWith('ri-') || name.startsWith('text-') || name.startsWith('bg-')
            );

            if (to_remove.length) {
                this.html_status.classList.remove(...to_remove);
            }
        }
    }

    // Set the status to Error
    status_error() {
        if (this.html_status) {
            this.status_clean();
            this.html_status.classList.add("ri-alert-line", "text-danger");
        }
    }

    // Set the status to OK
    status_ok() {
        if (this.html_status) {
            this.status_clean();
            this.html_status.classList.add("ri-checkbox-circle-line", "text-success");
        }
    }

    // Set the status to Unknown
    status_unknown() {
        if (this.html_status) {
            this.status_clean();
            this.html_status.classList.add("ri-question-line", "text-warning");
        }
    }

    async change() {
        try {
            this.status_unknown();

            // Grab the value depending on the type
            if (this.html_type == "checkbox") {
                var value = this.html_element.checked;
            } else if(this.html_type == "text") {
                var value = this.html_element.value;
            } else {
                throw Error("Unsupported input type for BrickChanger");
            }

            const response = await fetch(this.url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: this.prefix,
                    value: value,
                })
            });

            if (!response.ok) {
                throw new Error(`Response status: ${response.status}`);
            }

            const json = await response.json();

            if ("error" in json) {
                throw new Error(`Error received: ${json.error}`)
            }

            this.status_ok();

            // Update the parent
            if (this.html_parent) {
                if (this.html_type == "checkbox") {
                    value = Number(value)
                }

                // Not going through dataset to avoid converting
                this.html_parent.setAttribute(this.parent_dataset, value);
            }
        } catch (error) {
            console.log(error.message);

            this.status_error();
        }
    }
}

// Helper to setup the changer
const setup_changers = () => document.querySelectorAll("*[data-changer-id]").forEach(
    el => new BrickChanger(
        el.dataset.changerPrefix,
        el.dataset.changerId,
        el.dataset.changerUrl,
        el.dataset.changerParent
    )
);