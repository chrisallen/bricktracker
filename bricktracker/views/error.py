import logging
from sqlite3 import Error, OperationalError
import traceback
from typing import Any, Tuple

from flask import jsonify, redirect, request, render_template, url_for
from werkzeug.wrappers.response import Response

from ..exceptions import DatabaseException, ErrorException, NotFoundException

logger = logging.getLogger(__name__)


# Get the cleaned exception
def cleaned_exception(e: Exception, /) -> str:
    trace = traceback.TracebackException.from_exception(e)

    cleaned: list[str] = []

    # Hacky: stripped from the call to the decorator wrapper() or outer()
    for line in trace.format():
        if 'in wrapper' not in line and 'in outer' not in line:
            cleaned.append(line)

    return ''.join(cleaned)


# Generic error
def error(
    error: Exception | None,
    file: str,
    /,
    *,
    json: bool = False,
    post_redirect: str | None = None,
    error_name: str = 'error',
    **kwargs,
) -> str | Tuple[str | Response, int] | Response:
    # Back to the index if no error (not sure if this can happen)
    if error is None:
        if json:
            return json_error(
                'error() called without an error',
                error_name=error_name
            )
        else:
            return redirect(url_for('index.index'))

    # Convert SQLite errors
    if isinstance(error, (Error, OperationalError)):
        error = DatabaseException(error)

    # Clear redirect if not POST or json
    if json or request.method != 'POST':
        post_redirect = None

    # Not found
    if isinstance(error, NotFoundException):
        return error_404(
            error,
            json=json,
            post_redirect=post_redirect,
            error_name=error_name,
            **kwargs
        )

    # Common error
    elif isinstance(error, ErrorException):
        # Error
        logger.error('{title}: {error}'.format(
            title=error.title,
            error=str(error),
        ))

        # Debug
        logger.debug(cleaned_exception(error))

        if json:
            return json_error(
                str(error),
                error_name=error_name
            )
        elif post_redirect is not None:
            return redirect_error(
                post_redirect,
                error=str(error),
                error_name=error_name,
                **kwargs,
            )
        else:
            return render_template(
                'error.html',
                title=error.title,
                error=str(error)
            )

    # Exception
    else:
        # Error
        logger.error(cleaned_exception(error))

        if error.__traceback__ is not None:
            line = error.__traceback__.tb_lineno
        else:
            line = None

        if json:
            return json_error(
                'Exception: {error}'.format(error=str(error)),
                error_name=error_name,
                name=type(error).__name__,
                line=line,
                file=file
            ), 500
        elif post_redirect is not None:
            return redirect_error(
                post_redirect,
                error=str(error),
                error_name=error_name,
                **kwargs,
            )
        else:
            return render_template(
                'exception.html',
                error=str(error),
                name=type(error).__name__,
                line=line,
                file=file,
            )


# Error 404
def error_404(
    error: Exception,
    /,
    *,
    json: bool = False,
    post_redirect: str | None = None,
    error_name: str = 'error',
    **kwargs,
) -> Response | Tuple[str | Response, int]:
    # Warning
    logger.warning('Not found: {error} (path: {path})'.format(
        error=str(error),
        path=request.path,
    ))

    if json:
        return json_error(
            'Not found: {error}'.format(error=str(error)),
            error_name=error_name
        ), 404
    elif post_redirect is not None:
        return redirect_error(
            post_redirect,
            error=str(error),
            error_name=error_name,
            **kwargs,
        )
    else:
        return render_template('404.html', error=str(error)), 404


# JSON error with parametric error name
def json_error(
    error: str,
    error_name: str = 'error',
    **parameters: Any
) -> Response:
    parameters[error_name] = error

    return jsonify(parameters)


# Redirect error with parametric error name
def redirect_error(
    url: str,
    error: str,
    error_name: str = 'error',
    **kwargs
) -> Response:
    error_parameter: dict[str, str] = {}
    error_parameter[error_name] = str(error)

    return redirect(url_for(
        url,
        **error_parameter,
        **kwargs
    ))
