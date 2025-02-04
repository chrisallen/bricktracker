BEGIN TRANSACTION;

INSERT INTO "bricktracker_metadata_purchase_locations" (
    "id",
    "name"
) VALUES (
    '{{ id }}',
    '{{ name }}'
);

COMMIT;