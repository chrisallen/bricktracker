UPDATE "missing"
SET "quantity" = :quantity
WHERE "missing"."set_num" IS NOT DISTINCT FROM :set_num
AND "missing"."id" IS NOT DISTINCT FROM :id
AND "missing"."u_id" IS NOT DISTINCT FROM :u_id
