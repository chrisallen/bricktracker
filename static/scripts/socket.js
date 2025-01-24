// Socket class
class BrickSocket {
    constructor(id, path, namespace, messages, bulk=false) {
        this.id = id;
        this.path = path;
        this.namespace = namespace;
        this.messages = messages;
        this.bulk = bulk;

        this.disabled = false;
        this.socket = undefined;

        // Listeners
        this.add_listener = undefined;
        this.confirm_listener = undefined;

        // Form elements (built based on the initial id)
        this.html_button = document.getElementById(id);
        this.html_complete = document.getElementById(`${id}-complete`);
        this.html_count = document.getElementById(`${id}-count`);
        this.html_fail = document.getElementById(`${id}-fail`);
        this.html_input = document.getElementById(`${id}-set`);
        this.html_no_confim = document.getElementById(`${id}-no-confirm`);
        this.html_progress = document.getElementById(`${id}-progress`);
        this.html_progress_bar = document.getElementById(`${id}-progress-bar`);
        this.html_progress_message = document.getElementById(`${id}-progress-message`);
        this.html_spinner = document.getElementById(`${id}-spinner`);
        this.html_status = document.getElementById(`${id}-status`);
        this.html_status_icon = document.getElementById(`${id}-status-icon`);

        // Card elements
        this.html_card = document.getElementById(`${id}-card`);
        this.html_card_set = document.getElementById(`${id}-card-set`);
        this.html_card_name = document.getElementById(`${id}-card-name`);
        this.html_card_image_container = document.getElementById(`${id}-card-image-container`);
        this.html_card_image = document.getElementById(`${id}-card-image`);
        this.html_card_footer = document.getElementById(`${id}-card-footer`);
        this.html_card_confirm = document.getElementById(`${id}-card-confirm`);
        this.html_card_dismiss = document.getElementById(`${id}-card-dismiss`);

        if (this.html_button) {
            this.add_listener = ((bricksocket) => (e) => {
                if (!bricksocket.disabled && bricksocket.socket !== undefined && bricksocket.socket.connected) {
                    bricksocket.toggle(false);

                    // Split and save the list if bulk
                    if (bricksocket.bulk) {
                        bricksocket.read_set_list()
                    }

                    if (bricksocket.bulk || (bricksocket.html_no_confim && bricksocket.html_no_confim.checked)) {
                        bricksocket.import_set(true);
                    } else {
                        bricksocket.load_set();
                    }
                }
            })(this);

            this.html_button.addEventListener("click", this.add_listener);
        }

        if (this.html_card_dismiss && this.html_card) {
            this.html_card_dismiss.addEventListener("click", ((card) => (e) => {
                card.classList.add("d-none");
            })(this.html_card));
        }

        // Socket status
        window.setInterval(((bricksocket) => () => {
            bricksocket.status();
        })(this), 500);

        // Setup the socket
        this.setup();
    }

    // Clear form
    clear() {
        this.clear_status();

        if (this.html_count) {
            this.html_count.classList.add("d-none");
        }

        if(this.html_progress_bar) {
            this.html_progress.setAttribute("aria-valuenow", "0");
            this.html_progress_bar.setAttribute("style", "width: 0%");
            this.html_progress_bar.textContent = "";
        }

        this.spinner(false);

        if (this.html_card) {
            this.html_card.classList.add("d-none");
        }

        if (this.html_card_footer) {
            this.html_card_footer.classList.add("d-none");

            if (this.html_card_confirm) {
                this.html_card_footer.classList.add("d-none");
            }
        }
    }

    // Clear status message
    clear_status() {
        if (this.html_complete) {
            this.html_complete.classList.add("d-none");

            if (this.bulk) {
                this.html_complete.innerHTML = "";
            } else {
                this.html_complete.textContent = "";
            }
        }

        if (this.html_fail) {
            this.html_fail.classList.add("d-none");
            this.html_fail.textContent = "";
        }
    }

