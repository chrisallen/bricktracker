-- Insert or update part into rebrickable_parts using pre-loaded color data
INSERT INTO "rebrickable_parts" (
    "part", "color_id", "color_name", "color_rgb", "color_transparent",
    "bricklink_color_id", "bricklink_color_name",
    "name", "image", "image_id", "url"
) VALUES (
    :part, :color_id, :color_name, :color_rgb, :color_transparent,
    :bricklink_color_id, :bricklink_color_name,
    :name, :image, :image_id, :url
)
ON CONFLICT("part", "color_id") DO UPDATE SET
    "color_name" = COALESCE(excluded."color_name", "rebrickable_parts"."color_name"),
    "color_rgb" = COALESCE(excluded."color_rgb", "rebrickable_parts"."color_rgb"),
    "color_transparent" = COALESCE(excluded."color_transparent", "rebrickable_parts"."color_transparent"),
    "bricklink_color_id" = COALESCE(excluded."bricklink_color_id", "rebrickable_parts"."bricklink_color_id"),
    "bricklink_color_name" = COALESCE(excluded."bricklink_color_name", "rebrickable_parts"."bricklink_color_name"),
    "name" = COALESCE(excluded."name", "rebrickable_parts"."name"),
    "image" = COALESCE(excluded."image", "rebrickable_parts"."image"),
    "image_id" = COALESCE(excluded."image_id", "rebrickable_parts"."image_id"),
    "url" = COALESCE(excluded."url", "rebrickable_parts"."url")
