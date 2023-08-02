import curses

from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)
        self.screen = None

    def draw_borders(self) -> None:
        for x in range(self.life.cols + 1):
            self.screen.addstr(0, x, '─')
            self.screen.addstr(self.life.rows + 1, x, '─')
        for y in range(self.life.rows + 1):
            self.screen.addstr(y, 0, '│')
            self.screen.addstr(y, self.life.cols + 1, '│')
        # corners
        self.screen.addstr(0, 0, '┌')
        self.screen.addstr(0, self.life.cols + 1, '┐')
        self.screen.addstr(self.life.rows + 1, 0, '└')
        self.screen.addstr(self.life.rows + 1, self.life.cols + 1, '┘')

    def draw_grid(self) -> None:
        self.screen.clear()
        self.draw_borders()
        for x in range(self.life.cols):
            for y in range(self.life.rows):
                if self.life.curr_generation[y][x] == 1:
                    self.screen.addstr(y + 1, x + 1, '⬤')
        self.screen.refresh()
        self.screen.getch()

    def run(self) -> None:
        self.screen = curses.initscr()
        self.draw_borders()

        while True:
            if not self.life.is_changing or self.life.is_max_generations_exceeded:
                break
            self.draw_grid()
            self.life.step()

        curses.endwin()


if __name__ == "__main__":
    life = GameOfLife((20, 30), max_generations=500)
    gui = Console(life)
    gui.run()
