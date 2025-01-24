from typing import Any


# SQLite record fields
class BrickRecordFields(object):
    def __getattr__(self, name: str, /) -> Any:
        if name not in self.__dict__:
            raise AttributeError(name)

        return self.__dict__[name]

    def __setattr__(self, name: str, value: Any, /) -> None:
        self.__dict__[name] = value
