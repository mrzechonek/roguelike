#!/usr/bin/env python3
# encoding: utf-8

import curses
import time


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
        if isinstance(item, Key):
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
        self.item = Key()

class Map:
    TILES = {
        '.': Floor,
        '#': Wall,
        '+': Door,
        '1': LockedDoor,
        '2': FloorWithKey,
    }

    def __init__(self, filename):
        with open(filename) as f:
            self.tiles = []

            for y, r in enumerate(f):
                row = []
                for x, c in enumerate(r.strip()):
                    row.append(self.make_tile(c, y, x))
                self.tiles.append(row)


    def make_tile(self, character, y, x):
        klass = Map.TILES[character]
        return klass(y, x)

    def show(self, screen):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                character, color_pair = tile.glyph()
                screen.addstr(y, x, character, color_pair)

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


class Player:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.items = [Knife()]

    def show(self, screen):
        character, color_pair = self.glyph()
        screen.addstr(self.y, self.x, character, color_pair)

    def glyph(self):
        return ('@', Colors.WHITE)

    def move(self, tile):
        if not tile.passable():
            raise ActionException("a %s blocks your way" % tile)

        self.y = tile.y
        self.x = tile.x

    def drop(self, tile, item):
        if item is None:
            raise ActionException("you don't have such an item")

        if tile.item is not None:
            raise ActionException("there's no space on the floor")

        tile.item = item
        self.items.remove(item)
        return tile.item

    def pickup(self, tile):
        if not tile.item:
            raise ActionException("there's nothing here")

        self.items.append(tile.item)
        tile.item = None
        return self.items[-1]

    def open(self, tile):
        tile.open()

    def close(self, tile):
        tile.close()

    def use(self, tile, item):
        return tile.use(item)


class ActionException(Exception):
    pass


class Action:
    def __init__(self, player, tile):
        self.player = player
        self.tile = tile

    def perform(self):
        raise NotImplemented


class Move(Action):
    def perform(self):
        try:
            self.player.move(self.tile)
            item = getattr(self.tile, "item", None)
            if item:
                return ("You walk. There is a %s on the floor." % item, Colors.LIGHT_GRAY)
            else:
                return ("You walk", Colors.LIGHT_GRAY)
        except ActionException as ex:
            return ("You can't go that way: %s" % str(ex), Colors.DARK_RED)



class Wait(Action):
    def __init__(self, message="You wait", color=None):
        self.message = message
        self.color = color or Colors.LIGHT_GRAY

    def perform(self):
        return (self.message, self.color)



class Drop(Action):
    def __init__(self, player, tile, item):
        super().__init__(player, tile)
        self.item = item

    def perform(self):
        try:
            item = self.player.drop(self.tile, self.item)
            return ("You drop the %s" % item, Colors.LIGHT_GRAY)
        except ActionException as ex:
            return ("You can't drop that: %s" % ex, Colors.DARK_RED)


class PickUp(Action):
    def perform(self):
        try:
            item = self.player.pickup(self.tile)
            return ("You pick up the %s" % item, Colors.LIGHT_GRAY)
        except ActionException as ex:
            return ("You can't pick that up: %s" % ex, Colors.DARK_RED)


class Open(Action):
    def perform(self):
        try:
            self.player.open(self.tile)
            return ("You open the %s" % self.tile, Colors.LIGHT_GRAY)
        except ActionException as ex:
            return ("You can't open the %s: %s" % (self.tile, ex), Colors.DARK_RED)
        except Exception as ex:
            return ("There's nothing to open", Colors.DARK_RED)


class Close(Action):
    def perform(self):
        try:
            self.player.close(self.tile)
            return ("You close the %s" % (self.tile), Colors.LIGHT_GRAY)
        except ActionException as ex:
            return ("You can't close the %s: %s" % (self.tile, ex), Colors.DARK_RED)
        except Exception as ex:
            return ("There's nothing to close", Colors.DARK_RED)

