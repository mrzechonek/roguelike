import curses


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
