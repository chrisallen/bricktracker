BEGIN TRANSACTION;

ALTER TABLE "bricktracker_set_owners"
ADD COLUMN "owner_{{ id }}" BOOLEAN NOT NULL DEFAULT 0;

-- Also inject into wishes
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