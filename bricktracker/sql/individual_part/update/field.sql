-- Update a specific field in bricktracker_individual_parts
UPDATE "bricktracker_individual_parts"
SET "{{ field }}" = :value
WHERE "id" = :id
