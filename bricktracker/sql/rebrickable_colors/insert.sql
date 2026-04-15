-- Insert or replace color information
INSERT OR REPLACE INTO "rebrickable_colors" (
    "color_id", "name", "rgb", "is_trans",
    "bricklink_color_id", "bricklink_color_name"
) VALUES (
    :color_id, :name, :rgb, :is_trans,
    :bricklink_color_id, :bricklink_color_name
)
