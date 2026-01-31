-- Count how many items are using this storage location
SELECT
    (SELECT COUNT(*) FROM bricktracker_sets WHERE storage = :id) as sets_count,
    (SELECT COUNT(*) FROM bricktracker_individual_minifigures WHERE storage = :id) as minifigures_count,
    (SELECT COUNT(*) FROM bricktracker_individual_parts WHERE storage = :id) as parts_count,
    (SELECT COUNT(*) FROM bricktracker_individual_part_lots WHERE storage = :id) as lots_count
