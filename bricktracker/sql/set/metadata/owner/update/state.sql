INSERT INTO "bricktracker_set_owners" (
    "id",
    "{{name}}"
) VALUES (
    :set_id,
    :state
)
ON CONFLICT("id")
DO UPDATE SET "{{name}}" = :state
WHERE "bricktracker_set_owners"."id" IS NOT DISTINCT FROM :set_id
