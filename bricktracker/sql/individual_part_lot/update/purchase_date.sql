-- Update individual part lot purchase date
UPDATE "bricktracker_individual_part_lots"
SET "purchase_date" = :purchase_date
WHERE "id" = :id
