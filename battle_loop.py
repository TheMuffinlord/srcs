import pygame, math, random
#import pygamepal as pgp # if i can break off some of these into their own thing, might be useful
from constants import SELECTION_RADIUS, SELECTION_DECAY_TIMER, SCREEN_HEIGHT, SCREEN_WIDTH
from enum import Enum
from rootobject import RootObject, PingObject
from playerunit import PlayerRobot
from enemies import EnemyUnit, EnemySpawner
from equipment import BasicBullet, BasicLaser, Particle
from textboxes import *
from mapgen import Obstacle, GroundTile, tmx_generator



'''def kbd_interpreter(pressed_key):
    global PlayerGroup, offset_y, offset_x, screenmax_y, screenmax_x
    toggle_unit = 0
    match(pressed_key):
        case pygame.K_1:
            toggle_unit = 1
        case pygame.K_2:
            toggle_unit = 2
        case pygame.K_w:
            if offset_y <= -50:
                offset_y += 50
                print(f"y offset now {offset_y}")
        case pygame.K_s:
            if offset_y >= (-1 * screenmax_y) + 50:
                offset_y -= 50
                print(f"y offset now {offset_y}")
        case pygame.K_a:
            if offset_x <= -50:
                offset_x += 50
                print(f"x offset now {offset_x}")
        case pygame.K_d:
            if offset_x >= (-1 * screenmax_x) + 50:
                offset_x -= 50
                print(f"x offset now {offset_x}")
    for unit in PlayerGroup:
        if unit.unit_number == toggle_unit:
            toggle_selection(unit)'''
        

def toggle_selection(unit):
    global SelectionGroup
    if SelectionGroup.has(unit):
        print(f"removing {unit.name} from selected units")
        SelectionGroup.remove(unit)
        unit.selected = False
    else:
        print(f"adding {unit.name} to selected units")
        SelectionGroup.add(unit)
        unit.selected = True
    
'''def mouse_interpreter(clicked_position, clicked_button):
    global SelectionGroup, offset_x, offset_y
    if clicked_button[0] or clicked_button[1]:
        go_here = SelectionCursor(clicked_position[0] + (-1 * offset_x), clicked_position[1] + (-1 * offset_y))
        for unit in SelectionGroup:
            unit.destination = go_here
            print(f"setting {unit.name} destination to {unit.destination.position}")
            toggle_selection(unit)    '''    

# classes go in here



class SelectionCursor(RootObject): #selection cursor. should move these to other modules but would need to pass groups better
    def __init__(self, x, y):
        super().__init__(x, y, SELECTION_RADIUS)
        self.color = pygame.color.Color(0,255,0)
        global SelectionGroup
        self.selected_units = SelectionGroup.copy()
        self.in_use = True
        
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius, 3)

    def update(self, *args):
        if self.color.g > 0:
            self.color.g -= 5 #fades to black. when backgrounds are in, change this to alpha?
        if self.color.g <= 0:
            if self.color.r < 250:
                self.color.r += 5 #makes it red if it runs out of green
            self.in_use = False
        for unit in self.selected_units:
            if unit.collision(self):
                self.selected_units.remove(unit)
                unit.destination = None
            if unit.destination == self:
                self.in_use = True
        if self.in_use == False:
            self.kill()
        
# main battle loop

