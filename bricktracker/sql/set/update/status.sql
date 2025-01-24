INSERT INTO "bricktracker_set_statuses" (
    "bricktracker_set_id",
    "{{name}}"
) VALUES (
    :id,
    :status
)
ON CONFLICT("bricktracker_set_id")
DO UPDATE SET "{{name}}" = :status
WHERE "bricktracker_set_statuses"."bricktracker_set_id" IS NOT DISTINCT FROM :id
