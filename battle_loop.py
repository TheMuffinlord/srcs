import pygame, math, random
import pygamepal as pgp
from constants import *
from enum import Enum
from rootobject import RootObject
from playerunit import PlayerRobot
from enemies import EnemyUnit, EnemySpawner
from equipment import BasicBullet, BasicLaser, Particle
from textboxes import *

def kbd_interpreter(pressed_key):
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
            toggle_selection(unit)
        

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
    
def mouse_interpreter(clicked_position, clicked_button):
    global SelectionGroup, offset_x, offset_y
    if clicked_button[0] or clicked_button[1]:
        go_here = SelectionCursor(clicked_position[0] + (-1 * offset_x), clicked_position[1] + (-1 * offset_y))
        for unit in SelectionGroup:
            unit.destination = go_here
            print(f"setting {unit.name} destination to {unit.destination.position}")
            toggle_selection(unit)        

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
    clock = pygame.time.Clock()
    dt = 0
    
    global offset_x, offset_y, screenmax_x, screenmax_y
    offset_x = 0
    offset_y = 0
    screenmax_x = SCREEN_WIDTH * 3
    screenmax_y = SCREEN_HEIGHT * 3
    playable_area = pygame.surface.Surface((screenmax_x, screenmax_y))

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

    Player = PlayerRobot(250, 300, "john character", 1)
    Player2 = PlayerRobot(250, 650, "jane character", 2)
    
    Spawner = EnemySpawner(1500, 500)
    Spawner2 = EnemySpawner(1800, 900)

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
                    mouse_interpreter(clicked_location, clicked_button)
                    action_waiting = False
                    mouse_waiting = False
                elif kbd_waiting == True:
                    kbd_interpreter(pressed_key)
                    action_waiting = False
                    kbd_waiting = False
                else: 
                    action_waiting = False
                    print("some other action took place?")

        pygame.Surface.fill(playable_area, "purple")

        for item in loop_updatable:
            if item in PlayerGroup:
                item.update(dt, EnemyGroup)
            elif item in EnemyGroup:
                item.update(dt, PlayerGroup, BulletGroup)
            else:
                item.update(dt)
        
        for item in loop_drawable:
            item.rect = item.draw(playable_area)    

        drawable_rect = pygame.rect.Rect(offset_x, offset_y, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.surface.Surface.blit(screen, playable_area, drawable_rect)
        pygame.display.flip()
        dt = clock.tick(60)/1000      