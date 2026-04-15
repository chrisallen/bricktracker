// Add parts page - handles individual parts and lots
document.addEventListener("DOMContentLoaded", () => {
  // Get template data from data attributes
  const addPartInput = document.getElementById('add-part-input');
  if (!addPartInput) return;

  // Read data from data attributes
  const templateData = {
    path: addPartInput.dataset.path,
    namespace: addPartInput.dataset.namespace,
    messages: {
      COMPLETE: addPartInput.dataset.msgComplete,
      CREATE_LOT: addPartInput.dataset.msgCreateLot,
      FAIL: addPartInput.dataset.msgFail,
      LOAD_PART: addPartInput.dataset.msgLoadPart,
      LOAD_PART_COLORS: addPartInput.dataset.msgLoadPartColors,
      PART_COLORS_LOADED: addPartInput.dataset.msgPartColorsLoaded,
      PROGRESS: addPartInput.dataset.msgProgress,
      PART_LOADED: addPartInput.dataset.msgPartLoaded,
    }
  };

  // Initialize the socket
  const partSocket = new BrickPartColorSocket(
    'add-part',
    templateData.path,
    templateData.namespace,
    {
      COMPLETE: templateData.messages.COMPLETE,
      CREATE_LOT: templateData.messages.CREATE_LOT,
      CREATE_BULK_INDIVIDUAL_PARTS: 'create_bulk_individual_parts',
      FAIL: templateData.messages.FAIL,
      LOAD_PART: templateData.messages.LOAD_PART,
      LOAD_PART_COLORS: templateData.messages.LOAD_PART_COLORS,
      PART_COLORS_LOADED: templateData.messages.PART_COLORS_LOADED,
      PROGRESS: templateData.messages.PROGRESS,
      PART_LOADED: templateData.messages.PART_LOADED,
    }
  );
});

// Individual Part Color Selection Socket class
class BrickPartColorSocket extends BrickSocket {
  constructor(id, path, namespace, messages) {
    super(id, path, namespace, messages, false);

    // Form elements
    this.html_button = document.getElementById(id + '-lookup');
    this.html_input = document.getElementById(`${id}-input`);
    this.html_owners = document.getElementById(`${id}-owners`);
    this.html_purchase_location = document.getElementById(`${id}-purchase-location`);
    this.html_purchase_date = document.getElementById(`${id}-purchase-date`);
    this.html_purchase_price = document.getElementById(`${id}-purchase-price`);
    this.html_storage = document.getElementById(`${id}-storage`);
    this.html_tags = document.getElementById(`${id}-tags`);

    // Color selection elements
    this.html_colors_section = document.getElementById(`${id}-colors-section`);
    this.html_colors_grid = document.getElementById(`${id}-colors-grid`);
    this.html_metadata_section = document.getElementById(`${id}-metadata-section`);

    // Add mode elements (radio buttons)
    this.html_single_mode = document.getElementById(`${id}-single-mode`);
    this.html_bulk_mode = document.getElementById(`${id}-bulk-mode`);
    this.html_lot_mode = document.getElementById(`${id}-lot-mode`);
    this.html_cart_section = document.getElementById(`${id}-cart-section`);
    this.html_cart_items = document.getElementById(`${id}-cart-items`);
    this.html_cart_count = document.getElementById(`${id}-cart-count`);
    this.html_complete_lot = document.getElementById(`${id}-complete-lot`);
    this.html_complete_button_text = document.getElementById(`${id}-complete-button-text`);
    this.html_clear_cart = document.getElementById(`${id}-clear-cart`);

    // State
    this.current_part = null;
    this.current_part_name = null;
    this.current_colors = null;
    this.selected_color = null;

    // Cart state
    this.add_mode = 'single'; // 'single', 'bulk', or 'lot'
    this.cart = []; // Array of {part, part_name, color_id, color_name, quantity, color_info}

    if (this.html_button) {
      this.html_button.addEventListener("click", ((bricksocket) => (e) => {
        bricksocket.lookup_part();
      })(this));
    }

    if (this.html_input) {
      this.html_input.addEventListener("keyup", ((bricksocket) => (e) => {
        if (e.key === 'Enter') {
          bricksocket.lookup_part();
        }
      })(this));
    }

    // Add mode radio buttons
    if (this.html_single_mode) {
      this.html_single_mode.addEventListener("change", ((bricksocket) => (e) => {
        if (e.target.checked) bricksocket.update_add_mode('single');
      })(this));
    }
    if (this.html_bulk_mode) {
      this.html_bulk_mode.addEventListener("change", ((bricksocket) => (e) => {
        if (e.target.checked) bricksocket.update_add_mode('bulk');
      })(this));
    }
    if (this.html_lot_mode) {
      this.html_lot_mode.addEventListener("change", ((bricksocket) => (e) => {
        if (e.target.checked) bricksocket.update_add_mode('lot');
      })(this));
    }

    // Clear cart button
    if (this.html_clear_cart) {
      this.html_clear_cart.addEventListener("click", ((bricksocket) => (e) => {
        bricksocket.clear_cart();
      })(this));
    }

    // Complete lot button
    if (this.html_complete_lot) {
      this.html_complete_lot.addEventListener("click", ((bricksocket) => (e) => {
        bricksocket.complete_lot();
      })(this));
    }

    // CSV file input
    this.html_csv_file = document.getElementById(`${id}-csv-file`);
    this.html_import_csv = document.getElementById(`${id}-import-csv`);

    if (this.html_csv_file) {
      this.html_csv_file.addEventListener("change", ((bricksocket) => (e) => {
        // Enable/disable import button based on file selection
        if (bricksocket.html_import_csv) {
          bricksocket.html_import_csv.disabled = !e.target.files || e.target.files.length === 0;
        }
      })(this));
    }

    if (this.html_import_csv) {
      this.html_import_csv.addEventListener("click", ((bricksocket) => () => {
        bricksocket.import_csv();
      })(this));
    }

    // Setup the socket
    this.setup();
  }

