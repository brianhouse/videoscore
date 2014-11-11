#!/usr/bin/env python3

import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

def main(screen):
    # Clear screen
    screen.clear()

    screen.addstr(0, 0, "%sx%s" % (curses.LINES, curses.COLS))

    rect(screen, 0, 0, curses.COLS-2, curses.LINES-1, True)

    rect(screen, 10, 10, 30, 40)

    # for 

    # rectangle(stdscr, 1, 1, curses.LINES - 2, curses.COLS - 2)    

    # # make text box
    # stdscr.addstr(10, 10, "Enter IM message: (hit Ctrl-G to send)")
    # editwin = curses.newwin(5,30, 2,1)
    # rectangle(stdscr, 1,0, 1+5+1, 1+30+1)
    # stdscr.refresh()
    # box = Textbox(editwin)
    # box.edit()     # Let the user edit until Ctrl-G is struck.
    # message = box.gather()

    # stdscr.refresh()
    # stdscr.getkey()

    # stdscr.addstr(10, 10, "This is a different message ")

    screen.refresh()
    screen.getkey()




def rect(screen, x1, y1, x2, y2, double=False):

    screen.addstr(y1, x1, '╔' if double else '┌')
    screen.addstr(y1, x2, '╗' if double else '┐')
    screen.addstr(y2, x1, '╚' if double else '└')
    screen.addstr(y2, x2, '╝' if double else '┘')

    for y in range(y2 - y1 - 1):
        screen.addstr(y1 + y + 1, x1, '║' if double else '│')
        screen.addstr(y1 + y + 1, x2, '║' if double else '│')

    for x in range(x2 - x1 - 1):
        screen.addstr(y1, x1 + x + 1, '═' if double else '─')
        screen.addstr(y2, x1 + x + 1, '═' if double else '─')

wrapper(main)