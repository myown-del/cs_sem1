import pathlib
import random
import typing as tp
from contextlib import suppress

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: tp.Tuple[int, int],
        randomize: bool = True,
        max_generations: tp.Optional[float] = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        if not randomize:
            return [[0] * self.cols for _ in range(self.rows)]
        else:
            return [
                [random.randint(0, 1) for _ in range(self.cols)]
                for _ in range(self.rows)
            ]

    def get_neighbours(self, cell: Cell) -> Cells:
        neighbours = []
        row, col = cell
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if (
                    0 <= row + i
                    and 0 <= col + j
                    and (i, j) != (0, 0)
                ):
                    with suppress(IndexError):
                        neighbours.append(self.curr_generation[row + i][col + j])
        return neighbours

    def get_next_generation(self) -> Grid:
        next_generation = self.create_grid()
        for i in range(self.rows):
            for j in range(self.cols):
                neighbours = sum(self.get_neighbours((i, j)))
                if self.curr_generation[i][j] == 1:
                    if neighbours in [2, 3]:
                        next_generation[i][j] = 1
                    else:
                        next_generation[i][j] = 0
                else:
                    if neighbours == 3:
                        next_generation[i][j] = 1
                    else:
                        next_generation[i][j] = 0
        return next_generation

    def step(self) -> None:
        self.prev_generation = self.curr_generation
        self.curr_generation = self.get_next_generation()
        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        return self.generations >= self.max_generations

    @property
    def is_changing(self) -> bool:
        return self.prev_generation != self.curr_generation

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.
        """
        pass

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        pass
