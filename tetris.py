# tetris.py
import pygame
import random
import json
import os
from datetime import datetime

# Kolory i stałe
COLORS = [
    (0, 255, 255),    # I - cyjan
    (255, 165, 0),    # L - pomarańczowy
    (0, 0, 255),      # J - niebieski
    (255, 255, 0),    # O - żółty
    (0, 255, 0),      # S - zielony
    (255, 0, 0),      # Z - czerwony
    (128, 0, 128)     # T - fioletowy
]

SHAPES = [
    [[1, 1, 1, 1]],                 # I
    [[1, 0], [1, 0], [1, 1]],       # L
    [[0, 1], [0, 1], [1, 1]],       # J
    [[1, 1], [1, 1]],               # O
    [[0, 1, 1], [1, 1, 0]],         # S
    [[1, 1, 0], [0, 1, 1]],         # Z
    [[1, 1, 1], [0, 1, 0]]          # T
]

class Tetris:
    def __init__(self, width=10, height=20, block_size=35):
        pygame.init()
        self.width = width
        self.height = height
        self.block_size = block_size
        self.screen = pygame.display.set_mode((width*block_size+250, height*block_size))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        
        # Bezpieczne ładowanie czcionek
        try:
            self.font = pygame.font.SysFont('Arial', 30, bold=True)
            self.big_font = pygame.font.SysFont('Arial', 50, bold=True)
        except:
            self.font = pygame.font.Font(None, 30)
            self.big_font = pygame.font.Font(None, 50)
        
        # Plik wyników
        self.highscores_file = 'tetris_scores.json'
        self.highscores = self.load_highscores()
        
        # Inicjalizacja gry
        self.reset_game()
        
        # Zmienne stanu gry
        self.last_fall = pygame.time.get_ticks()
        self.last_move = {'left': 0, 'right': 0, 'rotate': 0}
        self.game_started = False
        self.paused = False
        self.game_over = False

    def reset_game(self):
        # Resetowanie stanu gry
        self.grid = [[0] * self.width for _ in range(self.height)]
        self.next_pieces = [self.create_new_piece() for _ in range(3)]
        self.current_piece = self.get_next_piece()
        self.score = 0
        self.normal_speed = 800
        self.fast_speed = 50
        self.game_over = False
        self.paused = False

    def load_highscores(self):
        try:
            if os.path.exists(self.highscores_file):
                with open(self.highscores_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'best_score': 0, 'last_scores': []}

    def save_highscores(self):
        try:
            with open(self.highscores_file, 'w') as f:
                json.dump(self.highscores, f)
        except Exception:
            pass

    def update_highscores(self):
        if self.score > self.highscores['best_score']:
            self.highscores['best_score'] = self.score
            
        self.highscores['last_scores'].append({
            'score': self.score,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        if len(self.highscores['last_scores']) > 3:
            self.highscores['last_scores'] = self.highscores['last_scores'][-3:]
        self.save_highscores()

    def create_new_piece(self):
        return {'shape': random.choice(SHAPES), 'color': random.choice(COLORS)}
    
    def get_next_piece(self):
        new_piece = self.next_pieces.pop(0)
        self.next_pieces.append(self.create_new_piece())
        return {
            'shape': new_piece['shape'],
            'color': new_piece['color'],
            'x': self.width//2 - len(new_piece['shape'][0])//2,
            'y': 0
        }

    def draw_grid_lines(self):
        for y in range(self.height):
            pygame.draw.line(self.screen, (50, 50, 50), 
                (0, y * self.block_size),
                (self.width * self.block_size, y * self.block_size))
        for x in range(self.width):
            pygame.draw.line(self.screen, (50, 50, 50),
                (x * self.block_size, 0),
                (x * self.block_size, self.height * self.block_size))

    def draw_block(self, x, y, color, offset_x=0, offset_y=0, size=None):
        size = size or self.block_size
        pygame.draw.rect(self.screen, color, (
            offset_x + x * size + 1,
            offset_y + y * size + 1,
            size - 2, size - 2
        ))

    def draw_sidebar(self):
        sidebar_x = self.width * self.block_size + 20
        pygame.draw.rect(self.screen, (40, 40, 40), (sidebar_x-10, 0, 240, self.height*self.block_size))
        
        # Punkty
        score_text = self.font.render(f'SCORE: {self.score}', True, (255,255,255))
        self.screen.blit(score_text, (sidebar_x, 50))
        
        # Następne klocki
        next_text = self.font.render('NEXT:', True, (255,255,255))
        self.screen.blit(next_text, (sidebar_x, 150))
        
        preview_size = self.block_size // 1.5
        for i, piece in enumerate(self.next_pieces[:3]):
            shape = piece['shape']
            color = piece['color']
            start_y = 200 + i * 130
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        self.draw_block(x+1, y, color, sidebar_x + 20, start_y, preview_size)

        # Najlepsze wyniki
        hs_text = self.font.render('BEST:', True, (255,255,255))
        self.screen.blit(hs_text, (sidebar_x, 500))
        best_score = self.font.render(str(self.highscores['best_score']), True, (255,215,0))
        self.screen.blit(best_score, (sidebar_x + 20, 540))
        
        # Ostatnie wyniki
        last_text = self.font.render('LAST 3:', True, (255,255,255))
        self.screen.blit(last_text, (sidebar_x, 600))
        for i, score_data in enumerate(reversed(self.highscores['last_scores'][:3])):
            try:
                score_text = self.font.render(f"{score_data['score']}", True, (200,200,200))
                self.screen.blit(score_text, (sidebar_x + 20, 640 + i*40))
            except:
                pass

    def draw_pause_screen(self):
        overlay = pygame.Surface((self.width*self.block_size, self.height*self.block_size), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        text = self.big_font.render('PAUSED', True, (255, 255, 0))
        text_rect = text.get_rect(center=(self.width*self.block_size//2, self.height*self.block_size//2))
        self.screen.blit(text, text_rect)

    def draw_start_screen(self):
        self.screen.fill((0, 0, 0))
        title = self.big_font.render('TETRIS', True, (255, 255, 255))
        controls = [
            "Controls:",
            "← → - Move",
            "↑ - Rotate",
            "↓ - Fast drop",
            "Space - Pause",
            "R - Restart",
            "Enter - Start"
        ]
        
        title_rect = title.get_rect(center=(self.width*self.block_size//2, 100))
        self.screen.blit(title, title_rect)
        
        for i, line in enumerate(controls):
            text = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (100, 200 + i*40))
        
        start_text = self.font.render('Press ENTER to start', True, (0, 255, 0))
        start_rect = start_text.get_rect(center=(self.width*self.block_size//2, 500))
        self.screen.blit(start_text, start_rect)
        pygame.display.update()

    def draw_game_over(self):
        overlay = pygame.Surface((self.width*self.block_size, self.height*self.block_size), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        text = self.big_font.render('GAME OVER!', True, (255, 0, 0))
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        restart_text = self.font.render('Press R to restart', True, (0, 255, 0))
        
        text_rect = text.get_rect(center=(self.width*self.block_size//2, self.height*self.block_size//2 - 50))
        score_rect = score_text.get_rect(center=(self.width*self.block_size//2, self.height*self.block_size//2 + 10))
        restart_rect = restart_text.get_rect(center=(self.width*self.block_size//2, self.height*self.block_size//2 + 80))
        
        self.screen.blit(text, text_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
        pygame.display.update()

    def draw(self):
        self.screen.fill((0,0,0))
        self.draw_grid_lines()
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]:
                    self.draw_block(x, y, self.grid[y][x])
        
        piece = self.current_piece
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_block(piece['x'] + x, piece['y'] + y, piece['color'])
        
        self.draw_sidebar()
        
        if self.paused:
            self.draw_pause_screen()
        
        pygame.display.update()

    def check_collision(self, piece, dx=0, dy=0):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x + dx
                    new_y = piece['y'] + y + dy
                    if (new_x < 0 or new_x >= self.width or
                        new_y >= self.height or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return True
        return False

    def rotate_piece(self):
        now = pygame.time.get_ticks()
        if now - self.last_move['rotate'] > 200:
            original_shape = self.current_piece['shape']
            self.current_piece['shape'] = [list(row) for row in zip(*reversed(original_shape))]
            if self.check_collision(self.current_piece):
                self.current_piece['shape'] = original_shape
            self.last_move['rotate'] = now

    def merge_piece(self):
        piece = self.current_piece
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[piece['y'] + y][piece['x'] + x] = piece['color']
        self.clear_lines()
        self.current_piece = self.get_next_piece()
        if self.check_collision(self.current_piece):
            self.game_over = True
            self.update_highscores()

    def clear_lines(self):
        lines_cleared = 0
        for y in range(self.height-1, -1, -1):
            if all(self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [0]*self.width)
                lines_cleared += 1
        if lines_cleared:
            self.score += lines_cleared * 100 * lines_cleared

    def handle_input(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        
        if keys[pygame.K_LEFT] and now - self.last_move['left'] > 100:
            if not self.check_collision(self.current_piece, dx=-1):
                self.current_piece['x'] -= 1
            self.last_move['left'] = now
                
        if keys[pygame.K_RIGHT] and now - self.last_move['right'] > 100:
            if not self.check_collision(self.current_piece, dx=1):
                self.current_piece['x'] += 1
            self.last_move['right'] = now
                
        if keys[pygame.K_UP]:
            self.rotate_piece()

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_started:
                        self.paused = not self.paused
                    if event.key == pygame.K_RETURN and not self.game_started:
                        self.game_started = True
                    if event.key == pygame.K_r and (self.game_over or self.paused):
                        self.reset_game()
            
            if not running:
                break
                
            if not self.game_started:
                self.draw_start_screen()
                continue
                
            if self.game_over:
                self.draw_game_over()
                continue
                
            if self.paused:
                self.draw()
                continue
                
            self.handle_input()
            
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                fall_speed = self.fast_speed
            else:
                fall_speed = self.normal_speed
                
            if pygame.time.get_ticks() - self.last_fall > fall_speed:
                if not self.check_collision(self.current_piece, dy=1):
                    self.current_piece['y'] += 1
                else:
                    self.merge_piece()
                self.last_fall = pygame.time.get_ticks()
            
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    game = Tetris(block_size=35)
    game.run()
