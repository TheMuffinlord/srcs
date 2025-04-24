import pygame, random, math
from enum import Enum
from rootobjects import *
from constants import *
from enemies import *

class ValidMovements(Enum):
    FollowEnemy = "following enemy"
    FollowAlly = "following ally/squad"
    AvoidHostile = "avoiding hostiles"
    AvoidObject = "moving around object"
    MoveToCursor = "moving to destination"
    
    StandStill = "standing still"

class PlayerRobot(RootObject):
    def __init__(self, x, y, name, unit_number): #other attributes to be set later
        super().__init__(x, y, PLAYER_RADIUS)

        self.maxhealth = PLAYER_HEALTH
        self.health = self.maxhealth
        self.movespeed = PLAYER_MOVESPEED
        self.turnspeed = PLAYER_TURN_SPEED
        self.rotation_speed = PLAYER_TURN_SPEED * 2
        self.rotation = 0
        self.aim_rotation = 0
        self.timer = 0
        self.color = "white"
        self.current_movement = ValidMovements.StandStill
        self.destination = None
        self.current_target = None
        self.name = name
        self.unit_number = unit_number
        self.sight_range = int(BASIC_BULLET_VELOCITY * BASIC_BULLET_LIFESPAN)
        self.selected = False
        
    def __repr__(self):
        return f"PlayerRobot({self.name}, {self.health}/{self.maxhealth})"

    def draw(self, screen):
        if self.selected:
            self.color = "orange"
        else:
            self.color = "white"
        return pygame.draw.polygon(screen, self.color, self.triangle())

    def update(self, dt, target_group):
        self.Find_Target(target_group)
        self.Fire_At_Will(dt)
        self.Move_Closer(dt)

    def Find_Target(self, target_group):
        #print(f"searching for enemies in {self.sight_range} radius")
        target_range = RootObject(self.position.x, self.position.y, self.sight_range)
        valid_targets = []
        for unit in target_group:
            if target_range.collision(unit):
                valid_targets.append(unit)
    
        #print(f"{len(valid_targets)} valid targets")
        if len(valid_targets) > 0:
            
            c_x = self.position.x + self.sight_range
            c_y = self.position.y + self.sight_range
            c_vector = pygame.Vector2(c_x, c_y)
            c_distance = float('inf')
            c_target = None
            for target in valid_targets:
                #print(f"target found: {target.name}")
                target_dist = pygame.Vector2(target.position.x, target.position.y)
                if pygame.math.Vector2.distance_to(target_dist, c_vector) < c_distance:
                    c_target = target
                    c_x = target.position.x
                    c_y = target.position.y
                    c_vector = pygame.Vector2(c_x, c_y)
                    #print(f"set target {target.name} as target")
            self.current_target = c_target
            #print(f"current target is {self.current_target.name}")
        if len(valid_targets) == 0:
            #print(target_group)
            self.current_target = None

    def aim_rotate(self, dt):
        angle = math.atan2(self.position.y - self.current_target.position.y, self.position.x - self.current_target.position.x)
        degrees = math.degrees(angle)+90
        while degrees < 180:
            degrees += 360
        while degrees > 180:
            degrees -= 360
        if degrees < self.aim_rotation:
            self.aim_rotation += self.rotation_speed * (-1 * dt)
        elif degrees > self.aim_rotation:
            self.aim_rotation += self.rotation_speed * dt
        #print(f"current rotation: {self.aim_rotation}, angle of target: {degrees}")
       
    def Move_Closer(self, dt):
        if self.destination != None:
            #print("moving to destination")
            angle = math.atan2(self.position.y - self.destination.position.y, self.position.x - self.destination.position.x)
            degrees = math.degrees(angle)+90
            while degrees < 180:
                degrees += 360
            while degrees > 180:
                degrees -= 360
            if degrees < self.rotation:
                self.rotate(dt * -1)
            elif degrees > self.rotation:
                self.rotate(dt)
            if self.collision(self.destination) == False:
                self.move(dt)
        

    def Fire_At_Will(self, dt):
        if self.current_target != None:
            self.aim_rotate(dt)
            shot_diff = random.randrange(-30, 30)
            forward = pygame.Vector2(0, 1).rotate(self.aim_rotation + shot_diff)
            b_x = self.position.x + forward.x * self.radius
            b_y = self.position.y + forward.y * self.radius
            bullet = BasicBullet(b_x, b_y, forward * BASIC_BULLET_VELOCITY)
            

class BasicBullet(RootObject):
    def __init__(self, x, y, velocity):
        super().__init__(x, y, BASIC_BULLET_RADIUS)
        self.velocity = velocity
        self.damage = BASIC_BULLET_DAMAGE
        self.timer = BASIC_BULLET_LIFESPAN
        self.color = "white"

    def draw(self, screen):
        if self.timer < BASIC_BULLET_LIFESPAN / 2:
            self.color = "gray"
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.kill()
        self.position += (self.velocity * dt) 