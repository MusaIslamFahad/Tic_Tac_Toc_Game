import pygame
import sys
import numpy as np

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (50, 200, 50)
BUTTON_HOVER_COLOR = (70, 220, 70)
END_BUTTON_COLOR = (200, 50, 50) # Red for End Game button
END_BUTTON_HOVER_COLOR = (220, 70, 70)
DIFFICULTY_BUTTON_COLOR = (80, 80, 200) # Blue for difficulty buttons
DIFFICULTY_BUTTON_HOVER_COLOR = (100, 100, 220)

# --- Pygame Setup ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe')
screen.fill(BG_COLOR)

# Fonts
font_large = pygame.font.Font(None, 80) # Font for titles
font_medium = pygame.font.Font(None, 60) # Font for messages and main buttons
font_small = pygame.font.Font(None, 40) # Font for other text, including difficulty buttons

# Sound
try:
    pygame.mixer.init() # Ensure mixer is initialized, although pygame.init() usually covers it
    click_sound = pygame.mixer.Sound('click_sound.wav') # Load your sound file here
except pygame.error as e:
    print(f"Could not load sound file: {e}")
    click_sound = None # Set to None if sound file isn't found

# Game Board
board = np.zeros((BOARD_ROWS, BOARD_COLS))

# AI Difficulty - Now a global variable to be changed by user selection
difficulty = "medium"  # Default AI difficulty level

# --- Game Functions ---

def draw_lines():
    for row in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, row * SQUARE_SIZE), (WIDTH, row * SQUARE_SIZE), LINE_WIDTH)
    for col in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_COLOR, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:
                pygame.draw.circle(screen, CIRCLE_COLOR,
                                   (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2)),
                                   CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 2:
                pygame.draw.line(screen, CROSS_COLOR,
                                 (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR,
                                 (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                                 CROSS_WIDTH)

def mark_square(row, col, player):
    board[row][col] = player

def available_square(row, col):
    return board[row][col] == 0

def is_board_full():
    return np.all(board != 0)

def check_win(player):
    for row in range(BOARD_ROWS):
        if np.all(board[row, :] == player):
            return True
    for col in range(BOARD_COLS):
        if np.all(board[:, col] == player):
            return True
    if board[0, 0] == player and board[1, 1] == player and board[2, 2] == player:
        return True
    if board[0, 2] == player and board[1, 1] == player and board[2, 0] == player:
        return True
    return False

# MODIFIED: Removed pygame.display.update() from this function
def display_message(message, font_type=font_small):
    text = font_type.render(message, True, TEXT_COLOR)
    # Adjust position slightly for better visual flow with buttons below
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)) # Moved up slightly
    screen.blit(text, text_rect)
    # pygame.display.update() # REMOVED

# Minimax algorithm with difficulty levels
def minimax(board, depth, is_maximizing):
    if check_win(2):  # AI win
        return 1
    elif check_win(1):  # Player win
        return -1
    elif is_board_full():
        return 0

    if is_maximizing:
        best_score = -np.inf
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if available_square(row, col):
                    board[row][col] = 2
                    score = minimax(board, depth + 1, False)
                    board[row][col] = 0
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = np.inf
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if available_square(row, col):
                    board[row][col] = 1
                    score = minimax(board, depth + 1, True)
                    board[row][col] = 0
                    best_score = min(score, best_score)
        return best_score

# AI Move based on difficulty level
def ai_move():
    best_score = -np.inf
    move = None
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if available_square(row, col):
                board[row][col] = 2
                score = minimax(board, 0, False)
                board[row][col] = 0
                if score > best_score:
                    best_score = score
                    move = (row, col)
    
    if move:
        mark_square(move[0], move[1], 2)

# Easy AI move: choose a random available square
def easy_ai_move():
    available_moves = [(row, col) for row in range(BOARD_ROWS) for col in range(BOARD_COLS) if available_square(row, col)]
    if available_moves:
        move = available_moves[np.random.randint(len(available_moves))]
        mark_square(move[0], move[1], 2)

def restart():
    screen.fill(BG_COLOR)
    draw_lines()
    global board, game_over, player
    board = np.zeros((BOARD_ROWS, BOARD_COLS))
    game_over = False
    player = 1

