from colors import Colors


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
                return ("You walk. There is a %s on the floor." % item,
                        Colors.LIGHT_GRAY)
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
            return ("You open the %s" % self.tile,
                    Colors.LIGHT_GRAY)
        except ActionException as ex:
            return ("You can't open the %s: %s" % (self.tile, ex),
                    Colors.DARK_RED)
        except Exception as ex:
            return ("There's nothing to open",
                    Colors.DARK_RED)


class Close(Action):
    def perform(self):
        try:
            self.player.close(self.tile)
            return ("You close the %s" % (self.tile),
                    Colors.LIGHT_GRAY)
        except ActionException as ex:
            return ("You can't close the %s: %s" % (self.tile, ex),
                    Colors.DARK_RED)
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
