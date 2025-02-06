INSERT INTO "bricktracker_wish_owners" (
    "set",
    "{{name}}"
) VALUES (
    :set,
    :state
)
ON CONFLICT("set")
DO UPDATE SET "{{name}}" = :state
WHERE "bricktracker_wish_owners"."set" IS NOT DISTINCT FROM :set
