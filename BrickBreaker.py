import pygame
import random

pygame.init()
pygame.mixer.init() # Inisialisasi modul audio

# Dimensions of the screen
WIDTH, HEIGHT = 600, 500

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SOFT_PINK = (255, 182, 193)    
SOFT_BURGUNDY = (128, 55, 75)  

font = pygame.font.Font('freesansbold.ttf', 15)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Breaker with Sound & Timer")

# to control the frame rate
clock = pygame.time.Clock()
FPS = 50

# Fungsi untuk membuat efek suara sederhana (Beep) saat bola memantul/kena balok
def play_beep(frequency=440, duration=50):
    try:
        sample_rate = 22050
        num_samples = int(sample_rate * (duration / 1000.0))
        buffer = bytearray()
        for i in range(num_samples):
            value = int(127 + 127 * pygame.math.sin(2.0 * 3.14159 * frequency * i / sample_rate))
            buffer.append(value)
            buffer.append(value)
        sound = pygame.mixer.Sound(buffer=bytes(buffer))
        sound.set_volume(0.1)
        sound.play()
    except Exception:
        pass # Mencegah error jika audio device bermasalah

# Striker class
class Striker:
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx, self.posy = posx, posy
        self.width, self.height = width, height
        self.speed = speed
        self.color = color
        self.strikerRect = pygame.Rect(self.posx, self.posy, self.width, self.height)
        self.striker = pygame.draw.rect(screen, self.color, self.strikerRect)

    def display(self):
        self.striker = pygame.draw.rect(screen, self.color, self.strikerRect)

    def update(self, xFac):
        self.posx += self.speed * xFac
        if self.posx <= 0:
            self.posx = 0
        elif self.posx + self.width >= WIDTH:
            self.posx = WIDTH - self.width
        self.strikerRect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def getRect(self):
        return self.strikerRect

# Block Class
class Block:
    def __init__(self, posx, posy, width, height, color):
        self.posx, self.posy = posx, posy
        self.width, self.height = width, height
        self.color = color
        self.damage = 100
        
        # Soft Burgundy (2 kali pukul), Soft Pink (1 kali pukul)
        if color == SOFT_BURGUNDY:
            self.health = 200
        else:
            self.health = 100
            
        self.blockRect = pygame.Rect(self.posx, self.posy, self.width, self.height)
        self.block = pygame.draw.rect(screen, self.color, self.blockRect)

    def display(self):
        if self.health > 0:
            self.brick = pygame.draw.rect(screen, self.color, self.blockRect)

    def hit(self):
        self.health -= self.damage

    def getRect(self):
        return self.blockRect

    def getHealth(self):
        return self.health

# Ball Class
class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx, self.posy = posx, posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac, self.yFac = 1, 1
        self.ball = pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)

    def display(self):
        self.ball = pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        self.posx += self.xFac * self.speed
        self.posy += self.yFac * self.speed
        if self.posx <= 0 or self.posx >= WIDTH:
            self.xFac *= -1
            play_beep(300, 30) # Suara pantulan dinding
        if self.posy <= 0:
            self.yFac *= -1
            play_beep(300, 30) # Suara pantulan atas
        if self.posy >= HEIGHT:
            return True
        return False

    def reset(self):
        self.posx = 0
        self.posy = HEIGHT
        self.xFac, self.yFac = 1, -1

    def hit(self):
        self.yFac *= -1
        play_beep(500, 40) # Suara pantulan objek (papan/balok)

    def getRect(self):
        return self.ball

# Helper Functions
def collisionChecker(rect, ball):
    if pygame.Rect.colliderect(rect, ball):
        return True
    return False

def populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap):
    listOfBlocks = []
    for i in range(0, WIDTH, blockWidth + horizontalGap):
        for j in range(0, HEIGHT // 2, blockHeight + verticalGap):
            listOfBlocks.append(Block(i, j, blockWidth, blockHeight, random.choice([SOFT_PINK, SOFT_BURGUNDY])))
    return listOfBlocks

def gameOver():
    gameOver = True
    while gameOver:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True

# Game Manager
def main():
    running = True
    lives = 3
    score = 0
    
    # Timer 3 Menit (180.000 milidetik)
    TOTAL_TIME = 3 * 60 * 1000  
    start_ticks = pygame.time.get_ticks()

    scoreText = font.render("score", True, WHITE)
    scoreTextRect = scoreText.get_rect()
    scoreTextRect.center = (20, HEIGHT - 10)
    
    livesText = font.render("Lives", True, WHITE)
    livesTextRect = livesText.get_rect()
    livesTextRect.center = (120, HEIGHT - 10)
    
    striker = Striker(0, HEIGHT - 50, 100, 20, 10, WHITE)
    strikerXFac = 0
    ball = Ball(0, HEIGHT - 150, 7, 5, WHITE)
    
    blockWidth, blockHeight = 40, 15
    horizontalGap, verticalGap = 20, 20
    listOfBlocks = populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap)
    
    while running:
        screen.fill(BLACK)
        
        # Hitung Sisa Waktu
        elapsed_ticks = pygame.time.get_ticks() - start_ticks
        remaining_ticks = TOTAL_TIME - elapsed_ticks
        
        # Jika Waktu Habis (Timeout)
        if remaining_ticks <= 0:
            play_beep(150, 200) # Suara game over
            running = gameOver()
            start_ticks = pygame.time.get_ticks()
            lives = 3
            score = 0
            listOfBlocks = populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap)
            remaining_ticks = TOTAL_TIME

        # Format Teks Waktu
        seconds_left = max(0, remaining_ticks // 1000)
        minutes_display = seconds_left // 60
        seconds_display = seconds_left % 60
        time_str = f"Time: {minutes_display:02d}:{seconds_display:02d}"

        timeText = font.render(time_str, True, WHITE)
        timeTextRect = timeText.get_rect()
        timeTextRect.center = (220, HEIGHT - 10)

        screen.blit(scoreText, scoreTextRect)
        screen.blit(livesText, livesTextRect)
        screen.blit(timeText, timeTextRect)

        scoreText = font.render("Score : " + str(score), True, WHITE)
        livesText = font.render("Lives : " + str(lives), True, WHITE)
        
        if not listOfBlocks:
            listOfBlocks = populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap)
            
        if lives <= 0:
            play_beep(150, 200)
            running = gameOver()
            start_ticks = pygame.time.get_ticks()
            while listOfBlocks:
                listOfBlocks.pop(0)
            lives = 3
            score = 0
            listOfBlocks = populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    strikerXFac = -1
                if event.key == pygame.K_RIGHT:
                    strikerXFac = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    strikerXFac = 0
                    
        if collisionChecker(striker.getRect(), ball.getRect()):
            ball.hit()
            
        for block in listOfBlocks:
            if collisionChecker(block.getRect(), ball.getRect()):
                ball.hit()
                block.hit()
                if block.getHealth() <= 0:
                    listOfBlocks.pop(listOfBlocks.index(block))
                    score += 5
                    
        striker.update(strikerXFac)
        lifeLost = ball.update()
        if lifeLost:
            lives -= 1
            play_beep(200, 150) # Suara kehilangan nyawa
            ball.reset()
            
        striker.display()
        ball.display()
        for block in listOfBlocks:
            block.display()
            
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
    pygame.quit()