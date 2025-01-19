from typing import Any


# SQLite record fields
class BrickRecordFields(object):
    def __getattr__(self, name: str, /) -> Any:
        return self.__dict__[name]

    def __setattr__(self, name: str, value: Any, /) -> None:
        self.__dict__[name] = value
