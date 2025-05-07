import pygame
from rootobject import RootObject

class Obstacle(RootObject):
    def __init__(self, x, y, type):
        if type == "rock":
            radius = 25
            self.color = "gray"
        #more tbd
        super().__init__(x, y, radius)
        self.can_damage = False
        self.rect = pygame.rect.Rect(self.position.x-self.radius, self.position.y-self.radius, self.radius*2, self.radius*2)

    def draw(self, screen):
        return pygame.draw.circle(screen, self.color, self.position.xy, self.radius)
    
    def update(self, *args):
        #oh who the hell knows it's a fucking rock
        pass

#sample map dictionary

map1 = {
    "name": "training mission",
    "spawn": (250, 250),
    "mapsize_x": 3000,
    "mapsize_y": 2000,
    "objects": [
        Obstacle(50, 50, "rock"),
        Obstacle(50, 100, "rock"),
        Obstacle(400, 50, "rock"),
        Obstacle(400, 100, "rock"),
        Obstacle(400, 200, "rock"),
        Obstacle(50, 1800, "rock"),
        Obstacle(50, 1850, "rock"),
        Obstacle(50, 1900, "rock"),
        Obstacle(500, 400, "rock"),
        Obstacle(550, 450, "rock")
    ]
}

def map_generator(map_dictionary: dict):
    #i should have thought this out first
    pass