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
    def __init__(self, x, y, name): #other attributes to be set later
        super().__init__(x, y, PLAYER_RADIUS)

        self.maxhealth = PLAYER_HEALTH
        self.health = self.maxhealth
        self.movespeed = PLAYER_MOVESPEED
        self.turnspeed = PLAYER_TURN_SPEED
        self.rotation = 0
        self.aim_rotation = 0
        self.timer = 0
        self.color = "white"
        self.current_movement = ValidMovements.StandStill
        self.destination = None
        self.current_target = None
        self.name = name
        self.sight_range = int(BASIC_BULLET_VELOCITY * BASIC_BULLET_LIFESPAN)
        
    def __repr__(self):
        return f"PlayerRobot({self.name}, {self.health}/{self.maxhealth})"

    def aim_rotate(self, dt):
        angle = math.atan2(self.position.y - self.current_target.position.y, self.position.x - self.current_target.position.x)
        degrees = math.degrees(angle)+90
        if degrees < self.aim_rotation:
            self.aim_rotation += self.turnspeed * (-1 * dt)
        elif degrees > self.aim_rotation:
            self.aim_rotation += self.turnspeed * dt
        #print(f"current rotation: {self.aim_rotation}, angle of target: {degrees}")
    
    def draw(self, screen):
        return pygame.draw.polygon(screen, self.color, self.triangle())

    def update(self, dt, target_group):
        self.Find_Target(target_group)
        if self.current_target != None:
            self.Fire_At_Will(dt)
        if self.current_movement != ValidMovements.StandStill:
            self.Move_Closer(dt)

    def Find_Target(self, group):
        print(f"searching for enemies in {self.sight_range} radius")
        target_range = pygame.sprite.GroupSingle(RootObject(self.position.x, self.position.y, self.sight_range))

        valid_targets = pygame.sprite.groupcollide(group, target_range, False, False, pygame.sprite.collide_circle)
        
        if len(valid_targets) > 0:
            print(f"{len(valid_targets)} valid targets")
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
                    print(f"set target {target.name} as target")
            self.current_target = c_target
            #print(f"current target is {self.current_target.name}")
        elif len(valid_targets) == 0:
            
            self.current_target = None

        
    def Move_Closer(self, dt):
        if self.destination != None:
            angle = math.atan2(self.position.y - self.destination.position.y, self.position.x - self.destination.position.x)
            degrees = math.degrees(angle)+90
            if self.rotation > degrees:
                self.rotate(dt)
            elif self.rotation < degrees:
                self.rotate(dt * -1)
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