BEGIN transaction;

DROP TABLE IF EXISTS "bricktracker_metadata_owners";
DROP TABLE IF EXISTS "bricktracker_metadata_statuses";
DROP TABLE IF EXISTS "bricktracker_metadata_tags";
DROP TABLE IF EXISTS "bricktracker_minifigures";
DROP TABLE IF EXISTS "bricktracker_parts";
DROP TABLE IF EXISTS "bricktracker_sets";
DROP TABLE IF EXISTS "bricktracker_set_checkboxes";
DROP TABLE IF EXISTS "bricktracker_set_owners";
DROP TABLE IF EXISTS "bricktracker_set_statuses";
DROP TABLE IF EXISTS "bricktracker_set_storages";
DROP TABLE IF EXISTS "bricktracker_set_tags";
DROP TABLE IF EXISTS "bricktracker_wishes";
DROP TABLE IF EXISTS "inventory";
DROP TABLE IF EXISTS "inventory_old";
DROP TABLE IF EXISTS "minifigures";
DROP TABLE IF EXISTS "minifigures_old";
DROP TABLE IF EXISTS "missing";
DROP TABLE IF EXISTS "missing_old";
DROP TABLE IF EXISTS "rebrickable_minifigures";
DROP TABLE IF EXISTS "rebrickable_parts";
DROP TABLE IF EXISTS "rebrickable_sets";
DROP TABLE IF EXISTS "sets";
DROP TABLE IF EXISTS "sets_old";
DROP TABLE IF EXISTS "wishlist";
DROP TABLE IF EXISTS "wishlist_old";

COMMIT;

PRAGMA user_version = 0;