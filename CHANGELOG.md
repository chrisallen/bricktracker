# Changelog

## Unreleased

- Fix legibility of "Damaged" and "Missing" fields for tiny screen by reducing horizontal padding

## 1.2.2:

This release fixes a bug where orphaned parts in the `inventory` table are blocking the database upgrade.

## 1.2.1:

This release fixes a bug where you could not add a set if no metadata was configured.

## 1.2.0:

> **Warning**
> "Missing" part has been renamed to "Problems" to accomodate for missing and damaged parts.
> The associated environment variables have changed named (the old names are still valid)

### Environment

- Renamed: `BK_HIDE_MISSING_PARTS` -> `BK_HIDE_ALL_PROBLEMS_PARTS`
- Added: `BK_HIDE_TABLE_MISSING_PARTS`, hide the Missing column in all tables
- Added: `BK_HIDE_TABLE_DAMAGED_PARTS`, hide the Damaged column in all tables
- Added: `BK_SHOW_GRID_SORT`, show the sort options on the grid by default
- Added: `BK_SHOW_GRID_FILTERS`, show the filter options on the grid by default
- Added: `BK_HIDE_ALL_STORAGES`, hide the "Storages" menu entry
- Added: `BK_STORAGE_DEFAULT_ORDER`, ordering of storages
- Added: `BK_PURCHASE_LOCATION_DEFAULT_ORDER`, ordering of purchase locations
- Added: `BK_PURCHASE_CURRENCY`, currency to display for purchase prices
- Added: `BK_PURCHASE_DATE_FORMAT`, date format for purchase dates
- Documented: `BK_FILE_DATETIME_FORMAT`, date format for files on disk (instructions, theme)

### Code

- Changer
    - Revert the checked state of a checkbox if an error occured

- Form
    - Migrate missing input fields to BrickChanger

- General cleanup

- Metadata
    - Underlying class to implement more metadata-like features

- Minifigure
    - Deduplicate
    - Compute number of parts

- Parts
    - Damaged parts

- Sets
    - Refresh data from Rebrickable
    - Fix missing @login_required for set deletion
    - Ownership
    - Tags
    - Storage
    - Purchase location, date, price

- Storage
    - Storage content and list

- Socket
    - Add decorator for rebrickable, authenticated and threaded socket actions

- SQL
    - Allow for advanced migration scenarios through companion python files
    - Add a bunch of the requested fields into the database for future implementation

- Wish
    - Requester

### UI

- Add
    - Allow adding or bulk adding by pressing Enter in the input field

- Admin
    - Grey out legacy tables in the database view
    - Checkboxes renamed to Set statuses
    - List of sets that may need to be refreshed

- Cards
    - Use macros for badge in the card header

- Form
    - Add a clear button for dynamic text inputs
    - Add error message in a tooltip for dynamic inputs

- Minifigure
    - Display number of parts

- Parts
    - Use Rebrickable URL if stored (+ color code)
    - Display color and transparency
    - Display if print of another part
    - Display prints using the same base
    - Damaged parts
    - Display same parts using a different color

- Sets
    - Add a flag to hide instructions in a set
    - Make checkbox clickable on the whole width of the card
    - Management
        - Ownership
        - Tags
        - Refresh
        - Storage
        - Purchase location, date, price

- Sets grid
    - Collapsible controls depending on screen size
    - Manually collapsible filters (with configuration variable for default state)
    - Manually collapsible sort (with configuration variable for default state)
    - Clear search bar

- Storage
    - Storage list
    - Storage content

- Wish
    - Requester

## 1.1.1: PDF Instructions Download

### Instructions

- Added buttons for instructions download from Rebrickable


## 1.1.0: Deduped sets, custom checkboxes and database upgrade

### Database

- Sets
    - Deduplicating rebrickable sets (unique) and bricktracker sets (can be n bricktracker sets for one rebrickable set)

### Docs

- Removed extra `<br>` to accomodate Gitea Markdown
- Add an organized DOCS.md documentation page
- Database upgrade/migration
- Checkboxes

### Code

- Admin
    - Split the views before admin because an unmanageable monster view

- Checkboxes
    - Customizable checkboxes for set (amount and names, displayed on the grid or not)
    - Replaced the 3 original routes to update the status with a generic route to accomodate any custom status

- Instructions
    - Base instructions on RebrickableSet (the generic one) rather than BrickSet (the specific one)
    - Refine set number detection in file name by making sure each first items is an integer

- Python
    - Make stricter function definition with no "arg_or_keyword" parameters

- Records
    - Consolidate the select() -> not None or Exception -> ingest() process duplicated in every child class

- SQL
    - Forward-only migration mechanism
    - Check for database too far in version
    - Inject the database version in the file when downloading it
    - Quote all indentifiers as best practice
    - Allow insert query to be overriden
    - Allow insert query to force not being deferred even if not committed
    - Allow select query to push context in BrickRecord and BrickRecordList
    - Make SQL record counters failsafe as they are used in the admin and it should always work
    - Remove BrickSQL.initialize() as it is replaced by upgrade()

- Sets
    - Now that it is deduplicated, adding the same set more than once will not pull it fully from the Rebrickable API (minifigures and parts)
    - Make RebrickableSet extend BrickRecord since it is now an item in database
    - Make BrickSet extend RebrickableSet now that RebrickableSet is a proper database item

