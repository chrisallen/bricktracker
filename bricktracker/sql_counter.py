class BrickCounter(object):
    name: str
    table: str
    icon: str
    count: int

    def __init__(self, name: str, table: str, /, icon: str = ''):
        self.name = name
        self.table = table
        self.icon = icon
        self.count = 0
