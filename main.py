import pygame
import sys
import random
import time
import sqlite3
from datetime import datetime
from card import Card

pygame.init()

conn = sqlite3.connect("scores.db")
cursor = conn.cursor()

cursor.execute("""
  CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER,
    time_taken TEXT,
    date_played TEXT
  )
""")

conn.commit()

start_time = time.time()

screen_w, screen_h = 1200, 920

screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption("Card Flip Game")

font = pygame.font.SysFont(None, 48)

clock = pygame.time.Clock()

card_values = [i for i in range(1, 11)] * 2
random.shuffle(card_values)

cards = []
START_X, START_Y = 280, 150
GAP = 40
CARD_W, CARD_H = 100, 150

ROWS, COLS = 4, 5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

for row in range(ROWS):
    for col in range(COLS):
        # idx = 0 * 2 + 0
        # idx = 0 * 2 + 1
        # idx = 0 * 2 + 2
        # ...............
        # idx = 1 * 2 + 0
        idx = row * COLS + col
        value = card_values[idx]
        # x = 100 + 0 * (100 + 40)
        # x = 100 + 1 * (140)
        x = START_X + col * (CARD_W + GAP)
        y = START_Y + row * (CARD_H + GAP)
        cards.append(Card(value, x, y))

flipped_cards = []
flip_back_time = 0
num_matches = 0
player_score = 0
game_over = False
final_time = None
date_played = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

score_saved = False

save_button_clicked = False

popup_state = None
restart_button = None

# Popup
box_width, box_height = 800, 400
box_x = (screen_w - box_width) // 2
box_y = (screen_h - box_height) // 2

running = True

while running:

    screen.fill((30, 30, 30))

    now = pygame.time.get_ticks()

    # Draw cards
    for card in cards:
        card.draw(screen)

    # Draw score
    score_text = f"Score: {player_score}"
    score_surface = font.render(score_text, True, (200, 200, 200))
    score_pos = (screen_w - score_surface.get_width() - 700, screen_h - score_surface.get_height() - 820)
    screen.blit(score_surface, score_pos)

    # Draw timer
    if not game_over:
        elapsed_time = int(time.time() - start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        timer_text = f"Time: {minutes:02}:{seconds:02}"
        timer_surface = font.render(timer_text, True, (200, 200, 200))
        time_pos = (screen_w - timer_surface.get_width() - 330, screen_h - timer_surface.get_height() - 820)
        screen.blit(timer_surface, time_pos)

    # Handle matched cards
    if len(flipped_cards) == 2:
        card1, card2 = flipped_cards
        if card1.value == card2.value:
            card1.is_matched = True
            card2.is_matched = True
            num_matches += 1
            player_score += 2

        else:
            card1.is_flipped = False
            card2.is_flipped = False
            # Set timer to flip back after 1 second
            if flip_back_time == 0:
                flip_back_time = now + 1000
        flipped_cards = []

    if flip_back_time != 0 and now >= flip_back_time:
        for card in flipped_cards:
            card.is_flipped = False
        flipped_cards = []
        flip_back_time = 0

    if not game_over and num_matches == len(cards) // 2:
        game_over = True
        final_time = elapsed_time
        date_played = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        popup_state = "save_prompt"

    # Popup
    if game_over:

        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(180)  # Transparency
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=15)

        if popup_state == "save_prompt":
            # Text
            message = f"Congratulations!\n\nYou found all matches in {elapsed_time // 60}min{elapsed_time % 60:02}s."
            lines = message.split("\n")
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(screen_w // 2, box_y + 100 + i * 30))
                screen.blit(text_surface, text_rect)

            # Save button
            save_button = pygame.Rect(screen_w // 2 - 90, box_y + 260, 180, 80)
            pygame.draw.rect(screen, (100, 200, 100), save_button, border_radius=8)
            save_button_text = font.render("Save", True, (255, 255, 255))
            button_text_rect = save_button_text.get_rect(center=save_button.center)

            screen.blit(save_button_text, button_text_rect)

        elif popup_state == "saved":

            # Text
            message = f"Score saved!\n\nWanna try again?"
            lines = message.split("\n")
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(screen_w // 2, box_y + 100 + i * 30))
                screen.blit(text_surface, text_rect)

            # Save button
            restart_button = pygame.Rect(screen_w // 2 - 90, box_y + 260, 180, 80)
            pygame.draw.rect(screen, (100, 200, 100), restart_button, border_radius=8)
            restart_button_text = font.render("Retry", True, (255, 255, 255))
            button_text_rect = restart_button_text.get_rect(center=restart_button.center)
            screen.blit(restart_button_text, button_text_rect)

    # Event handling
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if game_over and popup_state == "save_prompt":
                if save_button.collidepoint(event.pos) and not score_saved:
                    conn.execute("INSERT INTO scores (score, time_taken, date_played) VALUES (?,?,?) ",
                                 (player_score, elapsed_time, date_played))
                    conn.commit()
                    conn.close()
                    score_saved = True
                    popup_state = "saved"

            elif game_over and popup_state == "saved":
                if restart_button.collidepoint(event.pos):
                    # Reset game state
                    card_values = [i for i in range(1, 11)] * 2
                    random.shuffle(card_values)
                    cards = []
                    for row in range(ROWS):
                        for col in range(COLS):
                            idx = row * COLS + col
                            value = card_values[idx]
                            x = START_X + col * (CARD_W + GAP)
                            y = START_Y + row * (CARD_H + GAP)
                            cards.append(Card(value, x, y))
                    flipped_cards = []
                    flip_back_time = 0
                    num_matches = 0
                    player_score = 0
                    game_over = False
                    score_saved = False
                    popup_state = None
                    start_time = time.time()
                    conn = sqlite3.connect('scores.db')

            else:

                for card in cards:
                    if len(flipped_cards) < 2 and card.handle_click(event.pos):
                        flipped_cards.append(card)
                        flip_back_time = time.time()
                        break

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()