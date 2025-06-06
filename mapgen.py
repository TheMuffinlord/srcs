import pygame, pytmx
from rootobject import RootObject

class GroundTile(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, surface_type, image: pygame.surface.Surface):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self._pos = (x * width, y * height)
        self.row = y
        self.col = x
        self.surface_type = surface_type
        if self.surface_type == "grass" or self.surface_type == "dirt":
            self.passable = True
        else:
            self.passable = False
        self.image = image
        self.rect = self.image.get_rect()

    def draw(self, surface):
        #print("ground tile drawing")
        surface.blit(self.image, self._pos, self.rect)
        return self.rect

class Obstacle(RootObject):
    def __init__(self, x, y, type):
        if type == "rock":
            radius = 32
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

def tmx_generator(tmx_file):
    levelmap = pytmx.load_pygame(tmx_file)
    tw = levelmap.tilewidth
    th = levelmap.tileheight
    mapsize_x = levelmap.width * tw
    mapsize_y = levelmap.height * th
    ground = levelmap.get_layer_by_name("ground")
    #objects = levelmap.get_layer_by_name("objects")
    spawnpoint = levelmap.get_object_by_name("spawnpoint")
    mapdict = {
        "name": levelmap.properties["mapname"],
        "spawn": (spawnpoint.x*2, spawnpoint.y*2),
        "mapsize_x": mapsize_x,
        "mapsize_y": mapsize_y,
        "tilewidth": tw,
        "tileheight": th,
        "ground": [],
        "objects": [],
        "nodegrid": [],
        "nodegraph": {},
    }
    for tile in ground:
        x = tile[0]
        y = tile[1]
        image = levelmap.get_tile_image(x, y, 0)
        props = levelmap.get_tile_properties(x, y, 0)
        name = props["type"]
        name = name.rstrip("1234567890")
        #print(name)
        #new_x = x * tw
        #new_y = y * th
        newtile = GroundTile(x, y, tw, th, name, image)
        #print(f"drawing ground tile at ({new_x}, {new_y}) using image {image}")
        mapdict["ground"].append(newtile)
    
    return pathnode_generator(mapdict)

def pathnode_generator(mapdict: dict):
    nodegrid = []
    c_graph = []
    nodegraph = {}
    c_row = 0
    for tile in mapdict["ground"]:
        if tile.row != c_row:
            nodegrid.append(c_graph)
            c_row = tile.row
            c_graph = []
        c_graph.append(tile.passable)
    nodegrid.append(c_graph)
    for row in range(len(nodegrid)):
        for col in range(len(nodegrid[row])):
            neighbors = []
            for x in range(-1, 2):
                for y in range(-1, 2):
                    try:
                        if nodegrid[row+y][col+x] == True:
                            if (col+x != col) or (row+y != row):
                                neighbors.append((col+x, row+y))
                    except IndexError:
                        pass
            nodegraph[(col, row)] = neighbors
    mapdict["nodegrid"] = nodegrid
    mapdict["nodegraph"] = nodegraph
    return mapdict
            
        