def draw_button(text, x, y, w, h, inactive_color, active_color, font, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    button_rect = pygame.Rect(x, y, w, h)

    if button_rect.collidepoint(mouse):
        pygame.draw.rect(screen, active_color, button_rect)
        if click[0] == 1 and action is not None:
            if click_sound: # Play sound if loaded
                click_sound.play()
            pygame.time.wait(200) # Small delay to prevent multiple clicks
            action()
            return True # Indicate that the button was clicked
    else:
        pygame.draw.rect(screen, inactive_color, button_rect)

    text_surf = font.render(text, True, TEXT_COLOR) # Use the passed font
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    return False # Indicate that the button was not clicked

# --- New functions to set difficulty ---
def set_difficulty_easy():
    global difficulty
    difficulty = "easy"
    # print(f"Difficulty set to: {difficulty}") # For debugging/confirmation

def set_difficulty_medium():
    global difficulty
    difficulty = "medium"
    # print(f"Difficulty set to: {difficulty}") # For debugging/confirmation

def set_difficulty_hard():
    global difficulty
    difficulty = "hard"
    # print(f"Difficulty set to: {difficulty}") # For debugging/confirmation

def draw_landing_page():
    screen.fill(BG_COLOR)
    title_text = font_large.render("TIC TAC TOE", True, TEXT_COLOR)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    # Display current difficulty
    difficulty_text = font_small.render(f"Difficulty: {difficulty.upper()}", True, TEXT_COLOR)
    difficulty_text_rect = difficulty_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
    screen.blit(difficulty_text, difficulty_text_rect)

    # Difficulty Buttons
    button_width = 150
    button_height = 50
    button_spacing = 10
    total_buttons_width = (button_width * 3) + (button_spacing * 2)
    start_x = (WIDTH - total_buttons_width) // 2
    button_y = HEIGHT // 2 - 20

    # Pass font_small for difficulty buttons
    draw_button("EASY", start_x, button_y, button_width, button_height, DIFFICULTY_BUTTON_COLOR, DIFFICULTY_BUTTON_HOVER_COLOR, font_small, set_difficulty_easy)
    draw_button("MEDIUM", start_x + button_width + button_spacing, button_y, button_width, button_height, DIFFICULTY_BUTTON_COLOR, DIFFICULTY_BUTTON_HOVER_COLOR, font_small, set_difficulty_medium)
    draw_button("HARD", start_x + (button_width + button_spacing) * 2, button_y, button_width, button_height, DIFFICULTY_BUTTON_COLOR, DIFFICULTY_BUTTON_HOVER_COLOR, font_small, set_difficulty_hard)

    # Start Button
    start_button_x = (WIDTH // 2) - 100
    start_button_y = button_y + button_height + 40 # Position below difficulty buttons
    draw_button("START", start_button_x, start_button_y, 200, 70, BUTTON_COLOR, BUTTON_HOVER_COLOR, font_medium, start_game)

    # End Game Button (on landing page)
    end_button_x = (WIDTH // 2) - 125
    end_button_y = start_button_y + 90 # Position below Start button
    draw_button("END GAME", end_button_x, end_button_y, 250, 70, END_BUTTON_COLOR, END_BUTTON_HOVER_COLOR, font_medium, end_game)
    
    pygame.display.update()

# MODIFIED: Adjusted button positions and ensures single update
def draw_game_over_page(message):
    screen.fill(BG_COLOR) # Clear the screen first
    
    # Display message (now only draws, doesn't update)
    display_message(message, font_medium)

    # Play Again Button - Adjusted position
    play_again_button_x = (WIDTH // 2) - 150
    play_again_button_y = (HEIGHT // 2) + 20 # Moved up
    draw_button("PLAY AGAIN", play_again_button_x, play_again_button_y, 300, 70, BUTTON_COLOR, BUTTON_HOVER_COLOR, font_medium, play_again)

    # End Game Button - Adjusted position
    end_button_x = (WIDTH // 2) - 125
    end_button_y = play_again_button_y + 90 # Position below Play Again button
    draw_button("END GAME", end_button_x, end_button_y, 250, 70, END_BUTTON_COLOR, END_BUTTON_HOVER_COLOR, font_medium, end_game)
    
    pygame.display.update() # Only update once after all drawing is done

def start_game():
    global game_state
    game_state = "playing"
    restart() # Initialize board and game state for playing

def play_again():
    global game_state
    game_state = "playing"
    restart()

def end_game():
    pygame.quit()
    sys.exit()

# --- Game Loop Variables ---
player = 1  # Player 1 is human
game_over = False
game_state = "landing" # "landing", "playing", "game_over"
winner_message = ""
AI_THINK_TIME = 200 # AI thinking time in milliseconds

# --- Main Game Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "landing":
            pass # Buttons are handled by their draw_button calls

        elif game_state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouseX = event.pos[0]  # X coordinate
                mouseY = event.pos[1]  # Y coordinate

                clicked_row = mouseY // SQUARE_SIZE
                clicked_col = mouseX // SQUARE_SIZE

                if available_square(clicked_row, clicked_col):
                    mark_square(clicked_row, clicked_col, player)
                    if click_sound: # Play sound for marking a square
                        click_sound.play()
                    if check_win(player):
                        winner_message = "Player Wins!"
                        game_over = True
                    player = 2 # Switch to AI player

            if player == 2 and not game_over:
                pygame.time.wait(AI_THINK_TIME) 
                if difficulty == "easy":
                    easy_ai_move()
                else: # For "medium" and "hard", use the minimax-based AI
                    ai_move()
                
                if click_sound: # Play sound for AI marking a square
                    click_sound.play()
                
                if check_win(2):
                    winner_message = "AI Wins!"
                    game_over = True
                player = 1 # Switch back to human player

            if is_board_full() and not game_over:
                winner_message = "It's a Draw!"
                game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart()

        elif game_state == "game_over":
            pass # Buttons are handled by their draw_button calls


    # --- Drawing Logic based on game_state ---
    if game_state == "landing":
        draw_landing_page()
    elif game_state == "playing":
        if game_over:
            game_state = "game_over" # Transition to game_over state
        else:
            screen.fill(BG_COLOR)
            draw_lines()
            draw_figures()
            pygame.display.update()
    elif game_state == "game_over":
        draw_game_over_page(winner_message) # This function now handles clearing and updating
    
     
    
     
       
    

    

