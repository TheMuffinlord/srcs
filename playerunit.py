import pygame, enum, math, random

from rootobject import RootObject, ValidMovements
#from battle_loop import *
from constants import PLAYER_RADIUS, PLAYER_HEALTH, PLAYER_DETECTION_RANGE
#from equipment import EngineType, PrimaryWeaponType
from textboxes import *

class PlayerRobot(RootObject):
    def __init__(self, x, y, name, unit_number): #other attributes to be set later
        super().__init__(x, y, PLAYER_RADIUS)

        self.maxhealth = PLAYER_HEALTH
        self.health = self.maxhealth
        self.movespeed = 0
        self.turnspeed = 0
        self.rotation_speed = self.turnspeed * 2
        self.rotation = 0
        self.aim_rotation = 0
        self.shot_diff = 5
        self.timer = 0
        self.color = "white"
        self.current_movement = ValidMovements.StandStill
        self.destination = []
        self.current_target = None
        self.can_damage = True
        self.name = name
        self.unit_number = unit_number
        self.sight_range = PLAYER_DETECTION_RANGE
        self.selected = False
        
        '''self.equipment = [
            EngineType(PLAYER_MOVESPEED, PLAYER_TURN_SPEED),
            PrimaryWeaponType(MINIGUN_ARC, MINIGUN_ROF)
        ]'''
        self.equipment = {}
        
        
    def __repr__(self):
        return f"PlayerRobot({self.name}, {self.health}/{self.maxhealth})"

    def draw(self, screen):
        if self.selected:
            self.color = "orange"
        else:
            self.color = "white"
        pygame.draw.circle(screen, "lightblue", self.position.xy, self.sight_range, 1)
        return pygame.draw.polygon(screen, self.color, self.triangle()) 

    def update(self, dt, EnemyGroup, surface, mapdict):
        self.timer -= dt
        self.Equipment_Check()
        self.Find_Target(EnemyGroup)
        self.Fire_At_Will(dt)
        if self.map_edge_check(surface):
            self.Move_Closer(dt, mapdict)
        else:
            #find a new destination i guess?
            pass
        
        
        
    def Equipment_Check(self):
        self.movespeed = self.equipment["engine"].move_speed
        self.turnspeed = self.equipment["engine"].turn_speed
        self.rotation_speed = self.turnspeed * 2
        #self.shot_diff = self.equipment[1].shot_diff


    def take_damage(self, damage):
        #print(self.timer)
        if self.timer <= 0:
            lines = [
                "!!UNIT DAMAGED!!",
                f"!!{damage} DAMAGE!!",
            ]
            dmgbox = DamageAlertBox(self, lines)
            self.health -= damage
            #print(f"{self.name} health: {self.health}")
            self.timer = HIT_COOLDOWN
            #print(f"time to next hit: {self.timer}")
        #else:
            #print(f"too soon for {self.name} to take damage")
        if self.health <= 0:
                #print("something broke")
                self.Unit_Destroyed()

    def Move_Closer(self, dt, mapdict):
        if self.destination != [] and self.destination != None:
            if self.next_node == None:
                next_spot = self.destination.pop()
                if isinstance(next_spot, tuple):
                    nn_x = next_spot[0]
                    nn_y = next_spot[1]
                elif isinstance(next_spot, pygame.Vector2):
                    nn_x = next_spot.x
                    nn_y = next_spot.y
                self.next_node = RootObject(nn_x, nn_y, 2)
        if self.next_node != None:
            degrees = self.find_angle(self.next_node)
        #print(f"moving to destination, current rotation {self.rotation}, target angle {degrees}")
            #if degrees < self.rotation:
                #self.rotate(dt * -1)
            #elif degrees > self.rotation:
                #self.rotate(dt)
            self.rotation = degrees
            
            if self.grid_oob(mapdict) == False:
                g_pos = self.grid_position(mapdict)
                print(f"ah shit we went out of bounds on grid square {g_pos}")
            if self.rect.contains(self.next_node.rect) == False:
                self.move(dt)
            else:
                self.next_node = None

    def aim_rotate(self, dt): #TODO:  CLAMP THIS LATER
        degrees = self.find_angle(self.current_target) 
        if degrees < self.aim_rotation:
            self.aim_rotation += self.rotation_speed * (-1 * dt)
        elif degrees > self.aim_rotation:
            self.aim_rotation += self.rotation_speed * dt
        #print(f"current rotation: {self.aim_rotation}, angle of target: {degrees}")
       
    
    
        
    def Fire_At_Will(self, dt):
        if self.current_target != None:
            self.aim_rotate(dt)
            #print(f"aim rotation: {self.aim_rotation} degrees, body rotation: {self.rotation} degrees")
            for weapon in self.equipment["weapons"]:
                weapon.Start_Shooting(dt, self.aim_rotation, self.position.x, self.position.y, self.radius)
            
    '''def Something_Broke(self):
        intact_gear = []
        broken = False
        for item in self.equipment:
            if item.intact == True:
                #print(item)
                intact_gear.append(item)
        if intact_gear == []:
            self.Unit_Destroyed()
        elif len(intact_gear) >= 1:
            #print(intact_gear)
            while broken == False:
                break_roll = random.randint(0, 1)
                broken = self.equipment[break_roll].Get_Broken()
            break_text = [
                f"!!BROKEN!!",
                f"{self.equipment[break_roll].short_form()}",
                f"!!BROKEN!!"
            ]
            break_box = DamageAlertBox(self, break_text)
            self.health = self.maxhealth'''

    def Unit_Destroyed(self):
        sad_end = [
            "ALERT ALERT ALERT UH OH",
            f"UNIT {self.name}",
            "!!!!!DESTROYED!!!!!"
        ]
        sad_box = DamageAlertBox(self, sad_end)
        self.kill()
        #put a big explosion here or something, i dunno