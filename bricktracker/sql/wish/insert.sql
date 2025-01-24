INSERT OR IGNORE INTO "bricktracker_wishes" (
    "set",
    "name",
    "year",
    "theme_id",
    "number_of_parts",
    "image",
    "url"
) VALUES (
    :set,
    :name,
    :year,
    :theme_id,
    :number_of_parts,
    :image,
    :url
)
