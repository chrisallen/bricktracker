{% extends 'set/base/select.sql' %}

{% block where %}
WHERE sets.u_id IN (
    SELECT
        missing.u_id
    FROM missing

    WHERE missing.set_num IS NOT DISTINCT FROM :fig_num

    GROUP BY missing.u_id
)
{% endblock %}
