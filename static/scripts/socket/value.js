// Socket client for the bulk "value all sets" admin action. Connects, emits a
// single VALUE_ALL_SETS message and lets the generic BrickSocket base render
// the progress bar / completion message while the server prices each set.
class BrickValueSocket extends BrickSocket {
    constructor(id, path, namespace, messages) {
        // Single-shot operation (not bulk): the base complete() then stops the
        // spinner, shows the success message and re-enables the button.
        super(id, path, namespace, messages, false);

        this.html_button = document.getElementById(`${id}-button`);

        if (this.html_button) {
            this.html_button.addEventListener("click", ((bricksocket) => () => {
                bricksocket.start();
            })(this));
        }
    }

    // Kick off the server-side valuation
    start() {
        if (this.disabled) {
            return;
        }

        // Connect lazily on first use so the host page (e.g. the admin page)
        // does not open a socket until the action is actually triggered.
        this.setup();

        this.clear();
        this.spinner(true);
        this.toggle(false);

        this.socket.emit(this.messages.VALUE_ALL_SETS, {});
    }
}
