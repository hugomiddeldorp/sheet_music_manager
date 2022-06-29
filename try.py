import curses
from curses import wrapper

def main(stdscr):
    screen = curses.initscr()
    curses.noecho()
    c = screen.getch()
    while c != ord("q"):
        screen.clear()
        screen.addstr(0, 0, str(c))
        screen.addstr(1, 0, str(ord('\b')))
        screen.addstr(2, 0, str(curses.KEY_DC))
        c = screen.getch()
    
wrapper(main)
