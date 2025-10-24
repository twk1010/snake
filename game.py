import pygame
import random
from snake import Snake

class Game:
    def __init__(self, screen, settings, window_size, cell_size):
        self.screen = screen
        self.settings = settings
        self.window_width, self.window_height = window_size
        self.cell_size = cell_size
        self.clock = pygame.time.Clock()

        self.snake = Snake(self.window_width, self.window_height, self.cell_size)
        self.food_pos = None
        self.score = 0

        self.font_large = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 32)

        self.running = True
        self.paused = False
        self.game_over = False

        self.colors = settings["colors"]
        self.fps = settings.get("fps", 15)

        self.generate_food()

    def generate_food(self):
        max_x = (self.window_width - self.cell_size) // self.cell_size
        max_y = (self.window_height - self.cell_size) // self.cell_size
        while True:
            x = random.randint(0, max_x) * self.cell_size
            y = random.randint(0, max_y) * self.cell_size
            pos = (x, y)
            if pos not in self.snake.body:
                self.food_pos = pos
                return

    def draw_food(self):
        if self.food_pos is not None:
            pygame.draw.rect(self.screen, self.colors.get("food", (255,255,255)),
                             (self.food_pos[0], self.food_pos[1], self.cell_size, self.cell_size))

    def check_food_collision(self):
        if self.snake.body[0] == self.food_pos:
            self.snake.size += 1
            self.score += 1
            self.generate_food()

    def check_collisions(self):
        head = self.snake.body[0]
        if (head[0] < 0 or head[0] >= self.window_width or
            head[1] < 0 or head[1] >= self.window_height or
            head in self.snake.body[1:]):
            self.game_over = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.restart()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction((1, 0))
                elif event.key == pygame.K_UP:
                    self.snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction((0, 1))

    def handle_continuous_input(self):
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

    def draw_overlays(self):
        if self.paused:
            overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            text = self.font_large.render("PAUSED - Press P to resume", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(self.window_width // 2, self.window_height // 2)))

        if self.game_over:
            overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            txt1 = self.font_large.render("GAME OVER", True, (255, 50, 50))
            txt2 = self.font_small.render(f"Score: {self.score}  -  R to restart  |  Esc to quit", True, (255, 255, 255))
            self.screen.blit(txt1, txt1.get_rect(center=(self.window_width // 2, self.window_height // 2 - 30)))
            self.screen.blit(txt2, txt2.get_rect(center=(self.window_width // 2, self.window_height // 2 + 20)))

    def draw(self):
        self.screen.fill(self.colors.get("bg", (0, 0, 0)))
        # draw snake
        for seg in self.snake.body:
            pygame.draw.rect(self.screen, self.colors.get("snake", (0,255,0)),
                             (seg[0], seg[1], self.cell_size, self.cell_size))
        self.draw_food()
        self.draw_overlays()
        pygame.display.flip()

    def update(self):
        if not self.paused and not self.game_over:
            self.snake.move()
            self.check_food_collision()
            self.check_collisions()

    def restart(self):
        self.snake = Snake(self.window_width, self.window_height, self.cell_size)
        self.score = 0
        self.game_over = False
        self.paused = False
        self.generate_food()

    def run(self):
        while self.running:
            self.handle_events()
            self.handle_continuous_input()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        pygame.quit()