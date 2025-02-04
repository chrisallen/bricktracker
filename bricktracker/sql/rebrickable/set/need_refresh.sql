SELECT
    "rebrickable_sets"."set",
    "rebrickable_sets"."name",
    "rebrickable_sets"."number_of_parts",
    "rebrickable_sets"."image",
    "rebrickable_sets"."url",
    "null_join"."null_rgb",
    "null_join"."null_transparent",
    "null_join"."null_url"
FROM "rebrickable_sets"

INNER JOIN (
    SELECT
        "null_sums"."set",
        "null_sums"."null_rgb",
        "null_sums"."null_transparent",
        "null_sums"."null_url"
    FROM (
        SELECT
            "unique_set_parts"."set",
            SUM(CASE WHEN "unique_set_parts"."color_rgb" IS NULL THEN 1 ELSE 0 END) AS "null_rgb",
            SUM(CASE WHEN "unique_set_parts"."color_transparent" IS NULL THEN 1 ELSE 0 END) AS "null_transparent",
            SUM(CASE WHEN "unique_set_parts"."url" IS NULL THEN 1 ELSE 0 END) AS "null_url"
        FROM (
            SELECT
                "bricktracker_sets"."set",
                "rebrickable_parts"."color_rgb",
                "rebrickable_parts"."color_transparent",
                "rebrickable_parts"."url"
            FROM "bricktracker_sets"

            INNER JOIN "bricktracker_parts"
            ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_parts"."id"

            LEFT JOIN "rebrickable_parts"
            ON "bricktracker_parts"."part" IS NOT DISTINCT FROM "rebrickable_parts"."part"
            AND "bricktracker_parts"."color" IS NOT DISTINCT FROM "rebrickable_parts"."color_id"

            GROUP BY
                "bricktracker_sets"."set",
                "bricktracker_parts"."part",
                "bricktracker_parts"."color"
        ) "unique_set_parts"

        GROUP BY "unique_set_parts"."set"

    ) "null_sums"

    WHERE "null_rgb" > 0
    OR "null_transparent" > 0
    OR "null_url" > 0
) "null_join"
ON "rebrickable_sets"."set" IS NOT DISTINCT FROM "null_join"."set"
