import pygame, math, random

class RootObject(pygame.sprite.WeakSprite):
    def __init__(self, x, y, radius):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius
        self.rotation = 0
        self.timer = 0
        self.turnspeed = 0
        self.movespeed = 0
        self.name = "root object"
        self.can_damage = False
        self.rect = pygame.rect.Rect(x - (radius/2), y - (radius/2), radius, radius)

    def __repr__(self):
        pass

    def triangle(self): #this code is never not useful
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def rotate(self, dt):
        self.rotation += self.turnspeed * dt    

    def draw(self, screen):
        # sub-classes must override
        pass

    def update(self, dt, *args):
        # sub-classes must override
        pass

    def collision(self, object):
        if object.position.distance_to(self.position) <= (self.radius + object.radius):
            return True
        else:
            return False
        
    def collision_rough(self, object):
        if object.position.distance_to(self.position) <= (self.radius + (object.radius * 1.1)):
            return True
        return False
        
    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * self.movespeed * dt

    def find_angle(self, target):
        angle = math.atan2(self.position.y -target.position.y, self.position.x - target.position.x)
        degrees = math.degrees(angle)+90
        while degrees < 180:
            degrees += 360
        while degrees > 180:
            degrees -= 360
        return degrees
    