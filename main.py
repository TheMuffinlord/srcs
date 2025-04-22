import pygame
from constants import *
from playerunits import *
from enemies import *

def kbd_interpreter(pressed_key, selected_units):
    pass

def mouse_interpreter(clicked_position, clicked_button, selected_units):
    pass

def main():
    pygame.init()
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    

    battle_mode(screen)

def battle_mode(screen):
    clock = pygame.time.Clock()
    dt = 0

    #create the map, populate with units

    loop_updatable = pygame.sprite.Group()
    loop_drawable = pygame.sprite.Group()
    EnemyGroup = pygame.sprite.Group()
    PlayerGroup = pygame.sprite.Group()
    BulletGroup = pygame.sprite.Group()

    PlayerRobot.containers = (loop_updatable, loop_drawable, PlayerGroup)
    EnemyUnit.containers = (loop_updatable, loop_drawable, EnemyGroup)
    BasicBullet.containers = (loop_updatable, loop_drawable, BulletGroup)
    EnemySpawner.containers = (loop_updatable, loop_drawable, EnemyGroup)


    Player = PlayerRobot(250, 300, "john character")
    Enemy = EnemyUnit(750, 400)
    Spawner = EnemySpawner(700, 500)

    action_waiting = False
    kbd_waiting = False
    mouse_waiting = False
    
    game_running = True
    selected_units = []

    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN: #going to have to put mouse logic in ehre too
                pressed_key = event.key
                action_waiting = True
                kbd_waiting = True
                if mouse_waiting == True:
                    print("keyboard overriding mouse") #good enough for debug!
                    mouse_waiting = False
                if pressed_key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #targeting logic, break out
                clicked_location = pygame.mouse.get_pos()
                clicked_button = event.type
                print(f"clicked at {clicked_location}")
                action_waiting = True
                mouse_waiting = True
                if kbd_waiting == True:
                    print("mouse overriding keyboard")
                    kbd_waiting = False
            if action_waiting == True:
                print("action caught")
                if mouse_waiting == True:
                    mouse_interpreter(clicked_location, clicked_button, selected_units)
                    action_waiting = False
                    mouse_waiting = False
                elif kbd_waiting == True:
                    kbd_interpreter(pressed_key, selected_units)
                    action_waiting = False
                    kbd_waiting = False
                else: 
                    action_waiting = False
                    print("some other action took place?")

        pygame.Surface.fill(screen, "black")
        for item in loop_updatable:
            if PlayerGroup in item.groups():
                item.update(dt, EnemyGroup)
            elif EnemyGroup in item.groups():
                item.update(dt, PlayerGroup, BulletGroup)
            else:
                item.update(dt)
        
        for item in loop_drawable:
            item.c_bounds = item.draw(screen)    

        pygame.display.flip()
        dt = clock.tick(60)/1000      

#this goes last
if __name__ == "__main__":
    main()