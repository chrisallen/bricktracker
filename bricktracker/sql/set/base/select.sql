SELECT
    sets.set_num,
    sets.name,
    sets.year,
    sets.theme_id,
    sets.num_parts,
    sets.set_img_url,
    sets.set_url,
    sets.last_modified_dt,
    sets.mini_col,
    sets.set_check,
    sets.set_col,
    sets.u_id,
    {% block number %}
    CAST(SUBSTR(sets.set_num, 1, INSTR(sets.set_num, '-') - 1) AS INTEGER) AS set_number,
    CAST(SUBSTR(sets.set_num, 1, INSTR(sets.set_num, '-') + 1) AS INTEGER) AS set_version,
    {% endblock %}
    IFNULL(missing_join.total, 0) AS total_missing,
    IFNULL(minifigures_join.total, 0) AS total_minifigures
FROM sets

-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        u_id,
        SUM(quantity) AS total
    FROM missing
    {% block where_missing %}{% endblock %}
    GROUP BY u_id
) missing_join
ON sets.u_id IS NOT DISTINCT FROM missing_join.u_id

-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        u_id,
       SUM(quantity) AS total
    FROM minifigures
    {% block where_minifigures %}{% endblock %}
    GROUP BY u_id
) minifigures_join
ON sets.u_id IS NOT DISTINCT FROM minifigures_join.u_id

{% block where %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}
