BEGIN TRANSACTION;

-- Add status column to set_statuses table (used by all entities: sets, individual parts, individual minifigures)
-- Note: Individual part lots don't have statuses
ALTER TABLE "bricktracker_set_statuses"
ADD COLUMN "status_{{ id }}" BOOLEAN NOT NULL DEFAULT 0;

INSERT INTO "bricktracker_metadata_statuses" (
    "id",
    "name",
    "displayed_on_grid"
) VALUES (
    '{{ id }}',
    '{{ name }}',
    {{ displayed_on_grid }}
);

COMMIT;