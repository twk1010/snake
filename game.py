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

        # Portals: each is (x,y) or None
        self.portal_a = None
        self.portal_b = None
        self.portals_active = False

        # When True, portals exist but teleporting is locked until the snake fully exits destination
        self.portal_locked = False
        self.portal_locked_dest = None

        # Respawn timing (ms)
        self.portal_respawn_delay = 4000
        self.portal_next_spawn = pygame.time.get_ticks() + 2000  # spawn shortly after start

        self.generate_food()

    # --- Game logic helpers ---
    def generate_food(self):
        max_x = (self.window_width - self.cell_size) // self.cell_size
        max_y = (self.window_height - self.cell_size) // self.cell_size
        while True:
            x = random.randint(0, max_x) * self.cell_size
            y = random.randint(0, max_y) * self.cell_size
            food = (x, y)
            if food not in self.snake.body and food != self.portal_a and food != self.portal_b:
                self.food_pos = food
                return

    def generate_portals(self):
        """Place two portals (blue and orange) on free cells not overlapping snake or food."""
        max_x = (self.window_width - self.cell_size) // self.cell_size
        max_y = (self.window_height - self.cell_size) // self.cell_size

        def rand_cell():
            return (random.randint(0, max_x) * self.cell_size,
                    random.randint(0, max_y) * self.cell_size)

        # attempt until we find two distinct, valid cells
        for _ in range(200):
            a = rand_cell()
            b = rand_cell()
            if a == b:
                continue
            if a in self.snake.body or b in self.snake.body:
                continue
            if a == self.food_pos or b == self.food_pos:
                continue
            # ok
            self.portal_a = a
            self.portal_b = b
            self.portals_active = True
            self.portal_locked = False
            self.portal_locked_dest = None
            return
        # fallback: do nothing if couldn't place
        self.portal_a = None
        self.portal_b = None
        self.portals_active = False

    def clear_portals_and_schedule(self):
        self.portal_a = None
        self.portal_b = None
        self.portals_active = False
        self.portal_locked = False
        self.portal_locked_dest = None
        self.portal_next_spawn = pygame.time.get_ticks() + self.portal_respawn_delay

    def draw_portals(self):
        if not self.portals_active or self.portal_a is None or self.portal_b is None:
            return
        # blue portal A
        rect_a = (self.portal_a[0], self.portal_a[1], self.cell_size, self.cell_size)
        rect_b = (self.portal_b[0], self.portal_b[1], self.cell_size, self.cell_size)
        # draw filled rects with a border
        pygame.draw.rect(self.screen, (30, 144, 255), rect_a)    # blue
        pygame.draw.rect(self.screen, (255, 165, 0), rect_b)     # orange
        pygame.draw.rect(self.screen, (0,0,0), rect_a, 1)
        pygame.draw.rect(self.screen, (0,0,0), rect_b, 1)

    def check_food_collision(self):
        if self.snake.body[0] == self.food_pos:
            self.snake.size += 1
            self.score += 1
            self.generate_food()

    def check_portal_entry(self):
        """Teleport head between portals when entered and manage portal lifecycle."""
        if not self.portals_active or self.portal_a is None or self.portal_b is None:
            return

        head = self.snake.body[0]

        # If locked, wait until entire snake body has left the locked_dest portal cell
        if self.portal_locked:
            dest = self.portal_locked_dest
            # If no segment occupies dest anymore, remove portals and schedule a respawn
            if dest is not None and all(seg != dest for seg in self.snake.body):
                self.clear_portals_and_schedule()
            return

        # Not locked: check entry into A or B
        if head == self.portal_a:
            # teleport to B
            self._teleport_head(self.portal_b)
            # lock portals until body exits destination
            self.portal_locked = True
            self.portal_locked_dest = self.portal_b
        elif head == self.portal_b:
            self._teleport_head(self.portal_a)
            self.portal_locked = True
            self.portal_locked_dest = self.portal_a

    def _teleport_head(self, dest_pos):
        """Place head at dest_pos while preserving direction. Ensure resulting head is on grid."""
        # replace head position (index 0)
        if dest_pos is None:
            return
        # set head to dest_pos
        self.snake.body[0] = dest_pos
        # To avoid immediate self-collision against the body that remains at dest,
        # we do not grow or shrink here (movement logic already handled). The portal_locked
        # mechanism ensures portals remain until the snake fully exits the dest cell.

    def check_collisions(self):
        head = self.snake.body[0]
        if (head[0] < 0 or head[0] >= self.window_width or
            head[1] < 0 or head[1] >= self.window_height or
            head in self.snake.body[1:]):
            self.game_over = True

    # --- Input & events ---
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

    # --- Drawing ---
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
        self.screen.fill(self.settings.get("colors", {}).get("bg", (0, 0, 0)))
        # draw snake
        for seg in self.snake.body:
            pygame.draw.rect(self.screen, self.colors.get("snake", (0,255,0)),
                             (seg[0], seg[1], self.cell_size, self.cell_size))
        self.draw_food()
        # draw portals if active
        self.draw_portals()
        self.draw_overlays()
        pygame.display.flip()

    # --- Update ---
    def update(self):
        # spawn portals when scheduled
        now = pygame.time.get_ticks()
        if not self.portals_active and now >= self.portal_next_spawn:
            self.generate_portals()

        if not self.paused and not self.game_over:
            self.snake.move()
            self.check_food_collision()
            # check portal entry after movement (teleport head if entered)
            self.check_portal_entry()
            self.check_collisions()

    # --- Control ---
    def restart(self):
        self.snake = Snake(self.window_width, self.window_height, self.cell_size)
        self.score = 0
        self.game_over = False
        self.paused = False
        self.food_pos = None
        self.generate_food()
        # reset portals
        self.portal_a = None
        self.portal_b = None
        self.portals_active = False
        self.portal_locked = False
        self.portal_locked_dest = None
        self.portal_next_spawn = pygame.time.get_ticks() + 2000

    def run(self):
        while self.running:
            self.handle_events()
            self.handle_continuous_input()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        pygame.quit()