BEGIN TRANSACTION;

-- Add owner column to set_owners table (used by all entities: sets, individual parts, individual minifigures, individual part lots)
ALTER TABLE "bricktracker_set_owners"
ADD COLUMN "owner_{{ id }}" BOOLEAN NOT NULL DEFAULT 0;

-- Also inject into wishes (wishes use their own table)
ALTER TABLE "bricktracker_wish_owners"
ADD COLUMN "owner_{{ id }}" BOOLEAN NOT NULL DEFAULT 0;

INSERT INTO "bricktracker_metadata_owners" (
    "id",
    "name"
) VALUES (
    '{{ id }}',
    '{{ name }}'
);

COMMIT;