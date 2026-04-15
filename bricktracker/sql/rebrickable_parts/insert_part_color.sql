-- Insert a part/color combination into rebrickable_parts
INSERT OR IGNORE INTO "rebrickable_parts" (
    "part",
    "name",
    "color_id",
    "color_name",
    "color_rgb",
    "color_transparent",
    "image",
    "image_id",
    "url",
    "bricklink_color_id",
    "bricklink_color_name"
) VALUES (
    :part,
    :name,
    :color_id,
    :color_name,
    :color_rgb,
    :color_transparent,
    :image,
    :image_id,
    :url,
    :bricklink_color_id,
    :bricklink_color_name
)
