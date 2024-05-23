# main.py

import pygame
import sys
import os
import random
from settings import WIDTH, HEIGHT, FPS, BACKGROUND_COLOR, PLAYER_SIZE
from player import Player
from apple import Apple
from button import Button

# Determine if the application is a frozen executable (PyInstaller bundle)
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('EQUISENSE')

# Set up font
font = pygame.font.SysFont(None, 36)
button_font = pygame.font.SysFont(None, 48)

# Load background image
background_path = os.path.join(application_path, 'assets', 'bg.jpeg')
background = pygame.image.load(background_path).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load sound files
sound_paths = {
    'sag': os.path.join(application_path, 'assets', 'sag.mp3'),
    'sol': os.path.join(application_path, 'assets', 'sol.mp3'),
    'yukari': os.path.join(application_path, 'assets', 'yukari.mp3'),
    'asagi': os.path.join(application_path, 'assets', 'asagi.mp3')
}
sounds = {key: pygame.mixer.Sound(path) for key, path in sound_paths.items()}

# Create clock object
clock = pygame.time.Clock()


# Function to create player and apple objects
def create_game_objects():
    player = Player(WIDTH // 2 - PLAYER_SIZE, HEIGHT // 2 - PLAYER_SIZE, application_path)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    apple_positions = [
        (PLAYER_SIZE // 2, HEIGHT // 2),  # Left corner
        (WIDTH // 2, PLAYER_SIZE // 2),  # Top-center
        (WIDTH // 2, HEIGHT - PLAYER_SIZE // 2),  # Bottom-center
        (WIDTH - PLAYER_SIZE // 2, HEIGHT // 2)  # Right-center
    ]
    apples = pygame.sprite.Group()
    for pos in apple_positions:
        apple = Apple(pos[0], pos[1], application_path)
        all_sprites.add(apple)
        apples.add(apple)

    apple_respawn_tracker = {pos: False for pos in apple_positions}

    return player, all_sprites, apples, apple_positions, apple_respawn_tracker


# Create initial game objects
player, all_sprites, apples, apple_positions, apple_respawn_tracker = create_game_objects()

# Initialize score
score = 0

# Game states
MENU = 'menu'
PLAYING = 'playing'
GAME_OVER = 'game_over'
game_state = MENU

# Create buttons
start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 100, 'BAŞLA', button_font, (0, 128, 0), (0, 255, 0))
restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 100, 'Yeniden Başla', button_font, (0, 128, 0), (0, 255, 0))

# Track target apple and direction changes
target_apple = None
last_direction = None


# Function to play directional sound
def play_directional_sound(player_pos, apple):
    direction = (apple.rect.centerx - player_pos[0], apple.rect.centery - player_pos[1])
    if abs(direction[0]) > abs(direction[1]):
        if direction[0] > 0:
            sounds['sag'].play()
        else:
            sounds['sol'].play()
    else:
        if direction[1] > 0:
            sounds['asagi'].play()
        else:
            sounds['yukari'].play()


# Function to choose a random apple target
def choose_random_apple(apples):
    return random.choice(apples.sprites())


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == MENU:
            if start_button.is_clicked(event):
                game_state = PLAYING
                target_apple = choose_random_apple(apples)
                play_directional_sound(player.rect.center, target_apple)

        elif game_state == GAME_OVER:
            if restart_button.is_clicked(event):
                player, all_sprites, apples, apple_positions, apple_respawn_tracker = create_game_objects()
                score = 0
                game_state = MENU

    if game_state == PLAYING:
        keys = pygame.key.get_pressed()
        moved = player.update(keys)

        # Determine the new direction
        if keys[pygame.K_LEFT]:
            new_direction = 'left'
        elif keys[pygame.K_RIGHT]:
            new_direction = 'right'
        elif keys[pygame.K_UP]:
            new_direction = 'up'
        elif keys[pygame.K_DOWN]:
            new_direction = 'down'
        else:
            new_direction = None

        # Play sound if direction changes
        if new_direction and new_direction != last_direction:
            play_directional_sound(player.rect.center, target_apple)
            last_direction = new_direction

        # Check if the player has deviated from the target apple
        if new_direction:
            apple_direction = (
            target_apple.rect.centerx - player.rect.centerx, target_apple.rect.centery - player.rect.centery)
            if abs(apple_direction[0]) > abs(apple_direction[1]):
                if apple_direction[0] > 0:
                    if new_direction != 'right':
                        play_directional_sound(player.rect.center, target_apple)
                else:
                    if new_direction != 'left':
                        play_directional_sound(player.rect.center, target_apple)
            else:
                if apple_direction[1] > 0:
                    if new_direction != 'down':
                        play_directional_sound(player.rect.center, target_apple)
                else:
                    if new_direction != 'up':
                        play_directional_sound(player.rect.center, target_apple)

        # Check for collisions between player and apples
        collided_apples = pygame.sprite.spritecollide(player, apples, True)
        for apple in collided_apples:
            apple_pos = (apple.rect.centerx, apple.rect.centery)
            apple_respawn_tracker[apple_pos] = True
            apple.kill()
            score += 1
            target_apple = choose_random_apple(apples)
            play_directional_sound(player.rect.center, target_apple)  # Play sound when apple is eaten

        # Check if player has moved away from the previous apple positions
        for pos, should_respawn in apple_respawn_tracker.items():
            if should_respawn:
                if abs(player.rect.centerx - pos[0]) > PLAYER_SIZE and abs(player.rect.centery - pos[1]) > PLAYER_SIZE:
                    new_apple = Apple(pos[0], pos[1], application_path)
                    all_sprites.add(new_apple)
                    apples.add(new_apple)
                    apple_respawn_tracker[pos] = False

        if score >= 50:
            game_state = GAME_OVER

    if game_state == MENU:
        # Draw the background
        screen.blit(background, (0, 0))

        # Draw the start button
        start_button.draw(screen)

    elif game_state == PLAYING:
        # Draw the background
        screen.blit(background, (0, 0))

        # Draw all sprites
        all_sprites.draw(screen)

        # Draw square around the target apple
        if target_apple:
            pygame.draw.rect(screen, (255, 0, 0), target_apple.rect, 2)

        # Render the score
        score_text = font.render(f'Score: {score} / 50 ELMA', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

    elif game_state == GAME_OVER:
        # Draw the background
        screen.blit(background, (0, 0))

        # Draw the game over text
        game_over_text = button_font.render('Oyun Bitti', True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

        # Draw the restart button
        restart_button.draw(screen)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()
