BEGIN transaction;

-- Disable foreign key checks during drop to avoid constraint errors
PRAGMA foreign_keys = OFF;

-- Drop child tables first (those with foreign key references)

-- Individual minifigure parts (references individual_minifigures)
DROP TABLE IF EXISTS "bricktracker_individual_minifigure_parts";

-- Individual parts (references individual_part_lots)
-- Drop before lots since lot_id is a foreign key
DROP TABLE IF EXISTS "bricktracker_individual_parts";

-- Individual minifigures (references rebrickable_minifigures, metadata tables)
DROP TABLE IF EXISTS "bricktracker_individual_minifigures";

-- Individual part lots (references metadata tables)
DROP TABLE IF EXISTS "bricktracker_individual_part_lots";

-- Set-based parts and minifigures (references sets)
DROP TABLE IF EXISTS "bricktracker_minifigures";
DROP TABLE IF EXISTS "bricktracker_parts";

-- Set metadata junction tables (reference sets and metadata)
DROP TABLE IF EXISTS "bricktracker_set_checkboxes";
DROP TABLE IF EXISTS "bricktracker_set_owners";
DROP TABLE IF EXISTS "bricktracker_set_statuses";
DROP TABLE IF EXISTS "bricktracker_set_storages";
DROP TABLE IF EXISTS "bricktracker_set_tags";

-- Wish metadata junction tables
DROP TABLE IF EXISTS "bricktracker_wish_owners";

-- Main sets and wishes tables
DROP TABLE IF EXISTS "bricktracker_sets";
DROP TABLE IF EXISTS "bricktracker_wishes";

-- Metadata definition tables
DROP TABLE IF EXISTS "bricktracker_metadata_owners";
DROP TABLE IF EXISTS "bricktracker_metadata_statuses";
DROP TABLE IF EXISTS "bricktracker_metadata_tags";
DROP TABLE IF EXISTS "bricktracker_metadata_storages";
DROP TABLE IF EXISTS "bricktracker_metadata_purchase_locations";

-- Rebrickable reference tables
DROP TABLE IF EXISTS "rebrickable_colors";
DROP TABLE IF EXISTS "rebrickable_minifigures";
DROP TABLE IF EXISTS "rebrickable_parts";
DROP TABLE IF EXISTS "rebrickable_sets";
DROP TABLE IF EXISTS "rebrickable_sets_new";

-- Legacy/migration tables
DROP TABLE IF EXISTS "inventory";
DROP TABLE IF EXISTS "inventory_old";
DROP TABLE IF EXISTS "minifigures";
DROP TABLE IF EXISTS "minifigures_old";
DROP TABLE IF EXISTS "missing";
DROP TABLE IF EXISTS "missing_old";
DROP TABLE IF EXISTS "sets";
DROP TABLE IF EXISTS "sets_old";
DROP TABLE IF EXISTS "wishlist";
DROP TABLE IF EXISTS "wishlist_old";

-- Re-enable foreign key checks
PRAGMA foreign_keys = ON;

COMMIT;

PRAGMA user_version = 0;