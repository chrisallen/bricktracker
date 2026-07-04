from flask import Blueprint, Response, abort, request

from ..sidecar import BrickSidecar


# Proxies sidecar (BrickData) images through BrickTracker so the browser only
# ever talks to BrickTracker. This is what makes box art, the additional-images
# carousel and the cover previews work when the sidecar is only reachable on
# the internal Docker network (e.g. http://brickdata:3335), which the browser
# itself cannot resolve. Public (no login) because these images appear on pages
# anonymous users can already see.
sidecar_page = Blueprint('sidecar', __name__, url_prefix='/sidecar')


def _image_response(data: bytes | None, mimetype: str, /) -> Response:
    if data is None:
        abort(404)

    response = Response(data, mimetype=mimetype)
    # Cache in the browser so viewing a set does not re-proxy every image.
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response


# Box / set art (BrickLink image proxy), e.g. /sidecar/image/box/8250-1.png
@sidecar_page.route('/image/<image_type>/<ref>.png', methods=['GET'])
def image(*, image_type: str, ref: str) -> Response:
    if not BrickSidecar.enabled():
        abort(404)

    return _image_response(
        BrickSidecar.fetch_image_bytes(image_type, ref), 'image/png',
    )


# One Brickset additional image, e.g. /sidecar/additional-images/8250-1/0.
# Path kept plural ("additional-images") so it matches the BaguetteBox gallery
# filter in base.html, which keys on that string for extensionless image URLs.
@sidecar_page.route(
    '/additional-images/<ref>/<int:index>', methods=['GET'],
)
def additional_image(*, ref: str, index: int) -> Response:
    if not BrickSidecar.enabled():
        abort(404)

    thumbnail = request.args.get('thumbnail') is not None

    return _image_response(
        BrickSidecar.fetch_additional_image_bytes(
            ref, index, thumbnail=thumbnail,
        ),
        'image/jpeg',
    )
