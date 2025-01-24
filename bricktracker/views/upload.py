import os

from flask import redirect, request, url_for
from werkzeug.datastructures import FileStorage
from werkzeug.wrappers.response import Response

from ..exceptions import ErrorException


# Helper for a standard file upload process
def upload_helper(
    name: str,
    endpoint: str,
    /,
    *,
    extensions: list[str] = [],
) -> FileStorage | Response:
    # Bogus submit
    if name not in request.files:
        return redirect(url_for(endpoint))

    file = request.files[name]

    # Empty submit
    if not file or file.filename is None or file.filename == '':
        return redirect(url_for(endpoint, empty_file=True))

    # Not allowed extension
    # Security: not really
    if len(extensions):
        _, extension = os.path.splitext(file.filename)

        if extension not in extensions:
            raise ErrorException('{file} extension is not an allowed. Expected: {allowed}'.format(  # noqa: E501
                file=file.filename,
                allowed=', '.join(extensions)
            ))

    return file
