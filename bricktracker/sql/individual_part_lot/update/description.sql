-- Update individual part lot description
UPDATE "bricktracker_individual_part_lots"
SET "description" = :description
WHERE "id" = :id
