-- Update quantity for an individual part
UPDATE "bricktracker_individual_parts"
SET "quantity" = :quantity
WHERE "id" = :id;
