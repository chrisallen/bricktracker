-- Find orphaned sets (bricktracker_sets records without parent rebrickable_sets)

SELECT
    bs."set",
    bs.id,
    bs.description,
    bs.storage,
    bs.purchase_date,
    bs.purchase_location,
    bs.purchase_price
FROM bricktracker_sets bs
WHERE NOT EXISTS (
    SELECT 1 FROM rebrickable_sets rs WHERE rs."set" = bs."set"
)
ORDER BY bs."set";