def battle_mode(screen):
    #create the map, populate with units

    loop_updatable = pygame.sprite.Group()
    loop_drawable = pygame.sprite.Group()
    global EnemyGroup, PlayerGroup, BulletGroup, SelectionGroup
    EnemyGroup = pygame.sprite.Group()
    PlayerGroup = pygame.sprite.Group()
    BulletGroup = pygame.sprite.Group()
    SelectionGroup = pygame.sprite.Group()

    

    PlayerRobot.containers = (loop_updatable, loop_drawable, PlayerGroup)
    EnemyUnit.containers = (loop_updatable, loop_drawable, EnemyGroup)
    BasicBullet.containers = (loop_updatable, loop_drawable, BulletGroup)
    BasicLaser.containers = (loop_drawable, loop_updatable, BulletGroup)
    EnemySpawner.containers = (loop_updatable, loop_drawable, EnemyGroup)
    SelectionCursor.containers = (loop_updatable, loop_drawable, SelectionGroup)
    TextBoxObject.containers = (loop_updatable, loop_drawable)
    Particle.containers = (loop_drawable, loop_updatable)
    PingObject.containers = (loop_drawable, loop_updatable)
    GroundTile.containers = (loop_drawable)

    #Player = PlayerRobot(250, 300, "john character", 1)
    #Player2 = PlayerRobot(250, 650, "jane character", 2)
    # TIME TO CODE A REALLY BASIC SPAWNER
    
    clock = pygame.time.Clock()
    dt = 0
    battle_map = tmx_generator("maps/testmap_01.tmx")
    global offset_x, offset_y, screenmax_x, screenmax_y #love too declare globals
    offset_x = 0 #these work backwards. make sure to invert when adding to things!
    offset_y = 0 #not sure if i can explain why it's like that. you're pushing the camera around basically
    screenmax_x = battle_map["mapsize_x"]
    screenmax_y = battle_map["mapsize_y"]
    playable_area = pygame.surface.Surface((screenmax_x, screenmax_y))

    playerlist = DEFAULT_PLAYERLIST
    p_s_x = battle_map["spawn"][0]
    p_s_y = battle_map["spawn"][1]
    squad = []
    for unit in playerlist:
        print(unit)
        playerunit = PlayerRobot(p_s_x, p_s_y, unit["name"], unit["number"])
        playerunit.equipment = unit["equipment"]
        squad.append(playerunit)
        if p_s_x == battle_map["spawn"][0]:
            p_s_x += 50
        else:
            p_s_x = battle_map["spawn"][0]
            p_s_y += 50
            
    

    Spawner = EnemySpawner(1200, 1250)
    Spawner2 = EnemySpawner(1250, 1200)

    #action_waiting = False
    #kbd_waiting = False
    #mouse_waiting = False
    
    game_running = True
    moving_up = False
    moving_down = False
    moving_left = False
    moving_right = False
    toggle_unit = None

    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                if event.key == pygame.K_1:
                    toggle_unit = 1
                if event.key == pygame.K_2:
                    toggle_unit = 2
                if event.key == pygame.K_3:
                    toggle_unit = 3
                if event.key == pygame.K_4:
                    toggle_unit = 4
                if event.key == pygame.K_5:
                    toggle_unit = 5
                if event.key == pygame.K_6:
                    toggle_unit = 6
                #extend these for further units. maybe pass just this part to its own class, with a list of the player units?
                if toggle_unit:
                    for unit in PlayerGroup:
                        if unit.unit_number == toggle_unit and unit.alive():
                            toggle_selection(unit)
                        
                    toggle_unit = None
                if event.key == pygame.K_w: #up
                    moving_up = True
                if event.key == pygame.K_a: #left
                    moving_left = True
                if event.key == pygame.K_s: #down
                    moving_down = True
                if event.key == pygame.K_d: #right
                    moving_right = True
                if event.key == pygame.K_z: #dump offsets
                    print(f"camera offsets: ({offset_x, offset_y}), screen edges should be (0, 0), ({screenmax_x * -1 + SCREEN_WIDTH}, {screenmax_y * -1 + SCREEN_HEIGHT})")
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    moving_up = False
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_s:
                    moving_down = False
                if event.key == pygame.K_d:
                    moving_right = False
            if event.type == pygame.MOUSEBUTTONDOWN: #good enough for now!
                clicked_location = pygame.mouse.get_pos()
                clicked_button = pygame.mouse.get_pressed()
                if clicked_button[0] or clicked_button[1]:
                    go_here = SelectionCursor(clicked_location[0] + (-1 * offset_x), clicked_location[1] + (-1 * offset_y))
                    if clicked_button[0]:
                        for unit in SelectionGroup:
                            #unit.destination.append(go_here.position.xy)
                            if isinstance(unit, PlayerRobot):
                                unit.find_a_path(battle_map, go_here)
                            toggle_selection(unit)
                    elif clicked_button[1]:
                        #dunno what this button will do
                        pass

        #state checkers for camera movement                    
        if moving_left == True:
            if offset_x < 3:
                offset_x += 3
        if moving_up == True:
            if offset_y < 3:
                offset_y += 3
        if moving_down == True:
            if offset_y > (screenmax_y * -1) + SCREEN_HEIGHT:
                offset_y -= 3
        if moving_right == True:
            if offset_x > (screenmax_x * -1) + SCREEN_WIDTH:
                offset_x -= 3
            '''elif event.type == pygame.KEYDOWN: #going to have to put mouse logic in ehre too
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
                    mouse_interpreter(clicked_location, clicked_button)
                    action_waiting = False
                    mouse_waiting = False
                elif kbd_waiting == True:
                    kbd_interpreter(pressed_key)
                    action_waiting = False
                    kbd_waiting = False
                else: 
                    action_waiting = False
                    print("some other action took place?")'''

        #pygame.Surface.fill(playable_area, "purple")

        for item in loop_updatable:
            if item in PlayerGroup:
                item.update(dt, EnemyGroup, playable_area, battle_map)
            elif item in EnemyGroup:
                item.update(dt, PlayerGroup, BulletGroup, playable_area, battle_map)
            else:
                item.update(dt)
        
        for item in loop_drawable:
            item.rect = item.draw(playable_area)    

        drawable_rect = pygame.rect.Rect(offset_x, offset_y, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.surface.Surface.blit(screen, playable_area, drawable_rect)
        pygame.display.flip()
        dt = clock.tick(60)/1000      