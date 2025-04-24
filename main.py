import pygame
from constants import *
from battle_loop import battle_mode



def main():
    pygame.init()
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    #eventually i'm going to need to pass some variables between the modes 
    #but for now this is certified good enough    

    battle_mode(screen)



#this goes last
if __name__ == "__main__":
    main()