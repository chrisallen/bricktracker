-- Get distinct storages from problem parts' sets
SELECT DISTINCT
    "bricktracker_sets"."storage" AS "storage_id",
    "bricktracker_metadata_storages"."name" AS "storage_name",
    COUNT(DISTINCT "bricktracker_parts"."part") as "part_count"
FROM "bricktracker_parts"
INNER JOIN "bricktracker_sets"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_sets"."id"
LEFT JOIN "bricktracker_metadata_storages"
ON "bricktracker_sets"."storage" IS NOT DISTINCT FROM "bricktracker_metadata_storages"."id"
{% if owner_id and owner_id != 'all' %}
INNER JOIN "bricktracker_set_owners"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"
{% endif %}
WHERE ("bricktracker_parts"."missing" > 0 OR "bricktracker_parts"."damaged" > 0)
AND "bricktracker_sets"."storage" IS NOT NULL
{% if owner_id and owner_id != 'all' %}
AND "bricktracker_set_owners"."owner_{{ owner_id }}" = 1
{% endif %}
GROUP BY "bricktracker_sets"."storage", "bricktracker_metadata_storages"."name"
ORDER BY "bricktracker_metadata_storages"."name" ASC
