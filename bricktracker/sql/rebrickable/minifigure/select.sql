SELECT
    "rebrickable_minifigures"."figure",
    "rebrickable_minifigures"."number",
    "rebrickable_minifigures"."name",
    "rebrickable_minifigures"."image"
FROM "rebrickable_minifigures"

WHERE "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM :figure
