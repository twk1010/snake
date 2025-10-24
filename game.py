import pygame
import random
from typing import Optional, Tuple
from snake import Snake
from portal import PortalPair

Cell = Tuple[int, int]

class Game:
    def __init__(self, screen: pygame.Surface, settings: dict, window_size: Tuple[int,int], cell_size: int):
        self.screen = screen
        self.settings = settings
        self.window_width, self.window_height = window_size
        self.cell_size = cell_size
        self.clock = pygame.time.Clock()

        self.colors = settings.get("colors", {})
        self.fps = int(settings.get("fps", 15))

        self.snake = Snake(self.window_width, self.window_height, self.cell_size)
        self.food_pos: Optional[Cell] = None
        self.score = 0

        self.font_large = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 32)

        self.running = True
        self.paused = False
        self.game_over = False

        # use PortalPair to manage portals
        self.portals = PortalPair(self.window_width, self.window_height, self.cell_size, respawn_delay=4000)
        self.portals.next_spawn_at = pygame.time.get_ticks() + 2000

        self.generate_food()

    # --- helpers ---
    def _rand_cell(self) -> Cell:
        max_x = (self.window_width - self.cell_size) // self.cell_size
        max_y = (self.window_height - self.cell_size) // self.cell_size
        return (random.randint(0, max_x) * self.cell_size,
                random.randint(0, max_y) * self.cell_size)

    def generate_food(self) -> None:
        for _ in range(300):
            pos = self._rand_cell()
            if pos in self.snake.body:
                continue
            if self.portals.active and (pos == self.portals.a or pos == self.portals.b):
                continue
            self.food_pos = pos
            return
        self.food_pos = None

    # --- draw / overlays ---
    def draw(self) -> None:
        self.screen.fill(self.colors.get("bg", (0,0,0)))
        snake_color = self.colors.get("snake", (0,255,0))
        for seg in self.snake.body:
            pygame.draw.rect(self.screen, snake_color, (seg[0], seg[1], self.cell_size, self.cell_size))
        if self.food_pos:
            pygame.draw.rect(self.screen, self.colors.get("food", (255,255,255)),
                             (self.food_pos[0], self.food_pos[1], self.cell_size, self.cell_size))
        self.portals.draw(self.screen)
        self.draw_overlays()
        pygame.display.flip()

    def draw_overlays(self) -> None:
        if self.paused:
            overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            self.screen.blit(overlay, (0,0))
            text = self.font_large.render("PAUSED - Press P to resume", True, (255,255,255))
            self.screen.blit(text, text.get_rect(center=(self.window_width//2, self.window_height//2)))
        if self.game_over:
            overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            self.screen.blit(overlay, (0,0))
            t1 = self.font_large.render("GAME OVER", True, (255,50,50))
            t2 = self.font_small.render(f"Score: {self.score}  -  R to restart  |  Esc to quit", True, (255,255,255))
            self.screen.blit(t1, t1.get_rect(center=(self.window_width//2, self.window_height//2 - 30)))
            self.screen.blit(t2, t2.get_rect(center=(self.window_width//2, self.window_height//2 + 20)))

    # --- collisions / portals ---
    def check_food_collision(self) -> None:
        if self.food_pos is not None and self.snake.body[0] == self.food_pos:
            self.snake.size += 1
            self.score += 1
            self.generate_food()

    def check_self_and_wall(self) -> None:
        head = self.snake.body[0]
        if (head[0] < 0 or head[0] >= self.window_width or
            head[1] < 0 or head[1] >= self.window_height or
            head in self.snake.body[1:]):
            self.game_over = True

    # --- input & events ---
    def handle_events(self) -> None:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif ev.key == pygame.K_r and self.game_over:
                    self.restart()
                elif ev.key == pygame.K_ESCAPE:
                    self.running = False
                elif ev.key == pygame.K_LEFT:
                    self.snake.change_direction((-1, 0))
                elif ev.key == pygame.K_RIGHT:
                    self.snake.change_direction((1, 0))
                elif ev.key == pygame.K_UP:
                    self.snake.change_direction((0, -1))
                elif ev.key == pygame.K_DOWN:
                    self.snake.change_direction((0, 1))

    def handle_continuous_input(self) -> None:
        keys = pygame.key.get_pressed()
        if not self.paused and not self.game_over:
            if keys[pygame.K_LEFT]:
                self.snake.change_direction((-1, 0))
            elif keys[pygame.K_RIGHT]:
                self.snake.change_direction((1, 0))
            elif keys[pygame.K_UP]:
                self.snake.change_direction((0, -1))
            elif keys[pygame.K_DOWN]:
                self.snake.change_direction((0, 1))

    # --- update loop ---
    def update(self) -> None:
        # spawn portals when due (PortalPair uses pygame.time.get_ticks internally)
        self.portals.try_spawn_if_due(self.snake.body, self.food_pos)

        if not self.paused and not self.game_over:
            self.snake.move()
            self.check_food_collision()
            teleported = self.portals.try_teleport(self.snake)
            if self.portals.locked:
                self.portals.update_locked_state(self.snake.body)
            self.check_self_and_wall()

    # --- control ---
    def restart(self) -> None:
        self.snake = Snake(self.window_width, self.window_height, self.cell_size)
        self.score = 0
        self.game_over = False
        self.paused = False
        self.food_pos = None
        self.generate_food()
        self.portals.clear_and_schedule()
        self.portals.next_spawn_at = pygame.time.get_ticks() + 2000

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.handle_continuous_input()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        pygame.quit()