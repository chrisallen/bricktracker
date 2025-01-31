INSERT INTO "bricktracker_set_tags" (
    "id",
    "{{name}}"
) VALUES (
    :set_id,
    :state
)
ON CONFLICT("id")
DO UPDATE SET "{{name}}" = :state
WHERE "bricktracker_set_tags"."id" IS NOT DISTINCT FROM :set_id
