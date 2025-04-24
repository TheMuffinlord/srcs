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
        self.movespeed = 0
        self.turnspeed = 0
        self.rotation_speed = PLAYER_TURN_SPEED * 2
        self.rotation = 0
        self.aim_rotation = 0
        self.shot_diff = 5
        self.timer = 0
        self.color = "white"
        self.current_movement = ValidMovements.StandStill
        self.destination = None
        self.current_target = None
        self.can_damage = True
        self.name = name
        self.unit_number = unit_number
        self.sight_range = int(BASIC_BULLET_VELOCITY * BASIC_BULLET_LIFESPAN)
        self.selected = False
        self.equipment = (
            EngineType(PLAYER_MOVESPEED, PLAYER_TURN_SPEED),
            PrimaryWeaponType(MINIGUN_ARC, MINIGUN_ROF)
        )
        
    def __repr__(self):
        return f"PlayerRobot({self.name}, {self.health}/{self.maxhealth})"

    def draw(self, screen):
        if self.selected:
            self.color = "orange"
        else:
            self.color = "white"
        return pygame.draw.polygon(screen, self.color, self.triangle())

    def update(self, dt, target_group):
        self.timer -= dt
        self.Equipment_Check()
        self.Find_Target(target_group)
        self.Fire_At_Will(dt)
        self.Move_Closer(dt)
        
        
    def Equipment_Check(self):
        self.movespeed = self.equipment[0].move_speed
        self.turnspeed = self.equipment[0].turn_speed
        self.shot_diff = self.equipment[1].shot_diff

    def take_damage(self, damage):
        #print(self.timer)
        if self.timer <= 0:
            #print(f"{self.name} took {damage} damage")
            self.health -= damage
            #print(f"{self.name} health: {self.health}")
            self.timer = HIT_COOLDOWN
            #print(f"time to next hit: {self.timer}")
        #else:
            #print(f"too soon for {self.name} to take damage")
        if self.health <= 0:
                #print("something broke")
                self.Something_Broke()

    def Find_Target(self, target_group):
        #print(f"searching for enemies in {self.sight_range} radius")
        target_range = RootObject(self.position.x, self.position.y, self.sight_range)
        valid_targets = []
        for unit in target_group:
            if target_range.collision(unit):
                valid_targets.append(unit)
        #print(f"{len(valid_targets)} valid targets")
        if len(valid_targets) > 0:
            c_distance = float('inf')
            for target in valid_targets:
                #print(f"target found: {target.name}")
                target_dist = pygame.math.Vector2.distance_to(pygame.Vector2(target.position.x, target.position.y), self.position)
                if target_dist < c_distance:                      
                    c_distance = target_dist
                    #print(f"set target {target.name} as target. distance to target {c_distance}")
                    self.current_target = target
        if len(valid_targets) == 0:
            #print(target_group)
            self.current_target = None

    def aim_rotate(self, dt):
        degrees = self.find_angle(self.current_target)
        if degrees < self.aim_rotation:
            self.aim_rotation += self.rotation_speed * (-1 * dt)
        elif degrees > self.aim_rotation:
            self.aim_rotation += self.rotation_speed * dt
        #print(f"current rotation: {self.aim_rotation}, angle of target: {degrees}")
       
    def Move_Closer(self, dt):
        if self.destination != None:
            #print("moving to destination")
            degrees = self.find_angle(self.destination)
            if degrees < self.rotation:
                self.rotate(dt * -1)
            elif degrees > self.rotation:
                self.rotate(dt)
            if self.collision(self.destination) == False:
                self.move(dt)
        
    def Fire_At_Will(self, dt):
        if self.current_target != None:
            self.aim_rotate(dt)
            bullet_spread = random.randrange((self.shot_diff * -1), self.shot_diff)
            forward = pygame.Vector2(0, 1).rotate(self.aim_rotation + bullet_spread)
            b_x = self.position.x + forward.x * self.radius
            b_y = self.position.y + forward.y * self.radius
            self.equipment[1].Start_Shooting(dt, forward, b_x, b_y)
            

    def Something_Broke(self):
        intact_gear = []
        broken = False
        for item in self.equipment:
            if item.intact == True:
                #print(item)
                intact_gear.append(item)
        if intact_gear == []:
            self.Unit_Destroyed()
        elif len(intact_gear) >= 1:
            print(intact_gear)
            while broken == False:
                break_roll = random.randint(0, 1)
                broken = self.equipment[break_roll].Get_Broken()
            print(f"{self.equipment[break_roll]} broke")
            self.health = self.maxhealth


    def Unit_Destroyed(self):
        print(f"unit {self.name} destroyed, please code this")
        self.kill()
        #put a big explosion here or something, i dunno
        

class BasicBullet(RootObject):
    def __init__(self, x, y, velocity):
        super().__init__(x, y, BASIC_BULLET_RADIUS)
        self.velocity = velocity
        self.damage = BASIC_BULLET_DAMAGE
        self.timer = BASIC_BULLET_LIFESPAN
        self.color = "yellow"

    def draw(self, screen):
        if self.timer < BASIC_BULLET_LIFESPAN / 2:
            self.color = "orange"
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.kill()
        self.position += (self.velocity * dt)
        

class EngineType():
    def __init__(self, move_speed, turn_speed):
        self.move_speed = move_speed
        self.turn_speed = turn_speed
        self.broken_move_speed = move_speed // 5
        self.broken_turn_speed = turn_speed // 5
        self.intact = True

    def __repr__(self):
        return f"Engine, move speed {self.move_speed}, turn rate {self.turn_speed}, intact: {self.intact}"
        
    def Get_Broken(self):
        self.intact = False
        self.move_speed = self.broken_move_speed
        self.turn_speed = self.broken_turn_speed

class PrimaryWeaponType():
    def __init__(self, shot_diff, rate_of_fire):
        self.intact = True
        self.shot_diff = shot_diff
        self.broken_shot_diff = shot_diff
        self.rate_of_fire = rate_of_fire * 3
        self.broken_rof = rate_of_fire / 5
        self.timer = 0
    
    def __repr__(self):
        return f"Primary Weapon: Minigun, {self.shot_diff*2} degree arc, {self.rate_of_fire} shot timer; intact: {self.intact}"

    #def __str__(self):
        #return f"Primary Weapon: Minigun, {self.shot_diff*2} degree arc, {self.rate_of_fire} shot timer; intact: {self.intact}"

    def Get_Broken(self):
        if self.intact == True:
            self.intact = False
            self.shot_diff = self.broken_shot_diff
            self.rate_of_fire = self.broken_rof
            return True
        return False
        

    def Start_Shooting(self, dt, direction, b_x, b_y):
        if self.timer <= 0:
            bullet = BasicBullet(b_x, b_y, direction * BASIC_BULLET_VELOCITY)
            self.timer = self.rate_of_fire
        self.timer -= dt