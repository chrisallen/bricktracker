UPDATE "sets"
SET "{{name}}" = :status
WHERE "sets"."u_id" IS NOT DISTINCT FROM :u_id
