-- Select color information by color_id
SELECT "color_id", "name", "rgb", "is_trans",
       "bricklink_color_id", "bricklink_color_name"
FROM "rebrickable_colors"
WHERE "color_id" = :color_id