class Use(Action):
    def __init__(self, player, tile, item):
        super().__init__(player, tile)
        self.item = item

    def perform(self):
        try:
            result = self.player.use(self.tile, self.item)
            return ("You use the %s on the %s: %s" % (self.item, self.tile, result or "nothing happens"), Colors.LIGHT_GRAY)
        except ActionException as ex:
            return ("You can't use the %s on a %s: %s" % (self.item, self.tile, ex), Colors.DARK_RED)
        except Exception as ex:
            return ("You don't know what to do with that", Colors.DARK_RED)

class Game:
    DIRECTIONS = [
        (curses.KEY_LEFT, 0, -1),
        (curses.KEY_UP, -1, 0),
        (curses.KEY_RIGHT, 0, 1),
        (curses.KEY_DOWN, 1, 0)
    ]

    def __init__(self, screen, map):
        self.screen = screen
        self.status = curses.newwin(1, 80, 25, 0)
        self.map = Map(map)
        self.player = Player(1,1)


    def _get_direction(self, message=None, pressed=None):
        if message:
            self.message("%s [<arrows>]?" % message)

        pressed = pressed or self.screen.getch()

        for key, dy, dx in Game.DIRECTIONS:
            if pressed == key:
                return self.player.y + dy, self.player.x + dx

        return None, None

    def _get_item(self, message):
        selection = ", ".join([ "%i: %s" % i for i in enumerate(self.player.items, 1)])
        self.message("%s [%s]?" % (message, selection))

        pressed = self.screen.getch()
        try:
            return self.player.items[pressed - ord('1')]
        except IndexError:
            return None

    def action(self):
        pressed = self.screen.getch()

        y, x = self._get_direction(pressed=pressed)
        if y and x:
            return Move(self.player, self.map.tiles[y][x])

        # open
        if pressed == ord('o'):

            y, x = self._get_direction("Open what")
            if y and x:
                return Open(self.player, self.map.tiles[y][x])

        # close
        if pressed == ord('c'):
            y, x = self._get_direction("Close what")
            if y and x:
                return Close(self.player, self.map.tiles[y][x])

        y, x = self.player.y, self.player.x

        # pick up
        if pressed == ord('p'):
            return PickUp(self.player, self.map.tiles[y][x])

        # drop
        if pressed == ord('d'):
            item = self._get_item("Drop what")
            return Drop(self.player, self.map.tiles[y][x], item)

        # use
        if pressed == ord('u'):
            item = self._get_item("Use what")
            if item:
                y, x = self._get_direction("Use %s on what" % item)
                if y and x:
                    return Use(self.player, self.map.tiles[y][x], item)

        if pressed == ord('?'):
            return Wait("<arrows>: walk, O: open, C: close, P: pick up, D: drop, U: use")

        return Wait()

    def message(self, message, color=None):
        self.status.clear()
        self.status.addstr(0, 0, message, color or Colors.LIGHT_GRAY)
        self.status.addstr(0, 72, "?: help")
        self.status.refresh()

    def run(self):
        self.screen.refresh()
        self.message("You stand in a corridor.")

        while True:
            self.map.show(self.screen)
            self.player.show(self.screen)
            self.screen.refresh()

            action = self.action()
            if action:
                message, color = action.perform()
                self.message(message, color)


class Colors:
    def __init__(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

        Colors.DARK_GRAY = curses.color_pair(1) | curses.A_BOLD
        Colors.BROWN = curses.color_pair(2)
        Colors.WHITE = curses.color_pair(3) | curses.A_BOLD
        Colors.LIGHT_GRAY = curses.color_pair(3)
        Colors.DARK_RED = curses.color_pair(4)
        Colors.YELLOW = curses.color_pair(2) | curses.A_BOLD


def main(screen):
    curses.curs_set(0)
    colors = Colors()

    game = Game(screen, 'map.txt')
    game.run()


if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("Thanks for playing!")
