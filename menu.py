import pygame

class StartMenu:
    def __init__(self, screen, settings, window_size):
        self.screen = screen
        self.settings = settings
        self.window_size = window_size
        self.font = pygame.font.SysFont(None, 40)
        self.big = pygame.font.SysFont(None, 64)

    def run(self):
        speeds = self.settings.get("speeds", {})
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return None
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_1:
                        return int(speeds.get("slow", self.settings.get("fps")))
                    if ev.key == pygame.K_2:
                        return int(speeds.get("normal", self.settings.get("fps")))
                    if ev.key == pygame.K_3:
                        return int(speeds.get("fast", self.settings.get("fps")))
                    if ev.key == pygame.K_ESCAPE:
                        return None

            self.screen.fill(self.settings["colors"].get("bg", (0, 0, 0)))
            title = self.big.render("SNAKE", True, self.settings["colors"].get("snake", (0, 255, 0)))
            self.screen.blit(title, title.get_rect(center=(self.window_size[0] // 2, 120)))

            lines = [
                "Choose speed:",
                "1) Slow",
                "2) Normal",
                "3) Fast",
                "Esc) Quit"
            ]
            for i, line in enumerate(lines):
                txt = self.font.render(line, True, self.settings["colors"].get("food", (255, 255, 255)))
                self.screen.blit(txt, (self.window_size[0] // 2 - txt.get_width() // 2, 220 + i * 40))

            hint = self.font.render("Press 1/2/3 to select", True, (200, 200, 200))
            self.screen.blit(hint, hint.get_rect(center=(self.window_size[0] // 2, self.window_size[1] - 80)))

            pygame.display.flip()
            pygame.time.delay(50)