  // Clear form
  clear() {
    super.clear();

    if (this.html_colors_section) {
      this.html_colors_section.classList.add("d-none");
    }

    if (this.html_colors_grid) {
      this.html_colors_grid.innerHTML = '';
    }

    if (this.html_metadata_section) {
      this.html_metadata_section.classList.add("d-none");
    }

    this.current_part = null;
    this.current_part_name = null;
    this.current_colors = null;
    this.selected_color = null;
  }

  // Look up part and load available colors
  lookup_part() {
    if (this.disabled) {
      return;
    }

    const part = this.html_input.value.trim();

    if (!part) {
      this.fail({ message: 'Please enter a part number' });
      return;
    }

    // Clear previous results
    this.clear();

    this.clear_status();
    this.toggle(false);
    this.spinner(true);

    console.log('Emitting LOAD_PART_COLORS event with part:', part);
    this.socket.emit(this.messages.LOAD_PART_COLORS, { part: part });
  }

  // Create a color card element
  create_color_card(color) {
    const col = document.createElement('div');
    col.className = 'col';

    const card = document.createElement('div');
    card.className = 'card h-100';

    // Card image
    const imgContainer = document.createElement('div');
    imgContainer.className = 'card-img-top';
    imgContainer.style.height = '150px';
    imgContainer.style.backgroundImage = `url(${color.part_img_url || ''})`;
    imgContainer.style.backgroundSize = 'contain';
    imgContainer.style.backgroundRepeat = 'no-repeat';
    imgContainer.style.backgroundPosition = 'center';

    const img = document.createElement('img');
    img.src = color.part_img_url || '';
    img.alt = color.color_name;
    img.className = 'd-none';
    img.loading = 'lazy';
    imgContainer.appendChild(img);

    // Card body
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body p-2';

    const colorName = document.createElement('h6');
    colorName.className = 'card-title mb-1';
    colorName.textContent = color.color_name;

    const colorId = document.createElement('small');
    colorId.className = 'text-muted';
    colorId.textContent = `ID: ${color.color_id}`;

    cardBody.appendChild(colorName);
    cardBody.appendChild(colorId);

    // Card footer with quantity input and add button
    const cardFooter = document.createElement('div');
    cardFooter.className = 'card-footer p-2';

    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group input-group-sm';

    const quantityInput = document.createElement('input');
    quantityInput.type = 'number';
    quantityInput.className = 'form-control';
    quantityInput.placeholder = 'Qty';
    quantityInput.value = '1';
    quantityInput.min = '1';
    quantityInput.id = `qty-${color.color_id}`;

    const addButton = document.createElement('button');
    addButton.className = 'btn btn-primary';
    addButton.innerHTML = '<i class="ri-add-line"></i> Add';
    addButton.onclick = ((bricksocket, colorData, qtyInput) => () => {
      bricksocket.add_part_with_color(colorData, parseInt(qtyInput.value) || 1);
    })(this, color, quantityInput);

    inputGroup.appendChild(quantityInput);
    inputGroup.appendChild(addButton);
    cardFooter.appendChild(inputGroup);

    // Assemble card
    card.appendChild(imgContainer);
    card.appendChild(cardBody);
    card.appendChild(cardFooter);
    col.appendChild(card);

    return col;
  }

