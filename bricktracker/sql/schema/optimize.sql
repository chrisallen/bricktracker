-- Optimize database performance
-- Re-applies performance indexes and runs database maintenance

CREATE INDEX IF NOT EXISTS idx_bricktracker_parts_id_missing_damaged
ON bricktracker_parts(id, missing, damaged);

CREATE INDEX IF NOT EXISTS idx_bricktracker_parts_part_color_spare
ON bricktracker_parts(part, color, spare);

CREATE INDEX IF NOT EXISTS idx_bricktracker_sets_set_storage
ON bricktracker_sets("set", storage);

CREATE INDEX IF NOT EXISTS idx_rebrickable_sets_name_lower
ON rebrickable_sets(LOWER(name));

CREATE INDEX IF NOT EXISTS idx_rebrickable_parts_name_lower
ON rebrickable_parts(LOWER(name));

CREATE INDEX IF NOT EXISTS idx_bricktracker_sets_purchase_location
ON bricktracker_sets(purchase_location);

CREATE INDEX IF NOT EXISTS idx_bricktracker_parts_quantity
ON bricktracker_parts(quantity);

CREATE INDEX IF NOT EXISTS idx_rebrickable_sets_year
ON rebrickable_sets(year);

CREATE INDEX IF NOT EXISTS idx_rebrickable_sets_theme_id
ON rebrickable_sets(theme_id);

CREATE INDEX IF NOT EXISTS idx_rebrickable_sets_number_version
ON rebrickable_sets(number, version);

CREATE INDEX IF NOT EXISTS idx_bricktracker_sets_purchase_date
ON bricktracker_sets(purchase_date);

ANALYZE;

PRAGMA optimize;
