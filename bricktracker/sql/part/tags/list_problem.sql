-- Get list of all tags (simplified - filtering happens at application level)
-- Tags use dynamic columns in bricktracker_set_tags, making direct SQL filtering complex
SELECT
    "bricktracker_metadata_tags"."id" AS "tag_id",
    "bricktracker_metadata_tags"."name" AS "tag_name"
FROM "bricktracker_metadata_tags"
ORDER BY "bricktracker_metadata_tags"."name" ASC
