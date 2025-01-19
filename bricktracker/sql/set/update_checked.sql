UPDATE sets
SET {{name}} = :status
WHERE u_id IS NOT DISTINCT FROM :u_id
