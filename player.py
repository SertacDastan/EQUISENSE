import pygame
import os
from settings import PLAYER_SIZE, PLAYER_SPEED, WIDTH, HEIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, application_path):
        super().__init__()
        self.application_path = application_path
        self.image_right = pygame.image.load(os.path.join(application_path, 'assets', 'rabbit.png')).convert_alpha()
        self.image_right = pygame.transform.scale(self.image_right, (PLAYER_SIZE * 2, PLAYER_SIZE * 2))
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = PLAYER_SPEED
        self.last_direction = 'right'

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.last_direction != 'left':
                self.image = self.image_left
                self.last_direction = 'left'
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.last_direction != 'right':
                self.image = self.image_right
                self.last_direction = 'right'
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Keep player within screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
