SELECT
    sets.set_num,
    sets.name,
    sets.year,
    sets.theme_id,
    sets.num_parts,
    sets.set_img_url,
    sets.set_url
FROM sets

GROUP BY
    sets.set_num