  // Add part with selected color
  add_part_with_color(color, quantity) {
    if (this.disabled) {
      return;
    }

    console.log('Adding part with color:', color, 'quantity:', quantity);

    // Clear previous status messages
    this.clear_status();

    // If in bulk or lot mode, add to cart instead of adding immediately
    if (this.add_mode === 'bulk' || this.add_mode === 'lot') {
      this.add_to_cart(color, quantity);
      return;
    }

    // Collect owners
    const owners = [];
    if (this.html_owners) {
      this.html_owners.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
        owners.push(cb.value);
      });
    }

    // Collect tags
    const tags = [];
    if (this.html_tags) {
      this.html_tags.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
        tags.push(cb.value);
      });
    }

    const data = {
      part: this.current_part,
      part_name: this.current_part_name,
      color: color.color_id,
      color_info: color,
      quantity: quantity,
      description: '',  // No description field in this UI
      owners: owners,
      tags: tags,
      storage: this.html_storage ? this.html_storage.value : null,
      purchase_location: this.html_purchase_location ? this.html_purchase_location.value : null,
      purchase_date: this.html_purchase_date ? this.html_purchase_date.value : null,
      purchase_price: this.html_purchase_price ? parseFloat(this.html_purchase_price.value) : null
    };

    this.clear_status();
    this.toggle(false);
    this.spinner(true);

    console.log('Emitting LOAD_PART event with data:', data);
    this.socket.emit(this.messages.LOAD_PART, data);
  }

  // Update add mode (single, bulk, or lot)
  update_add_mode(mode) {
    this.add_mode = mode;

    // Show/hide cart section based on mode
    if (this.html_cart_section) {
      if (mode === 'bulk' || mode === 'lot') {
        this.html_cart_section.classList.remove("d-none");
      } else {
        this.html_cart_section.classList.add("d-none");
        // Clear cart when switching to single mode
        this.clear_cart();
      }
    }

    // Update button text based on mode
    if (this.html_complete_button_text) {
      if (mode === 'bulk') {
        this.html_complete_button_text.textContent = 'Add All Parts';
      } else if (mode === 'lot') {
        this.html_complete_button_text.textContent = 'Complete Lot & Add All Parts';
      }
    }
  }

  // Add part to cart
  add_to_cart(color, quantity) {
    const cart_item = {
      part: this.current_part,
      part_name: this.current_part_name,
      color_id: color.color_id,
      color_name: color.color_name,
      quantity: quantity,
      color_info: color
    };

    this.cart.push(cart_item);
    this.render_cart();
    this.progress_message(`Added ${this.current_part} in ${color.color_name} to cart (${this.cart.length} items)`);
  }

  // Remove item from cart
  remove_from_cart(index) {
    this.cart.splice(index, 1);
    this.render_cart();
  }

  // Clear entire cart
  clear_cart() {
    this.cart = [];
    this.render_cart();
    this.clear_status();
  }

  // Render cart items
  render_cart() {
    if (!this.html_cart_items) return;

    this.html_cart_items.innerHTML = '';

    if (this.cart.length === 0) {
      this.html_cart_items.innerHTML = '<p class="text-muted text-center">Cart is empty</p>';
      if (this.html_complete_lot) {
        this.html_complete_lot.disabled = true;
      }
    } else {
      this.cart.forEach((item, index) => {
        const cartItem = document.createElement('div');
        cartItem.className = 'card mb-2';

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body p-2 d-flex justify-content-between align-items-center';

        const info = document.createElement('div');
        info.innerHTML = `
          <strong>${item.part}</strong> - ${item.part_name}<br>
          <small class="text-muted">Color: ${item.color_name}, Qty: ${item.quantity}</small>
        `;

        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn btn-sm btn-outline-danger';
        removeBtn.innerHTML = '<i class="ri-delete-bin-line"></i>';
        removeBtn.onclick = () => this.remove_from_cart(index);

        cardBody.appendChild(info);
        cardBody.appendChild(removeBtn);
        cartItem.appendChild(cardBody);
        this.html_cart_items.appendChild(cartItem);
      });

      if (this.html_complete_lot) {
        this.html_complete_lot.disabled = false;
      }
    }

    // Update cart count badge
    if (this.html_cart_count) {
      this.html_cart_count.textContent = this.cart.length;
    }
  }

  // Complete lot and add all parts
  complete_lot() {
    if (this.cart.length === 0) {
      this.fail({message: 'Cart is empty. Add parts before completing the lot.'});
      return;
    }

    this.clear_status();
    this.toggle(false);
    this.spinner(true);

    // Prepare cart data - convert to format expected by backend
    const cart_data = this.cart.map(item => ({
      part: item.part,
      part_name: item.part_name,
      color_id: item.color_id,
      color_name: item.color_name,
      quantity: item.quantity,
      color_info: item.color_info
    }));

    // Gather metadata from form
    const data = {
      cart: cart_data,
      name: null,  // Could add optional lot name field
      description: null,  // Could add optional lot description field
      storage: this.html_storage ? (this.html_storage.value || '') : '',
      purchase_location: this.html_purchase_location ? (this.html_purchase_location.value || '') : '',
      purchase_date: this.html_purchase_date && this.html_purchase_date.value ? new Date(this.html_purchase_date.value).getTime() / 1000 : null,
      purchase_price: this.html_purchase_price && this.html_purchase_price.value ? parseFloat(this.html_purchase_price.value) : null,
      owners: this.html_owners ? Array.from(this.html_owners.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value) : [],
      tags: this.html_tags ? Array.from(this.html_tags.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value) : []
    };

    // Emit different event based on mode
    if (this.add_mode === 'bulk') {
      // Bulk mode: add individual parts (no lot)
      this.socket.emit(this.messages.CREATE_BULK_INDIVIDUAL_PARTS, data);
    } else if (this.add_mode === 'lot') {
      // Lot mode: create lot with parts
      this.socket.emit(this.messages.CREATE_LOT, data);
    }
  }

  // Import CSV file and add parts to cart
  import_csv() {
    if (!this.html_csv_file || !this.html_csv_file.files || this.html_csv_file.files.length === 0) {
      this.fail({message: 'Please select a CSV file to import'});
      return;
    }

    const file = this.html_csv_file.files[0];
    const reader = new FileReader();

    reader.onload = ((bricksocket) => (e) => {
      try {
        const text = e.target.result;
        const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);

        if (lines.length === 0) {
          bricksocket.fail({message: 'CSV file is empty'});
          return;
        }

        // Parse CSV header
        const header = lines[0].split(',').map(h => h.trim());
        const partIndex = header.findIndex(h => h.toLowerCase() === 'part');
        const colorIndex = header.findIndex(h => h.toLowerCase() === 'color');
        const quantityIndex = header.findIndex(h => h.toLowerCase() === 'quantity');

        if (partIndex === -1 || colorIndex === -1 || quantityIndex === -1) {
          bricksocket.fail({message: 'CSV must have columns: Part, Color, Quantity'});
          return;
        }

        // Parse rows
        const parts = [];
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(',').map(v => v.trim());

          if (values.length < 3) continue; // Skip incomplete rows

          const part = values[partIndex];
          const color = parseInt(values[colorIndex]);
          const quantity = parseInt(values[quantityIndex]);

          if (part && !isNaN(color) && !isNaN(quantity) && quantity > 0) {
            parts.push({part, color, quantity});
          }
        }

        if (parts.length === 0) {
          bricksocket.fail({message: 'No valid parts found in CSV file'});
          return;
        }

        // Enable lot mode if not already in bulk/lot mode
        if (bricksocket.add_mode === 'single') {
          if (bricksocket.html_lot_mode) {
            bricksocket.html_lot_mode.checked = true;
            bricksocket.update_add_mode('lot');
          }
        }

        // Clear previous status and progress
        bricksocket.clear_status();
        bricksocket.progress_message(`Importing ${parts.length} parts from CSV...`);

        // Process each part
        bricksocket.import_csv_parts(parts, 0);

      } catch (error) {
        bricksocket.fail({message: `Error parsing CSV: ${error.message}`});
      }
    })(this);

    reader.onerror = ((bricksocket) => () => {
      bricksocket.fail({message: 'Error reading CSV file'});
    })(this);

    reader.readAsText(file);
  }

  // Import CSV parts one by one
  import_csv_parts(parts, index) {
    if (index >= parts.length) {
      // All parts processed - clear CSV import state
      this.csv_import_parts = null;
      this.csv_import_index = undefined;

      // Final cart render
      this.render_cart();

      // Show metadata section
      if (this.html_metadata_section) {
        this.html_metadata_section.classList.remove('d-none');
      }

      // Set progress bar to 100%
      if (this.html_progress_bar) {
        this.html_progress.setAttribute('aria-valuenow', '100');
        this.html_progress_bar.setAttribute('style', 'width: 100%');
        this.html_progress_bar.textContent = '100%';
      }

      // Show success message
      this.clear_status();
      this.spinner(false);
      this.toggle(true);

      const successDiv = document.getElementById('add-part-complete');
      if (successDiv) {
        successDiv.textContent = `Successfully imported ${parts.length} parts to cart! You can now apply metadata and click "Complete Lot & Add All Parts".`;
        successDiv.classList.remove('d-none');
      }

      // Clear the file input
      if (this.html_csv_file) {
        this.html_csv_file.value = '';
      }
      if (this.html_import_csv) {
        this.html_import_csv.disabled = true;
      }

      return;
    }

    const part = parts[index];

    // Fetch colors for this part (backend will handle image downloads)
    this.socket.emit(this.messages.LOAD_PART_COLORS, {part: part.part});

    // Store CSV import state
    this.csv_import_parts = parts;
    this.csv_import_index = index;
  }

  // Override part_colors_loaded to handle CSV import
  part_colors_loaded(data) {
    // Check if we're in CSV import mode
    if (this.csv_import_parts && this.csv_import_index !== undefined) {
      const parts = this.csv_import_parts;
      const index = this.csv_import_index;
      const part = parts[index];

      // Find the color in the loaded colors
      const color = data.colors.find(c => c.color_id === part.color);

      if (color) {
        // Add to cart (silently, without rendering each time for performance)
        const cart_item = {
          part: data.part,
          part_name: data.part_name,
          color_id: color.color_id,
          color_name: color.color_name,
          quantity: part.quantity,
          color_info: color
        };

        this.cart.push(cart_item);

        // Only render cart at the end or every 5 parts for performance
        if ((index + 1) % 5 === 0 || (index + 1) === parts.length) {
          this.render_cart();
        }

        // Update progress bar manually
        const progress = ((index + 1) / parts.length) * 100;
        if (this.html_progress_bar) {
          this.html_progress.setAttribute('aria-valuenow', progress);
          this.html_progress_bar.setAttribute('style', `width: ${progress}%`);
          this.html_progress_bar.textContent = `${progress.toFixed(0)}%`;
        }

        // Update simple status without showing the backend progress
        this.clear_status();
        this.progress_message(`Added ${index + 1}/${parts.length} parts to cart`);

        // Process next part
        this.import_csv_parts(parts, index + 1);
      } else {
        this.fail({message: `Color ${part.color} not found for part ${part.part}. Import stopped at part ${index + 1}/${parts.length}.`});
        this.csv_import_parts = null;
        this.csv_import_index = undefined;
      }

      return;
    }

    // Normal part colors loaded flow
    console.log('Received part colors:', data);

    this.current_part = data.part;
    this.current_part_name = data.part_name;
    this.current_colors = data.colors;

    // Show the colors section
    if (this.html_colors_section) {
      this.html_colors_section.classList.remove("d-none");
    }

    // Render color cards
    if (this.html_colors_grid && this.current_colors) {
      this.html_colors_grid.innerHTML = '';

      this.current_colors.forEach((color) => {
        const card = this.create_color_card(color);
        this.html_colors_grid.appendChild(card);
      });
    }

    // Show metadata section
    if (this.html_metadata_section) {
      this.html_metadata_section.classList.remove("d-none");
    }

    // Set progress bar to 100% for single part lookup
    if (this.html_progress_bar) {
      this.html_progress.setAttribute('aria-valuenow', '100');
      this.html_progress_bar.setAttribute('style', 'width: 100%');
      this.html_progress_bar.textContent = '100%';
    }

    this.spinner(false);
    this.toggle(true);
    this.progress_message(`Found ${data.count} colors for ${this.current_part_name} (${this.current_part})`);
  }

  // Override progress to suppress backend progress updates during CSV import
  progress(data={}) {
    // Ignore backend progress updates when importing CSV
    if (this.csv_import_parts && this.csv_import_index !== undefined) {
      return;
    }

    // Otherwise, use the default progress behavior
    super.progress(data);
  }

  // Setup socket listeners
  setup() {
    super.setup();

    if (this.socket) {
      // Listen for part colors loaded
      this.socket.on(this.messages.PART_COLORS_LOADED, ((bricksocket) => (data) => {
        bricksocket.part_colors_loaded(data);
      })(this));
    }
  }

  // Override complete to clear the form but keep success message
  complete(data) {
    // Custom success display with green alert box
    if (this.html_progress_bar) {
      this.html_progress.setAttribute("aria-valuenow", "100");
      this.html_progress_bar.setAttribute("style", "width: 100%");
      this.html_progress_bar.textContent = "100%";
    }

    this.spinner(false);

    // Show success message in green alert box
    if (this.html_complete) {
      this.html_complete.classList.remove("d-none");
      this.html_complete.innerHTML = `<strong>Success:</strong> ${data.message}`;
    }

    if (this.html_fail) {
      this.html_fail.classList.add("d-none");
    }

    // If lot was created, clear the cart (but don't clear status message)
    if (data && (data.lot_id || data.parts_added)) {
      // Clear cart without clearing status
      this.cart = [];
      this.render_cart();

      // Reset to single mode after successful add
      if (this.html_single_mode) {
        this.html_single_mode.checked = true;
        // Don't call update_add_mode('single') as it would call clear_cart() again
        // Just update the mode and hide cart section manually
        this.add_mode = 'single';
        if (this.html_cart_section) {
          this.html_cart_section.classList.add("d-none");
        }
      }
    }

    // Clear the form after successful add (but don't call this.clear() as it clears status)
    if (this.html_input) {
      this.html_input.value = '';
    }

    // Hide color selection section without clearing status
    if (this.html_colors_section) {
      this.html_colors_section.classList.add("d-none");
    }

    if (this.html_colors_grid) {
      this.html_colors_grid.innerHTML = '';
    }

    if (this.html_metadata_section) {
      this.html_metadata_section.classList.add("d-none");
    }

    // Clear state
    this.current_part = null;
    this.current_part_name = null;
    this.current_colors = null;
    this.selected_color = null;

    // Uncheck all metadata
    if (this.html_owners) {
      this.html_owners.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    }
    if (this.html_tags) {
      this.html_tags.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    }
    if (this.html_storage) {
      this.html_storage.value = '';
    }
    if (this.html_purchase_location) {
      this.html_purchase_location.value = '';
    }
    if (this.html_purchase_date) {
      this.html_purchase_date.value = '';
    }
    if (this.html_purchase_price) {
      this.html_purchase_price.value = '';
    }
  }
}
