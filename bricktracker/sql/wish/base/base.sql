SELECT
    "bricktracker_wishes"."set",
    "bricktracker_wishes"."name",
    "bricktracker_wishes"."year",
    "bricktracker_wishes"."theme_id",
    "bricktracker_wishes"."number_of_parts",
    "bricktracker_wishes"."image",
    "bricktracker_wishes"."url"
FROM "bricktracker_wishes"

{% block where %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}