### UI

- Checkboxes
    - Possibility to hide the checkbox in the grid ("Sets") but sill have all them in the set details
    - Management

- Database
    - Migration tool

- Javascript
    - Generic BrickChanger class to handle quick modification through a JSON request with a visual feedback indicator
    - Simplify the way javascript scripts are loaded and instantiated

- Set grid
    - Filter by checkboxes and NOT checkboxes

- Tables
    - Fix table search looking inside links pills

- Wishlist
    - Add Rebrickable link badge for sets (@matthew)

## 1.0.0: New Year revamp

### Code

- Authentication
    - Basic authentication mechanism with ONE password to protect admin and writes
- CSV
    - Remove dependencies to numpy and panda for simpler built-in csv
- Code
    - Refactored the Python code
    - Modularity (more functions, splitting files)
    - Type hinting whenever possible
    - Flake8 linter
    - Retained most of the original behaviour (with its quirks)
- Colors
    - Remove dependency on color.csv
- Configuration
    - Moved all the hard-coded parameters into configuration variables
    - Most of the variables are configuration through environment variables
    - Force instruction, sets, etc path to be relative to static
- Docker
    - Added an entrypoint to grab PORT / HOST from the environment if set
    - Remove the need to seed the container with files (*.csv, nil files)
- Flask
    - Fix improper socketio.run(app.run()) call which lead to hard crash on ^C
    - Make use of url_for to create URLs
    - Use blueprints to implement routes
    - Move views into their own files
    - Split GET and POST methods into two different routes for clarity
- Images
    - Add an option to use remote images from the Rebrickable CDN rather than downloading everything locally
    - Handle nil.png and nil_mf.jpg as true images in /static/sets/ so that they are downloaded whenever necessary when importing a se with missing images
- Instructions
    - Scan the files once for the whole app, and re-use the data
    - Refresh the instructions from the admin
    - More lenient set number detection
    - Update when uploading a new one
    - Basic file management
- Logs
    - Added log lines for change actions (add, check, missing, delete) so that the server is not silent when DEBUG=false
- Minifigures
    - Added a variable to control default ordering
- Part(s)
    - Added a variable to control default ordering of listing
- Retired sets
    - Open the themes once for the whole app, and re-use the data
    - Do not hard fail if themes.csv is missing, simply display the IDs
    - Light management: resync, download
- Set(s)
    - Reworked the set checkboxes with a dedicated route per status
    - Switch from homemade ID generator to proven UUID4 for sets ID
        - Does not interfere with previously created sets
    - Do not rely on sets.csv to check if the set exists
    - When adding, commit the set to database only once everything has been processed
    - Added a bulk add page
    - Keep spare parts when importing
    - Added a variable to control default ordering of listing
- Socket
    - Make use of socket.io rooms to avoid broadcasting messages to all clients
- SQLite
    - Do not hard fail if the database is not present or not initialized
    - Open the database once for the context, and re-use the connection
    - Move queries to .sql files and load them as Jinja templates
    - Use named arguments rather than sets for SQLite queries
    - Allow execute() to be deferred to the commit() call to avoid locking the database for long period while importing (locked while downloading images)
- Themes
    - Open the themes once for the whole app, and re-use the data
    - Do not hard fail if themes.csv is missing, simply display the IDs
    - Light management: resync, download

### UI

- Admin
    - Initialize the database from the web interface
    - Reset the database
    - Delete the database
    - Download the database
    - Import the database
    - Display the configuration variables
    - Many things
- Accordions
    - Added a flag to make the accordion items independent
- Branding:
    - Add a brick as a logo (CC0 image from: https://iconduck.com/icons/71631/brick)
- Global
    - Redesign of the whole app
    - Sticky menu bar on top of the page
    - Execution time and SQL stats for fun
- Libraries
    - Switch from Bulma to Bootstrap, arbitrarily :D
    - Use of baguettebox for images (https://github.com/feimosi/baguetteBox.js)
    - Use of tinysort to sort and filter the grid (https://github.com/Sjeiti/TinySort)
    - Use of sortable for set card tables (https://github.com/tofsjonas/sortable)
    - Use of simple-datatables for big tables (https://github.com/fiduswriter/simple-datatables)
- Minifigures
    - Added a detail view for a minifigure
    - Display which sets are using a minifigure
    - Display which sets are missing a minifigure
- Parts
    - Added a detail view for a part
    - Display which sets are using a part
    - Display which sets are missing a part
- Templates
    - Use a common base template
    - Use HTML fragments/macros for repeted or parametrics items
    - a 404 page for wrong URLs
    - an error page for expected error messages
    - an exception page for unexpected error messages
- Set add
    - Two-tiered (with override) import where you see what you will import before importing it
    - Add a visual indicator that the socket is connected
- Set card
    - Badges to display info like theme, year, parts, etc
    - Set image on top of the card, filling the space
    - Trick to have a blurry background image fill the void in the card
    - Save missing parts on input change rather than by clicking
        - Visual feedback of success
    - Parts and minifigure in accordions
    - Instructions file list
- Set grid
    - 4-2-1 card distribution depending on screen size
    - Display the index with no set added, rather than redirecting
    - Keep last sort in a cookie, and trigger it on page load (can be cleared)
