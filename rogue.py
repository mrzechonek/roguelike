#!/usr/bin/env python3
# encoding: utf-8

import curses
import actions
from tiles import TileFactory
from colors import Colors


class Map:
    def __init__(self, filename):
        with open(filename) as f:
            self.tiles = []

            for y, r in enumerate(f):
                row = []
                for x, c in enumerate(r.strip()):
                    row.append(TileFactory.make_tile(c, y, x))
                self.tiles.append(row)

    def show(self, screen):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                character, color_pair = tile.glyph()
                screen.addstr(y, x, character, color_pair)


class Player:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.items = []

    def show(self, screen):
        character, color_pair = self.glyph()
        screen.addstr(self.y, self.x, character, color_pair)

    def glyph(self):
        return ('@', Colors.WHITE)

    def move(self, tile):
        if not tile.passable():
            raise actions.ActionException("a %s blocks your way" % tile)

        self.y = tile.y
        self.x = tile.x

    def drop(self, tile, item):
        if item is None:
            raise actions.ActionException("you don't have such an item")

        if tile.item is not None:
            raise actions.ActionException("there's no space on the floor")

        tile.item = item
        self.items.remove(item)
        return tile.item

    def pickup(self, tile):
        if not tile.item:
            raise actions.ActionException("there's nothing here")

        self.items.append(tile.item)
        tile.item = None
        return self.items[-1]

    def open(self, tile):
        tile.open()

    def close(self, tile):
        tile.close()

    def use(self, tile, item):
        return tile.use(item)


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
        self.player = Player(1, 1)

    def _get_direction(self, message=None, pressed=None):
        if message:
            self.message("%s [<arrows>]?" % message)

        pressed = pressed or self.screen.getch()

        for key, dy, dx in Game.DIRECTIONS:
            if pressed == key:
                return self.player.y + dy, self.player.x + dx

        return None, None

    def _get_item(self, message):
        selection = ", ".join(["%i: %s" % i for i in enumerate(self.player.items, 1)])
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
            return actions.Move(self.player, self.map.tiles[y][x])

        # open
        if pressed == ord('o'):

            y, x = self._get_direction("Open what")
            if y and x:
                return actions.Open(self.player, self.map.tiles[y][x])

        # close
        if pressed == ord('c'):
            y, x = self._get_direction("Close what")
            if y and x:
                return actions.Close(self.player, self.map.tiles[y][x])

        y, x = self.player.y, self.player.x

        # pick up
        if pressed == ord('p'):
            return actions.PickUp(self.player, self.map.tiles[y][x])

        # drop
        if pressed == ord('d'):
            item = self._get_item("Drop what")
            return actions.Drop(self.player, self.map.tiles[y][x], item)

        # use
        if pressed == ord('u'):
            item = self._get_item("Use what")
            if item:
                y, x = self._get_direction("Use %s on what" % item)
                if y and x:
                    return actions.Use(self.player, self.map.tiles[y][x], item)

        if pressed == ord('?'):
            return actions.Wait("<arrows>: walk, O: open, C: close, P: pick up, D: drop, U: use")

        return actions.Wait()

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
