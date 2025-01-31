BEGIN TRANSACTION;

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