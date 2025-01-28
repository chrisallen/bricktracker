SELECT
    "rebrickable_parts"."part",
    "rebrickable_parts"."color_id",
    "rebrickable_parts"."color_name",
    "rebrickable_parts"."color_rgb",
    "rebrickable_parts"."color_transparent",
    "rebrickable_parts"."name",
    "rebrickable_parts"."category",
    "rebrickable_parts"."image",
    "rebrickable_parts"."image_id",
    "rebrickable_parts"."url",
    "rebrickable_parts"."print"
FROM "rebrickable_parts"

WHERE "rebrickable_minifigures"."part" IS NOT DISTINCT FROM :figure
AND "rebrickable_minifigures"."color_id" IS NOT DISTINCT FROM :color
