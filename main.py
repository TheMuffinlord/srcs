import pygame
from constants import *
from playerunits import *
from enemies import *

def kbd_interpreter(pressed_key, selected_units, unit_group):
    toggle_unit = 0
    match(pressed_key):
        case pygame.K_1:
            toggle_unit = 1
        case pygame.K_2:
            toggle_unit = 2
    for unit in unit_group:
        if unit.unit_number == toggle_unit:
            selected_units = toggle_selection(selected_units, unit)
        

def toggle_selection(selected_units, unit):
    if selected_units.has(unit):
        print(f"removing {unit.name} from selected units")
        selected_units.remove(unit)
        unit.selected = False
    else:
        print(f"adding {unit.name} to selected units")
        selected_units.add(unit)
        unit.selected = True
    


def mouse_interpreter(clicked_position, clicked_button, selected_units):
    if clicked_button[0] or clicked_button[1]:
        for unit in selected_units:
            unit.destination = RootObject(clicked_position[0], clicked_position[1], 30)
            print(f"setting {unit.name} destination to {unit.destination.position}")



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
    SelectionGroup = pygame.sprite.Group()

    PlayerRobot.containers = (loop_updatable, loop_drawable, PlayerGroup)
    EnemyUnit.containers = (loop_updatable, loop_drawable, EnemyGroup)
    BasicBullet.containers = (loop_updatable, loop_drawable, BulletGroup)
    EnemySpawner.containers = (loop_updatable, loop_drawable, EnemyGroup)


    Player = PlayerRobot(250, 300, "john character", 1)
    Player2 = PlayerRobot(100, 650, "jane character", 2)
    
    Spawner = EnemySpawner(900, 500)
    Spawner2 = EnemySpawner(900, 200)

    action_waiting = False
    kbd_waiting = False
    mouse_waiting = False
    
    game_running = True


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
                clicked_button = pygame.mouse.get_pressed()
                print(f"clicked at {clicked_location}")
                action_waiting = True
                mouse_waiting = True
                if kbd_waiting == True:
                    print("mouse overriding keyboard")
                    kbd_waiting = False
            if action_waiting == True:
                print("action caught")
                if mouse_waiting == True:
                    mouse_interpreter(clicked_location, clicked_button, SelectionGroup)
                    action_waiting = False
                    mouse_waiting = False
                elif kbd_waiting == True:
                    kbd_interpreter(pressed_key, SelectionGroup, PlayerGroup)
                    action_waiting = False
                    kbd_waiting = False
                else: 
                    action_waiting = False
                    print("some other action took place?")

        pygame.Surface.fill(screen, "black")
        for item in loop_updatable:
            if isinstance(item, PlayerRobot):
                item.update(dt, EnemyGroup)
            elif isinstance(item, EnemyUnit) or isinstance(item, EnemySpawner):
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