import pygame, math, enum, random
from constants import *
from rootobject import RootObject
#from playerunit import *


class BasicLaser(RootObject):
    def __init__(self, x, y, rotation):
        super().__init__(x, y, BASIC_BULLET_RADIUS * 3)
        self.beam_length = BASIC_LASER_LENGTH
        #self.velocity = self.position + r_vector * self.beam_length
        self.velocity = self.position.rotate(rotation)
        self.radian_rotation = math.radians(rotation+90)
        self.end_x = BASIC_LASER_LENGTH * math.cos(self.radian_rotation) + self.position.x
        self.end_y = BASIC_LASER_LENGTH * math.sin(self.radian_rotation) + self.position.y
        self.endpoint = (self.end_x, self.end_y)
        #print(f"beam should go from {self.position.xy} to {self.end_x}, {self.end_y}")
        self.damage =  BASIC_LASER_DAMAGE
        self.timer = BASIC_LASER_LIFESPAN
        self.color = pygame.Color(128,128,255)
        self.knockback = BASIC_LASER_KNOCKBACK
        self.line = None
        self.been_particled = False
        
    def draw(self,screen):
        #if self.rect:
            #pygame.draw.rect(screen, "white", self.rect)
        self.line = pygame.draw.line(screen, self.color, self.position.xy, self.endpoint, self.radius)
        #return pygame.draw.polygon(screen, self.color, [self.position.xy, self.endpoint, (self.end_x + self.radius, self.end_y + self.radius), (self.position.x + self.radius, self.position.y + self.radius)])
        return self.line

    
    def update(self, dt):
        self.timer -= dt
        self.color.r -= 2
        self.color.g -= 2
        self.color.b -= 1
        if self.timer <= 0:
            self.kill()
    
    def get_particled(self, collision_object):
        if self.been_particled == False:
            c_x, c_y = collision_object.position.xy
            pops = random.randint(1,20)
            for n in range(pops):
                debris = Particle(c_x, c_y)
            #self.endpoint = (c_x, c_y)
            #print(f"placing particles at {self.endpoint}")
            #self.been_particled = True

    def collision(self, object: pygame.sprite.Sprite): #had to override the collision class. not working as intended but does detect!
        if self.line != None:
            impact_point = object.rect.clipline(self.position.xy, self.endpoint)
            if impact_point != ():
                return True
            return False
        return False
        

class BasicBullet(RootObject):
    def __init__(self, x, y, velocity):
        super().__init__(x, y, BASIC_BULLET_RADIUS)
        self.velocity = velocity
        self.damage = BASIC_BULLET_DAMAGE
        self.timer = BASIC_BULLET_LIFESPAN
        self.color = "yellow"
        self.knockback = BASIC_BULLET_KNOCKBACK

    def draw(self, screen):
        if self.timer < BASIC_BULLET_LIFESPAN / 2:
            self.color = "orange"
        return pygame.draw.circle(screen, self.color, self.position, self.radius)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.kill()
        self.position += (self.velocity * dt)

    def get_particled(self, *args):
        pops = random.randint(1,20)
        for n in range(pops):
            debris = Particle(self.position.x, self.position.y)
        self.kill()
            
class Particle(RootObject):
    def __init__(self, x, y):
        super().__init__(x, y, 1)
        self.color = "yellow"
        self.timer = PARTICLE_DECAY
        self.rotation = random.randint(0,359)
        self.movespeed = PARTICLE_SPEED

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.kill()
        self.move(dt)

    def draw(self, screen):
        if self.timer < PARTICLE_DECAY / 2:
            self.color = "orange"
        return pygame.draw.circle(screen, self.color, self.position, self.radius)

class EngineType():
    def __init__(self, move_speed, turn_speed):
        self.move_speed = move_speed
        self.turn_speed = turn_speed
        self.broken_move_speed = move_speed // 5
        self.broken_turn_speed = turn_speed // 5
        self.intact = True

    def __repr__(self):
        return f"Engine, move speed {self.move_speed}, turn rate {self.turn_speed}, intact: {self.intact}"
        
    def short_form(self):
        return f"Engine {self.move_speed}/{self.turn_speed}"

    def Get_Broken(self):
        self.intact = False
        self.move_speed = self.broken_move_speed
        self.turn_speed = self.broken_turn_speed

class PrimaryWeaponType():
    def __init__(self, shot_diff, rate_of_fire):
        self.intact = True
        self.shot_diff = shot_diff
        self.broken_shot_diff = shot_diff * 3
        self.rate_of_fire = rate_of_fire
        self.broken_rof = rate_of_fire * 25
        self.timer = 0
        self.weapontype = "minigun"
    
    def __repr__(self):
        return f"Primary Weapon: {self.weapontype}, {self.shot_diff*2} degree arc, {self.rate_of_fire} shot timer; intact: {self.intact}"

    def short_form(self):
        return f"Minigun {self.shot_diff*2}/{self.rate_of_fire//600}"
    #def __str__(self):
        #return f"Primary Weapon: Minigun, {self.shot_diff*2} degree arc, {self.rate_of_fire} shot timer; intact: {self.intact}"

    def Get_Broken(self):
        if self.intact == True:
            self.intact = False
            self.shot_diff = self.broken_shot_diff
            self.rate_of_fire = self.broken_rof
            return True
        return False
        

    def Start_Shooting(self, dt, rotation, unit_x, unit_y, radius):
        if self.timer <= 0:
            if self.weapontype == "minigun":
                bullet_spread = random.randrange((self.shot_diff * -1), self.shot_diff)
                forward = pygame.Vector2(0, 1).rotate(rotation + bullet_spread)
                b_x = unit_x + forward.x * radius
                b_y = unit_y + forward.y * radius
                bullet = BasicBullet(b_x, b_y, forward * BASIC_BULLET_VELOCITY)
            if self.weapontype == "laser":
                bullet = BasicLaser(unit_x, unit_y, rotation)
            self.timer = self.rate_of_fire
        self.timer -= dt