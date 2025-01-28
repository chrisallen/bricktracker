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
