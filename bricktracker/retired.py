# Lego retired set
class BrickRetired(object):
    theme: str
    subtheme: str
    number: str
    name: str
    age: str
    piece_count: str
    retirement_date: str

    def __init__(
        self,
        theme: str,
        subtheme: str,
        number: str,
        name: str,
        age: str,
        piece_count: str,
        retirement_date: str,
        *_,
    ):
        self.theme = theme
        self.subtheme = subtheme
        self.number = number
        self.name = name
        self.age = age
        self.piece_count = piece_count
        self.retirement_date = retirement_date
