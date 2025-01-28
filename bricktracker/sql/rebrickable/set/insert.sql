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
ON CONFLICT("set")
DO UPDATE SET
    "number" = :number,
    "version" = :version,
    "name" = :name,
    "year" = :year,
    "theme_id" = :theme_id,
    "number_of_parts" = :number_of_parts,
    "image" = :image,
    "url" = :url,
    "last_modified" = :last_modified
WHERE "rebrickable_sets"."set" IS NOT DISTINCT FROM :set
