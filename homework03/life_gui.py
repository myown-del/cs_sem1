import pygame

from life import GameOfLife
from pygame.locals import *
from ui import UI


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.cell_size = cell_size
        self.speed = speed
        self.screen = pygame.display.set_mode(
            (self.life.cols * self.cell_size, self.life.rows * self.cell_size)
        )

    @property
    def width(self) -> int:
        return self.life.cols * self.cell_size

    @property
    def height(self) -> int:
        return self.life.rows * self.cell_size

    def draw_lines(self) -> None:
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y), (self.width, y))

    def draw_grid(self) -> None:
        length = self.cell_size - 1
        for i in range(self.life.cols):
            for j in range(self.life.rows):
                if self.life.curr_generation[i][j] == 1:
                    color = pygame.Color("green")
                else:
                    color = pygame.Color("white")
                pygame.draw.rect(
                    surface=self.screen,
                    color=color,
                    rect=(i * self.cell_size + 1, j * self.cell_size + 1, length, length),
                )

    def handle_click(self, event: pygame.event.Event):
        x, y = event.pos
        col = y // self.cell_size
        row = x // self.cell_size
        if self.life.curr_generation[row][col]:
            self.life.curr_generation[row][col] = 0
        else:
            self.life.curr_generation[row][col] = 1
        self.draw_grid()
        pygame.display.flip()

    def run(self) -> None:
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))

        paused = False
        running = True
        while running:
            if not self.life.is_changing or self.life.is_max_generations_exceeded:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    paused = True

            self.draw_lines()

            if paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        paused = False
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.handle_click(event)
            else:
                self.life.step()
                self.draw_grid()
                pygame.display.flip()
                clock.tick(self.speed)
        pygame.quit()


if __name__ == "__main__":
    life = GameOfLife((100, 100), max_generations=500)
    gui = GUI(life)
    gui.run()
