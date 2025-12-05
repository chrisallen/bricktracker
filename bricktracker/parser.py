from .exceptions import ErrorException


# Make sense of string supposed to contain a set ID
def parse_set(set: str, /) -> str:
    number, _, version = set.partition('-')

    # Set number can be alphanumeric (e.g., "McDR6US", "10312", "COMCON035")
    # Just validate it's not empty
    if not number or number.strip() == '':
        raise ErrorException('Set number cannot be empty')

    # Clean up the number (trim whitespace)
    number = number.strip()

    # Version defaults to 1 if not provided
    if version == '':
        version = '1'

    # Version must be a positive integer
    try:
        version_int = int(version)
    except Exception:
        raise ErrorException('Version "{version}" is not a number'.format(
            version=version,
        ))

    if version_int < 0:
        raise ErrorException('Version "{version}" should be positive'.format(
            version=version,
        ))

    return '{number}-{version}'.format(number=number, version=version_int)
