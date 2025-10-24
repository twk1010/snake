import pygame
import random
from typing import Optional, Tuple, List

Cell = Tuple[int, int]

class PortalPair:
    def __init__(self, window_w: int, window_h: int, cell_size: int, respawn_delay: int = 4000):
        self.window_w = window_w
        self.window_h = window_h
        self.cell_size = cell_size
        self.respawn_delay = respawn_delay

        self.a: Optional[Cell] = None
        self.b: Optional[Cell] = None
        self.active: bool = False

        self.locked: bool = False            # True while waiting for snake to fully leave exit tile
        self.exit_tile: Optional[Cell] = None

        self.next_spawn_at: int = pygame.time.get_ticks() + 2000

    def _rand_cell(self) -> Cell:
        max_x = (self.window_w - self.cell_size) // self.cell_size
        max_y = (self.window_h - self.cell_size) // self.cell_size
        return (random.randint(0, max_x) * self.cell_size,
                random.randint(0, max_y) * self.cell_size)

    def try_spawn_if_due(self, snake_body: List[Cell], food_pos: Optional[Cell]) -> None:
        now = pygame.time.get_ticks()
        if self.active or now < self.next_spawn_at:
            return
        for _ in range(300):
            a = self._rand_cell()
            b = self._rand_cell()
            if a == b:
                continue
            if a in snake_body or b in snake_body:
                continue
            if food_pos is not None and (a == food_pos or b == food_pos):
                continue
            self.a = a
            self.b = b
            self.active = True
            self.locked = False
            self.exit_tile = None
            return
        # failed to place - schedule retry
        self.next_spawn_at = now + self.respawn_delay

    def clear_and_schedule(self) -> None:
        self.a = None
        self.b = None
        self.active = False
        self.locked = False
        self.exit_tile = None
        self.next_spawn_at = pygame.time.get_ticks() + self.respawn_delay

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active or self.a is None or self.b is None:
            return
        pygame.draw.rect(surface, (30, 144, 255), (self.a[0], self.a[1], self.cell_size, self.cell_size))
        pygame.draw.rect(surface, (255, 165, 0), (self.b[0], self.b[1], self.cell_size, self.cell_size))
        pygame.draw.rect(surface, (0,0,0), (self.a[0], self.a[1], self.cell_size, self.cell_size), 1)
        pygame.draw.rect(surface, (0,0,0), (self.b[0], self.b[1], self.cell_size, self.cell_size), 1)

    def try_teleport(self, snake) -> bool:
        """If head enters portal and portals are active & unlocked, teleport head and lock until full exit.
           Returns True if a teleport occurred."""
        if not self.active or self.a is None or self.b is None or self.locked:
            return False

        head = snake.body[0]
        if head == self.a:
            snake.body[0] = self.b
            self.locked = True
            self.exit_tile = self.b
            return True
        if head == self.b:
            snake.body[0] = self.a
            self.locked = True
            self.exit_tile = self.a
            return True
        return False

    def update_locked_state(self, snake_body: List[Cell]) -> None:
        """If locked, clear portals when no part of snake touches exit_tile."""
        if not self.locked or self.exit_tile is None:
            return
        if all(seg != self.exit_tile for seg in snake_body):
            self.clear_and_schedule()