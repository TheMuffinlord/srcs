import pygame
#import pygamepal as pgp  # maybe later, pygame pal
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from battle_loop import battle_mode



def main():
    pygame.init()
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    window = pygame.window.Window("shitty robot clone squad", size=(SCREEN_WIDTH, SCREEN_HEIGHT), resizable=False)
    screen = window.get_surface()

    #eventually i'm going to need to pass some variables between the modes 
    #but for now this is certified good enough    
    Waiting_On_Space = True
    while Waiting_On_Space:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                Waiting_On_Space = False

    battle_mode(window, screen)

if __name__ == "__main__":
    main()

'''game_size = (SCREEN_WIDTH, SCREEN_HEIGHT)

srcs_main = pgp.Game(size=game_size, caption="this space for rent", fps=60, fullscreen=False)

class title_screen(pgp.Scene):
    def init(self):
        self.backgroundColor = "black"

    def update(self):
        if self.game.input.isKeyPressed(pygame.K_SPACE):
            self.game.quit()

    def draw(self):
        pgp.drawText(self.overlaySurface, "if this works press space", position=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2), color="red", backgroundColor="blue")

#this goes last
title = title_screen(srcs_main)
srcs_main.currentScene = title
srcs_main.run()'''