    // Upon receiving a complete message
    complete(data) {
        if(this.html_progress_bar) {
            this.html_progress.setAttribute("aria-valuenow", "100");
            this.html_progress_bar.setAttribute("style", "width: 100%");
            this.html_progress_bar.textContent = "100%";
        }

        if (this.bulk) {
            if (this.html_complete) {
                this.html_complete.classList.remove("d-none");

                // Create a message (not ideal as it is template inside code)
                const success = document.createElement("div");
                success.classList.add("alert", "alert-success");
                success.setAttribute("role", "alert");
                success.innerHTML = `<strong>Success:</strong> ${data.message}`

                this.html_complete.append(success)
            }

            // Import the next set
            this.import_set(true, undefined, true);
        } else {
            this.spinner(false);

            if (this.html_complete) {
                this.html_complete.classList.remove("d-none");
                this.html_complete.innerHTML = `<strong>Success:</strong> ${data.message}`;
            }

            if (this.html_fail) {
                this.html_fail.classList.add("d-none");
            }
        }
    }

    // Update the count
    count(count, total) {
        if (this.html_count) {
            this.html_count.classList.remove("d-none");

            // If there is no total, display a question mark instead
            if (total == 0) {
                total = "?"
            }

            this.html_count.textContent = `(${count}/${total})`;
        }
    }

    // Upon receiving a fail message
    fail(data) {
        this.spinner(false);

        if (this.html_fail) {
            this.html_fail.classList.remove("d-none", );
            this.html_fail.innerHTML = `<strong>Error:</strong> ${data.message}`;
        }

        if (!this.bulk && this.html_complete) {
            this.html_complete.classList.add("d-none");
        }

        if (this.html_progress_bar) {
            this.html_progress_bar.classList.remove("progress-bar-animated");
        }

        if (this.bulk && this.html_input) {
            if (this.set_list_last_set !== undefined) {
                this.set_list.unshift(this.set_list_last_set);
                this.set_list_last_set = undefined;
            }

            this.html_input.value = this.set_list.join(', ');
        }
    }

    // Import a set
    import_set(no_confirm, set, from_complete=false) {
        if (this.html_input) {
            if (!this.bulk || !from_complete) {
                // Reset the progress
                if (no_confirm) {
                    this.clear();
                } else {
                    this.clear_status();
                }
            }

            // Grab from the list if bulk
            if (this.bulk) {
                set = this.set_list.shift()

                // Abort if nothing left to process
                if (set === undefined) {
                    // Clear the input
                    this.html_input.value = "";

                    // Settle the form
                    this.spinner(false);
                    this.toggle(true);

                    return;
                }

                // Save the pulled set
                this.set_list_last_set = set;
            }

            this.spinner(true);

            this.socket.emit(this.messages.IMPORT_SET, {
                set: (set !== undefined) ? set : this.html_input.value,
            });
        } else {
            this.fail("Could not find the input field for the set number");
        }
    }

    // Load a set
    load_set() {
        if (this.html_input) {
            // Reset the progress
            this.clear()
            this.spinner(true);

            this.socket.emit(this.messages.LOAD_SET, {
                set: this.html_input.value
            });
        } else {
            this.fail("Could not find the input field for the set number");
        }
    }

    // Update the progress
    progress(data={}) {
        let total = data["total"];
        let count = data["count"]

        // Fix the total if bogus
        if (!total || isNaN(total) || total <= 1) {
            total = 0;
        }

        // Fix the count if bogus
        if (!count || isNaN(count) || count <= 1) {
            count = 1;
        }

        this.count(count, total);
        this.progress_message(data["message"]);

        if (this.html_progress && this.html_progress_bar) {
            // Infinite progress bar
            if (!total) {
                this.html_progress.setAttribute("aria-valuenow", "100");
                this.html_progress_bar.classList.add("progress-bar-striped", "progress-bar-animated");
                this.html_progress_bar.setAttribute("style", "width: 100%");
                this.html_progress_bar.textContent = "";
            } else {
                if (count > total) {
                    total = count;
                }

                const progress = (count - 1) * 100 / total;

                this.html_progress.setAttribute("aria-valuenow", progress);
                this.html_progress_bar.classList.remove("progress-bar-striped", "progress-bar-animated");
                this.html_progress_bar.setAttribute("style", `width: ${progress}%`);
                this.html_progress_bar.textContent = `${progress.toFixed(2)}%`;
            }
        }
    }

    // Update the progress message
    progress_message(message) {
        if (this.html_progress_message) {
            this.html_progress_message.classList.remove("d-none");
            this.html_progress_message.textContent = message;
        }
    }

