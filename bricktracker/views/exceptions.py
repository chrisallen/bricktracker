from functools import wraps
from typing import Callable, ParamSpec, Tuple, Union

from werkzeug.wrappers.response import Response

from .error import error

# Decorator type hinting is hard.
# What a view can return (str or Response or (Response, xxx))
ViewReturn = Union[
    str,
    Response,
    Tuple[str | Response, int]
]

# View signature (*arg, **kwargs -> (str or Response or (Response, xxx))
P = ParamSpec('P')
ViewCallable = Callable[P, ViewReturn]


# Return the exception template or response if an exception occured
def exception_handler(
    file: str,
    /,
    *,
    json: bool = False,
    post_redirect: str | None = None,
    error_name: str = 'error',
    **superkwargs,
) -> Callable[[ViewCallable], ViewCallable]:
    def outer(function: ViewCallable, /) -> ViewCallable:
        @wraps(function)
        def wrapper(*args, **kwargs) -> ViewReturn:
            try:
                return function(*args, **kwargs)
            # Handle errors
            except Exception as e:
                return error(
                    e,
                    file,
                    json=json,
                    post_redirect=post_redirect,
                    error_name=error_name,
                    **kwargs,
                    **superkwargs,
                )
        return wrapper
    return outer
