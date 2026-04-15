-- Delete parts that weren't in the refresh (orphaned parts)
-- Only delete if we actually tracked some parts (safety check)
DELETE FROM bricktracker_parts
WHERE id = :id
AND EXISTS (SELECT 1 FROM temp_refresh_parts WHERE id = :id)
AND NOT EXISTS (
    SELECT 1 FROM temp_refresh_parts
    WHERE temp_refresh_parts.id = bricktracker_parts.id
    AND temp_refresh_parts.part = bricktracker_parts.part
    AND temp_refresh_parts.color = bricktracker_parts.color
    AND (temp_refresh_parts.figure IS NULL AND bricktracker_parts.figure IS NULL
         OR temp_refresh_parts.figure = bricktracker_parts.figure)
    AND temp_refresh_parts.spare = bricktracker_parts.spare
)
