BEGIN TRANSACTION;

INSERT INTO "bricktracker_metadata_storages" (
    "id",
    "name"
) VALUES (
    '{{ id }}',
    '{{ name }}'
);

COMMIT;