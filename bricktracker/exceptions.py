# Something was not found
class NotFoundException(Exception):
    ...


# Generic error exception
class ErrorException(Exception):
    title: str = 'Error'


# Configuration error
class ConfigurationMissingException(ErrorException):
    title: str = 'Configuration missing'


# Database error
class DatabaseException(ErrorException):
    title: str = 'Database error'


# Download error
class DownloadException(ErrorException):
    title: str = 'Download error'
