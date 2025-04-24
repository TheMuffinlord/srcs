import pygame, math, random
from enum import Enum
from rootobjects import *
from constants import *
from playerunits import *


class ValidMovements(Enum):
    FollowEnemy = "following enemy"
    FollowAlly = "following ally/squad"
    MoveToCursor = "moving to destination"
    StandStill = "standing still"

class EnemyTypes(Enum):
    EnemyUnit = "basic enemy"
    EnemySpawner = "enemy spawner"

class EnemyUnit(RootObject): #will have to branch off for extra enemy types
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_RADIUS)
        self.maxhealth = ENEMY_MAX_HEALTH
        self.health = self.maxhealth
        self.rotation = 0
        self.movespeed = ENEMY_MOVE_SPEED
        self.turnspeed = ENEMY_TURN_SPEED
        self.timer = 0
        self.current_movement = ValidMovements.StandStill
        self.destination = None
        self.color = "red"
        self.sight_range = ENEMY_DETECTION_RANGE
        self.current_target = None
        self.name = "debug enemy"
        self.spawner = None
        self.valid_targets = None
        self.type = EnemyTypes.EnemyUnit
        self.damage_value = ENEMY_DAMAGE_VALUE
        self.can_damage = True

    def draw(self, screen):
        if self.color == "white" and self.timer < HIT_COOLDOWN - 0.1:
            self.color = "red"
        return pygame.draw.polygon(screen, self.color, self.triangle())

    def update(self, dt, target_group, bullet_group):
        self.timer -= dt
        if self.current_target == None:
            self.Find_Target(target_group)  
        if self.current_movement != ValidMovements.StandStill:
            self.Move_Closer(dt)
        for bullet in bullet_group:
            self.check_bullet(bullet, dt)
        if self.destination and self.collision(self.destination) == True and self.destination.can_damage == True:
            self.destination.take_damage(self.damage_value)
        

    def check_bullet(self, bullet, dt):
        if self.collision(bullet):
            bullet.kill()
            self.color = "white"
            self.take_damage(bullet.damage)
        

    def take_damage(self, damage):
        if self.timer <= 0:
            #print(f"took {damage} damage")
            self.health -= damage
            self.timer = HIT_COOLDOWN
            if self.health <= 0:
                self.kill()
                if self.spawner != None and self.spawner.alive():
                    self.spawner.health += ENEMY_MAX_HEALTH // 2
                    self.spawner.color = "green"



    def Find_Target(self, group):
        target_range = RootObject(self.position.x, self.position.y, self.sight_range)
        valid_targets = pygame.sprite.spritecollide(target_range, group, False)
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
            self.destination = c_target
            self.current_movement = ValidMovements.FollowEnemy
        else:
            self.current_target = None
            self.current_movement = ValidMovements.FollowAlly
        
    def Move_Closer(self, dt):
        if self.destination != None:
            degrees = self.find_angle(self.destination)
            if self.rotation > degrees:
                self.rotate(dt*-1)
            elif self.rotation < degrees:
                self.rotate(dt)
            if self.collision(self.destination) == False:
                self.move(dt)
                
            else:
                #eventually damage will go here but for now i want them to kinda wander a bit
                self.destination = None
        else:
            self.Wander_Around(dt)

    def Wander_Around(self, dt):
        if self.timer < 0:
            r_x = random.randrange(0, SCREEN_WIDTH)
            r_y = random.randrange(0, SCREEN_HEIGHT)
            angle = math.atan2(self.position.y - r_y, self.position.x - r_x)
            degrees = math.degrees(angle)+90
            while degrees > 360:
                degrees -= 360
            while degrees < 0:
                degrees += 360
            if self.rotation > degrees:
                self.rotate((dt*-1)/4)
            elif self.rotation < degrees:
                self.rotate(dt/4)
                self.timer = random.random()
        if self.timer > 0:
            self.timer -= dt*2
            self.move(dt/4)
                



    def Fire_At_Will(self):
        # pull the target up, start blasting
        pass #later!!

class EnemySpawner(RootObject):
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_RADIUS*3)
        self.maxhealth = ENEMY_MAX_HEALTH*25
        self.health = self.maxhealth
        self.rotation = 0
        self.movespeed = ENEMY_MOVE_SPEED//2
        self.turnspeed = ENEMY_TURN_SPEED//2
        self.timer = 0
        self.spawn_timer = SPAWN_COOLDOWN
        self.current_movement = ValidMovements.StandStill
        self.destination = None
        self.color = "red"
        self.sight_range = ENEMY_DETECTION_RANGE//2
        self.current_target = None
        self.name = "enemy spawner"
        self.type = EnemyTypes.EnemySpawner
        
    
    def draw(self, screen):
        return pygame.draw.polygon(screen, self.color, self.triangle())
    
    def update(self, dt, target_group, bullet_group):
        self.timer -= dt
        self.spawn_timer -= dt
        for bullet in bullet_group:
            self.check_bullet(bullet, dt)
        if self.color == "white" and self.timer < HIT_COOLDOWN - 0.1:
            self.color = "red"
        if self.health > ENEMY_MAX_HEALTH:            
            self.enemy_spawn(target_group)

    def check_bullet(self, bullet, dt):
        if self.collision(bullet):
            bullet.kill()
            self.color = "white"
            self.take_damage(bullet.damage)
        
    def take_damage(self, damage):
        if self.timer <= 0:
            print(f"took {damage} damage")
            self.health -= damage
            self.timer = HIT_COOLDOWN
            if self.health <= 0:
                self.kill()
    
    def enemy_spawn(self, target_group):
        if self.spawn_timer < 0:
            self.health -= ENEMY_MAX_HEALTH
            new_enemy = EnemyUnit(self.position.x, self.position.y)
            new_enemy.add(self.groups())
            new_enemy.spawner = self
            new_enemy.rotation = random.randrange(0,360)
            new_enemy.valid_targets = target_group
            self.spawn_timer = SPAWN_COOLDOWN
