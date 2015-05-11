
import items
from actions import ActionException
from colors import Colors


class Tile:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.item = None

    def passable(self):
        raise NotImplemented

    def glyph(self):
        raise NotImplemented


class Floor(Tile):
    def passable(self):
        return True

    def glyph(self):
        return self.item.glyph() if self.item else ('.', Colors.DARK_GRAY)


class Wall(Tile):
    def passable(self):
        return False

    def glyph(self):
        return ('#', Colors.DARK_GRAY)

    def __str__(self):
        return "wall"


class Door(Tile):
    OPEN = 1
    CLOSED = 2

    def __init__(self, y, x):
        super().__init__(y, x)
        self.item = False
        self.state = Door.CLOSED

    def passable(self):
        return self.state == Door.OPEN

    def glyph(self):
        return ('/' if self.passable() else '+', Colors.BROWN)

    def open(self):
        if self.state == Door.CLOSED:
            self.state = Door.OPEN
        else:
            raise ActionException("it's already open")

    def close(self):
        if self.state == Door.OPEN:
            self.state = Door.CLOSED
        else:
            raise ActionException("it's already closed")

    def __str__(self):
        return "door"


    def use(self, item):
        if isinstance(item, Knife):
            return "you stab at the door, leaving a mark"


class LockedDoor(Door):
    LOCKED = 3

    def __init__(self, y, x):
        super().__init__(y, x)
        self.state = LockedDoor.LOCKED

    def open(self):
        if self.state == LockedDoor.LOCKED:
            raise ActionException("it's locked")

        return super().open()

    def glyph(self):
        sign, color = super().glyph()
        return (sign, Colors.DARK_RED if self.state == LockedDoor.LOCKED else color)

    def use(self, item):
        if isinstance(item, items.Key):
            if self.state == LockedDoor.LOCKED:
                self.state = LockedDoor.CLOSED
                return "door is unlocked"
            elif self.state == LockedDoor.CLOSED:
                self.state = LockedDoor.LOCKED
                return "door is locked"
            else:
                raise ActionException("door is open")

        return super().use(item)


class FloorWithKey(Floor):
    def __init__(self, y, x):
        super().__init__(y, x)
        self.item = items.Key()


class TileFactory:
    TILES = {
        '.': Floor,
        '#': Wall,
        '+': Door,
        '1': LockedDoor,
        '2': FloorWithKey,
    }

    @staticmethod
    def make_tile(character, y, x):
        klass = TileFactory.TILES[character]
        return klass(y, x)

