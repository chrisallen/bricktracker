-- Update individual part lot storage
UPDATE "bricktracker_individual_part_lots"
SET "storage" = :storage
WHERE "id" = :id
