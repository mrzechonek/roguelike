from colors import Colors


class Item:
    def glyph(self):
        raise NotImplemented

    def __str__(self):
        raise NotImplemented


class Knife(Item):
    def glyph(self):
        return ('(', Colors.YELLOW)

    def __str__(self):
        return "knife"


class Key(Item):
    def glyph(self):
        return (',', Colors.DARK_RED)

    def __str__(self):
        return "key"
