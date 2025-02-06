// Instructions Socket class
class BrickInstructionsSocket extends BrickSocket {
    constructor(id, path, namespace, messages) {
        super(id, path, namespace, messages, true);

        // Listeners
        this.download_listener = undefined;

        // Form elements (built based on the initial id)
        this.html_button = document.getElementById(id);
        this.html_files = document.getElementById(`${id}-files`);

        if (this.html_button) {
            this.download_listener = this.html_button.addEventListener("click", ((bricksocket) => (e) => {
                bricksocket.execute();
            })(this));
        }

        if (this.html_card_dismiss && this.html_card) {
            this.html_card_dismiss.addEventListener("click", ((card) => (e) => {
                card.classList.add("d-none");
            })(this.html_card));
        }

        // Setup the socket
        this.setup();
    }

    // Upon receiving a complete message
    complete(data) {
        super.complete(data);

        // Uncheck current file
        this.file.checked = false;

        // Download the next file
        this.download_instructions(true);
    }

    // Execute the action
    execute() {
        if (!this.disabled && this.socket !== undefined && this.socket.connected) {
            this.toggle(false);

            this.download_instructions();
        }
    }

    // Get the list of checkboxes describing files
    get_files(checked=false) {
        let files = [];

        if (this.html_files) {
            files = [...this.html_files.querySelectorAll('input[type="checkbox"]')];

            if (checked) {
                files = files.filter(file => file.checked);
            }
        }

        return files;
    }

    // Download an instructions file
    download_instructions(from_complete=false) {
        if (this.html_files) {
            if (!from_complete) {
                this.total = this.get_files(true).length;
                this.current = 0;
                this.clear();
            }

            // Find the next checkbox
            this.file = this.get_files(true).shift();

            // Abort if nothing left to process
            if (this.file === undefined) {
                // Settle the form
                this.spinner(false);
                this.toggle(true);

                return;
            }

            this.spinner(true);

            this.current++;
            this.socket.emit(this.messages.DOWNLOAD_INSTRUCTIONS, {
                alt: this.file.dataset.downloadAlt,
                href: this.file.dataset.downloadHref,
                total: this.total,
                current: this.current,
            });
        } else {
            this.fail("Could not find the list of files to download");
        }
    }

    // Toggle clicking on the button, or sending events
    toggle(enabled) {
        super.toggle(enabled);

        if (this.html_files) {
            this.get_files().forEach(el => el.disabled != enabled);
        }

        if (this.html_button) {
            this.html_button.disabled = !enabled;
        }
    }
}
