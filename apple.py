import pygame
import os

class Apple(pygame.sprite.Sprite):
    def __init__(self, x, y, application_path, size=30):
        super().__init__()
        image_path = os.path.join(application_path, 'assets', 'apple.png')
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size * 1.5, size * 1.5))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)