import pygame

WIDTH = 800
HEIGHT = 450
FPS = 30

# Define Colors 
COL_WHITE = (255, 255, 255)
COL_SKY = (247, 247, 237)
COL_WATER = (174, 208, 255)

## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Seajam')
clock = pygame.time.Clock()     ## For syncing the FPS

ship = pygame.transform.scale(pygame.image.load('source/seajam/Assets/ship.png'), (280, 160))


def draw():
    WIN.fill(COL_SKY)
    WIN.fill((0,0,0), pygame.Rect(0,0,WIDTH,1))
    WIN.blit(ship, (0, 0))
    WIN.fill((255, 255, 255, 60), pygame.Rect(0, 150, WIDTH, HEIGHT-150))

def main():
    running = True
    while running:
        clock.tick(FPS)     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw()
        pygame.display.flip()      

    pygame.quit()


if __name__ == '__main__':
    main()