    // Bulk: read the input as a list
    read_set_list() {
        this.set_list = [];

        if (this.html_input) {
            const value = this.html_input.value;
            this.set_list = value.split(",").map((el) => el.trim())
        }
    }

    // Set is loaded
    set_loaded(data) {
        if (this.html_card) {
            this.html_card.classList.remove("d-none");

            if (this.html_card_set) {
                this.html_card_set.textContent = data["set"];
            }

            if (this.html_card_name) {
                this.html_card_name.textContent = data["name"];
            }

            if (this.html_card_image_container) {
                this.html_card_image_container.setAttribute("style", `background-image: url(${data["image"]})`);
            }

            if (this.html_card_image) {
                this.html_card_image.setAttribute("src", data["image"]);
                this.html_card_image.setAttribute("alt", data["set"]);
            }

            if (this.html_card_footer) {
                this.html_card_footer.classList.add("d-none");

                if (!data.download) {
                    this.html_card_footer.classList.remove("d-none");

                    if (this.html_card_confirm) {
                        if (this.confirm_listener !== undefined) {
                            this.html_card_confirm.removeEventListener("click", this.confirm_listener);
                        }

                        this.confirm_listener = ((bricksocket, set) => (e) => {
                            if (!bricksocket.disabled) {
                                bricksocket.toggle(false);
                                bricksocket.import_set(false, set);
                            }
                        })(this, data["set"]);

                        this.html_card_confirm.addEventListener("click", this.confirm_listener);
                    }
                }
            }
        }
    }

    // Setup the actual socket
    setup() {
        if (this.socket === undefined) {
            this.socket = io.connect(`${window.location.origin}/${this.namespace}`, {
                path: this.path,
                transports: ["websocket"],
            });

            // Complete
            this.socket.on(this.messages.COMPLETE, ((bricksocket) => (data) => {
                bricksocket.complete(data);
                if (!bricksocket.bulk) {
                    bricksocket.toggle(true);
                }
            })(this));

            // Fail
            this.socket.on(this.messages.FAIL, ((bricksocket) => (data) => {
                bricksocket.fail(data);
                bricksocket.toggle(true);
            })(this));

            // Progress
            this.socket.on(this.messages.PROGRESS, ((bricksocket) => (data) => {
                bricksocket.progress(data);
            })(this));

            // Set loaded
            this.socket.on(this.messages.SET_LOADED, ((bricksocket) => (data) => {
                bricksocket.set_loaded(data);
            })(this));
        }
    }

    // Toggle the spinner
    spinner(show) {
        if (this.html_spinner) {
            if (show) {
                this.html_spinner.classList.remove("d-none");
            } else {
                this.html_spinner.classList.add("d-none");
            }
        }
    }

    // Toggle the status
    status() {
        if (this.html_status) {
            if (this.socket === undefined) {
                this.html_status.textContent = "Socket is not initialized";
                if (this.html_status_icon) {
                    this.html_status_icon.classList.remove("ri-checkbox-circle-fill", "ri-close-circle-fill");
                    this.html_status_icon.classList.add("ri-question-fill");
                }
            } else if (this.socket.connected) {
                this.html_status.textContent = "Socket is connected";
                if (this.html_status_icon) {
                    this.html_status_icon.classList.remove("ri-question-fill", "ri-close-circle-fill");
                    this.html_status_icon.classList.add("ri-checkbox-circle-fill");
                }
            } else {
                this.html_status.textContent = "Socket is disconnected";
                if (this.html_status_icon) {
                    this.html_status_icon.classList.remove("ri-question-fill", "ri-checkbox-circle-fill");
                    this.html_status_icon.classList.add("ri-close-circle-fill");
                }
            }
        }
    }

    // Toggle clicking on the button, or sending events
    toggle(enabled) {
        this.disabled = !enabled;

        if (this.html_button) {
            this.html_button.disabled = !enabled;
        }

        if (this.html_input) {
            this.html_input.disabled = !enabled;
        }

        if (this.html_card_confirm) {
            this.html_card_confirm.disabled = !enabled;
        }

        if (this.html_card_dismiss) {
            this.html_card_dismiss.disabled = !enabled;
        }
    }
}
