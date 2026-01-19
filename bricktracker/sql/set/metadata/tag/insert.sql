BEGIN TRANSACTION;

-- Add tag column to set_tags table (used by all entities: sets, individual parts, individual minifigures, individual part lots)
ALTER TABLE "bricktracker_set_tags"
ADD COLUMN "tag_{{ id }}" BOOLEAN NOT NULL DEFAULT 0;

INSERT INTO "bricktracker_metadata_tags" (
    "id",
    "name"
) VALUES (
    '{{ id }}',
    '{{ name }}'
);

COMMIT;