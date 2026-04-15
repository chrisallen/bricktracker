-- Update individual part lot name
UPDATE "bricktracker_individual_part_lots"
SET "name" = :name
WHERE "id" = :id
