BEGIN TRANSACTION;

-- Add the value column for this custom field (per-set TEXT value).
ALTER TABLE "bricktracker_set_custom_fields"
ADD COLUMN "custom_field_{{ id }}" TEXT;

INSERT INTO "bricktracker_metadata_custom_fields" (
    "id",
    "name",
    "type"
) VALUES (
    '{{ id }}',
    '{{ name }}',
    '{{ type }}'
);

COMMIT;
