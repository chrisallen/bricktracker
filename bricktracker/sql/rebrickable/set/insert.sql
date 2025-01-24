INSERT OR IGNORE INTO "rebrickable_sets" (
    "set",
    "number",
    "version",
    "name",
    "year",
    "theme_id",
    "number_of_parts",
    "image",
    "url",
    "last_modified"
) VALUES (
    :set,
    :number,
    :version,
    :name,
    :year,
    :theme_id,
    :number_of_parts,
    :image,
    :url,
    :last_modified
)
