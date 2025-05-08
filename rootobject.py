import pygame, math, random
from enum import Enum

class ValidMovements(Enum): #starting to think these might be a mistake. maybe simplify? maybe use for actual movement functions?
    FollowEnemy = "following enemy"
    FollowAlly = "following ally/squad"
    AvoidHostile = "avoiding hostiles"
    AvoidObject = "moving around object"
    MoveToCursor = "moving to destination"
    WanderAround = "searching"
    StandStill = "standing still"


class RootObject(pygame.sprite.WeakSprite): 
    #ok so rootobject is the root of all other in-game sprites
    #everything is circles at its core, this may change later
    #i've tried to put as many helpers in here as i can get away with
    def __init__(self, x, y, radius):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        #self.velocity = pygame.Vector2(0, 0)
        self.radius = radius
        self.rotation = 0
        self.timer = 0
        self.turnspeed = 0
        self.movespeed = 0
        self.name = "root object"
        self.can_damage = False
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        #rect gets overdrawn almost immediately. needed for map loader
        

    def __repr__(self):
        pass

    def triangle(self): #this code is never not useful. does what it says it does
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def rotate(self, dt): #turns a guy. pass a negative value to reverse spin
        self.rotation += self.turnspeed * dt    

    def draw(self, screen):
        # sub-classes must override
        pass

    def update(self, dt, *args): #some updates have other args. just *args'd it to be safe
        # sub-classes must override
        pass

    def map_edge_check(self, map: pygame.surface.Surface):
        if self.rect:
            map_rect = map.get_rect()
            return map_rect.contains(self.rect)

    #def Update_rect(self): #in the off chance that the rect isn't synced right this should pass one through
        #self.rect = pygame.rect.Rect(self.position.x - (self.radius/2), self.position.y - (self.radius/2), self.radius, self.radius)
    #don't think this works. returning rects is fine for most classes, set an initial rect to radius


    def collision(self, object): #basic circle collision works in most things
        #override if necessary
        if object.position.distance_to(self.position) <= (self.radius + object.radius):
            return True
        else:
            return False
        
    def collision_rough(self, object): #a slightly "rougher" collision for objects that are already "colliding" so you don't need like super precision
        if object.position.distance_to(self.position) <= (self.radius + (object.radius * 1.1)):
            return True
        return False
        
    def move(self, dt): #basic vector movement
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * self.movespeed * dt

    def push_away(self, dt, vector, strength): #moves target along a different vector, useful for impacts
        self.position += vector * strength * dt

    def find_angle(self, target): #i hate this code so much but it *does* work
        angle = math.atan2(self.position.y - target.position.y, self.position.x - target.position.x)
        degrees = math.degrees(angle)+90
        '''while degrees < 180: #IF YOU CHANGE THESE VALUES THE WHOLE THING BREAKS
            degrees += 360
        while degrees > 180: #THIS IS THE ONE WARNING 
            degrees -= 360''' # THE MUSEUM OF MUFFIN'S SHITTY CODING, THE ANGLE FINDER EXHIBIT
        return math.remainder(degrees, 360)
    
    def Find_Target(self, group): #when i have pathfinding code i should really re-evaluate this but, again, it *works*
        #print(f"searching for enemies in {self.sight_range} radius")
        target_range = RootObject(self.position.x, self.position.y, self.sight_range)
        valid_targets = []
        for unit in group:
            if target_range.collision(unit):
                valid_targets.append(unit)
        #print(f"{len(valid_targets)} valid targets")
        if len(valid_targets) > 0:
            c_distance = float('inf')
            for target in valid_targets:
                target.pinged = True
                #print(f"target found: {target.name}")
                target_dist = pygame.math.Vector2.distance_to(pygame.Vector2(target.position.x, target.position.y), self.position)
                if target_dist < c_distance:                      
                    c_distance = target_dist
                    #print(f"set target {target.name} as target. distance to target {c_distance}")
                    self.current_target = target
        if len(valid_targets) == 0:
            #print(EnemyGroup)
            self.current_target = None

    