SELECT
    "wishlist"."set_num",
    "wishlist"."name",
    "wishlist"."year",
    "wishlist"."theme_id",
    "wishlist"."num_parts",
    "wishlist"."set_img_url",
    "wishlist"."set_url",
    "wishlist"."last_modified_dt"
FROM "wishlist"

{% block where %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}
