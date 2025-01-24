// Clean a status indicator
const clean_status = (status) => {
    const to_remove = Array.from(status.classList.values()).filter((name) => name.startsWith('ri-') || name.startsWith('text-') || name.startsWith('bg-'))

    if (to_remove.length) {
        status.classList.remove(...to_remove);
    }
}

// Change the amount of missing parts
const change_part_missing_amount = async (el, set_id, part_id, url) => {
    const status = document.getElementById(`status-part-${set_id}-${part_id}`);

    try {
        // Set the status to unknown
        if (status) {
            clean_status(status)
            status.classList.add("ri-question-line", "bg-warning-subtle");
        }

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                missing: el.value
            })
        });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const json = await response.json();

        if ("error" in json) {
            throw new Error(`Error received: ${json.error}`);
        }

        // Set the status to OK
        if (status) {
            clean_status(status)
            status.classList.add("ri-checkbox-circle-line", "text-success", "bg-success-subtle");
        }

        // Update the sort data
        const sort = document.getElementById(`sort-part-${set_id}-${part_id}`);
        if (sort) {
            sort.dataset.sort = el.value;
        }

    } catch (error) {
        console.log(error.message);

        // Set the status to not OK
        if (status) {
            clean_status(status)
            status.classList.add("ri-alert-line", "text-danger", "bg-danger-subtle");
        }
    }
}
