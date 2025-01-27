INSERT INTO "bricktracker_set_statuses" (
    "id",
    "{{name}}"
) VALUES (
    :id,
    :status
)
ON CONFLICT("id")
DO UPDATE SET "{{name}}" = :status
WHERE "bricktracker_set_statuses"."id" IS NOT DISTINCT FROM :id
