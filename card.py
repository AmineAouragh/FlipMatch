import pygame

pygame.init()

font = pygame.font.SysFont(None, 48)

class Card:

    def __init__(self, value, x, y, width=100, height=150):
        self.value = value
        self.rect = pygame.Rect(x, y, width, height)
        self.is_flipped = False
        self.is_matched = False

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=15)

        if self.is_flipped:
            text = font.render(str(self.value), True, (0, 0, 0))
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos) and not self.is_flipped and not self.is_matched:
            self.is_flipped = True
            return True
        return False