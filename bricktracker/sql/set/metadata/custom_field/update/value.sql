INSERT INTO "bricktracker_set_custom_fields" (
    "id",
    "{{name}}"
) VALUES (
    :set_id,
    :value
)
ON CONFLICT("id")
DO UPDATE SET "{{name}}" = :value
WHERE "bricktracker_set_custom_fields"."id" IS NOT DISTINCT FROM :set_id
