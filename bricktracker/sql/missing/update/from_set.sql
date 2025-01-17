UPDATE missing
SET quantity = :quantity
WHERE set_num IS NOT DISTINCT FROM :set_num
AND id IS NOT DISTINCT FROM :id
AND u_id IS NOT DISTINCT FROM :u_id
