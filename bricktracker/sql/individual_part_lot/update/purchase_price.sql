-- Update individual part lot purchase price
UPDATE "bricktracker_individual_part_lots"
SET "purchase_price" = :purchase_price
WHERE "id" = :id
