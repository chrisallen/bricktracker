INSERT OR IGNORE INTO "rebrickable_parts" (
    "part",
    "color_id",
    "color_name",
    "color_rgb",
    "color_transparent",
    "name",
    "category",
    "image",
    "image_id",
    "url",
    "print"
) VALUES (
    :part,
    :color_id,
    :color_name,
    :color_rgb,
    :color_transparent,
    :name,
    :category,
    :image,
    :image_id,
    :url,
    :print
)
ON CONFLICT("part", "color_id")
DO UPDATE SET
"color_name" = :color_name,
"color_rgb" = :color_rgb,
"color_transparent" = :color_transparent,
"name" = :name,
"category" = :category,
"image" = :image,
"image_id" = :image_id,
"url" = :url,
"print" = :print
WHERE "rebrickable_parts"."part" IS NOT DISTINCT FROM :part
AND "rebrickable_parts"."color_id" IS NOT DISTINCT FROM :color_id