-- Update description for an individual part
UPDATE "bricktracker_individual_parts"
SET "description" = :description
WHERE "id" = :id;
