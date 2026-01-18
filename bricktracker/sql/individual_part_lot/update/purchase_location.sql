-- Update individual part lot purchase location
UPDATE "bricktracker_individual_part_lots"
SET "purchase_location" = :purchase_location
WHERE "id" = :id
