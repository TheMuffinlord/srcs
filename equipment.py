import pygame, math, enum, random
#from constants import BASIC_BULLET_DAMAGE, BASIC_BULLET_KNOCKBACK, BASIC_BULLET_LIFESPAN, BASIC_BULLET_RADIUS, BASIC_BULLET_VELOCITY, BASIC_LASER_DAMAGE, BASIC_LASER_KNOCKBACK, BASIC_LASER_LENGTH, 
# BASIC_LASER_LIFESPAN, PLAYER_MOVESPEED, PLAYER_TURN_SPEED, PARTICLE_DECAY, PARTICLE_SPEED, MINIGUN_ARC, MINIGUN_ROF, LASER_ROF
from rootobject import RootObject

#from playerunit import *

PLAYER_MOVESPEED = 100
PLAYER_TURN_SPEED = 150

BASIC_BULLET_RADIUS = 3
BASIC_BULLET_VELOCITY = 800
BASIC_BULLET_DAMAGE = 6
BASIC_BULLET_LIFESPAN = 0.7
BASIC_BULLET_KNOCKBACK = 1

MINIGUN_ARC = 30
#LASER_ARC = 0 #not used currently
LASER_ROF = 0.5
MINIGUN_ROF = 0.005

BASIC_LASER_LENGTH = 500
BASIC_LASER_LIFESPAN = 0.4
BASIC_LASER_DAMAGE = 10
BASIC_LASER_KNOCKBACK = 0.1

PARTICLE_DECAY = 0.25
PARTICLE_SPEED = 50

class BasicLaser(RootObject):
    def __init__(self, x, y, rotation, level):
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
    def __init__(self, x, y, velocity, level):
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

class Engine():
    def __init__(self, level):
        self.level = level
        if level > 0:
            self.move_speed = PLAYER_MOVESPEED
            self.turn_speed = PLAYER_TURN_SPEED
        if level > 1:
            self.move_speed *= 2
        #do more logic later. can i put this somewhere better?
        self.intact = True

    def __repr__(self):
        return f"Engine level {self.level}, move speed {self.move_speed}, turn rate {self.turn_speed}"
        
    def short_form(self):
        return f"Engine {self.move_speed}/{self.turn_speed}"

    
class Weapon_Minigun():
    def __init__(self, level):
        self.level = level
        match self.level:
            case 1:
                self.rate_of_fire = MINIGUN_ROF
                self.shot_diff = MINIGUN_ARC
                self.num_shots = 1
            case 2:
                self.rate_of_fire = MINIGUN_ROF
                self.shot_diff = MINIGUN_ARC
                self.num_shots = 2
            case 3:
                self.rate_of_fire = MINIGUN_ROF
                self.shot_diff = MINIGUN_ARC // 2
                self.num_shots = 2
            case 4:
                self.rate_of_fire = MINIGUN_ROF / 2
                self.shot_diff = MINIGUN_ARC // 2
                self.num_shots = 3
                
                
        self.timer = 0
        self.weapontype = "minigun"
    
    def __repr__(self):
        return f"Minigun level {self.level}, {self.shot_diff*2} degree arc, {self.rate_of_fire} shot timer"

    def short_form(self):
        return f"Minigun {self.shot_diff*2}/{self.rate_of_fire//600}"
    #def __str__(self):
        #return f"Primary Weapon: Minigun, {self.shot_diff*2} degree arc, {self.rate_of_fire} shot timer; intact: {self.intact}"

    def Start_Shooting(self, dt, rotation, unit_x, unit_y, radius):
        if self.timer <= 0:
            for shot in range(self.num_shots):
                bullet_spread = random.randrange((self.shot_diff * -1), self.shot_diff)
                forward = pygame.Vector2(0, 1).rotate(rotation + bullet_spread)
                b_x = unit_x + forward.x * radius
                b_y = unit_y + forward.y * radius
                bullet = BasicBullet(b_x, b_y, forward * BASIC_BULLET_VELOCITY, self.level)
            self.timer = self.rate_of_fire
        self.timer -= dt

class Weapon_Laser():
    def __init__(self, level):
        self.level = level
        self.timer = 0
        self.weapontype = "laser"
        if self.level > 0:
            self.rate_of_fire = LASER_ROF
        
    def __repr__(self):
        return f"Laser level {self.level}, {self.rate_of_fire} shot timer"

    def short_form(self):
        return f"Laser {self.shot_diff*2}/{self.rate_of_fire//600}"
    #def __str__(self):
        #return f"Primary Weapon: Minigun, {self.shot_diff*2} degree arc, {self.rate_of_fire} shot timer; intact: {self.intact}"

    def Start_Shooting(self, dt, rotation, unit_x, unit_y, *args):
        if self.timer <= 0:
            laser = BasicLaser(unit_x, unit_y, rotation, self.level)
            self.timer = self.rate_of_fire
        self.timer -= dt