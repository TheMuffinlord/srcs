import pygame, math, random, queue
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
        self.destination = []
        self.in_transit = False
        self.next_node = None
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

    def find_a_path(self, mapdict, target):
        tw = mapdict["tilewidth"]
        th = mapdict["tileheight"]
        n_grid = mapdict["nodegrid"]
        n_graph = mapdict["nodegraph"]
        #todo: extract the node graph from the map when i call this. no reason to bring all the images and shit along
        #gist: rough out the current "node" and the target "node" then do all the pathfinding in between,
        #then return a list of destinations to go through.
        #a lot of this is red blob games code i'll freely admit.
        #right now this pathfinds okay but it gets caught up on obstacles.
        #will probably work smoother when i make an actual graph out of my node chart
        startnode = self.grid_position(mapdict)
        target_node = target.grid_position(mapdict)
        if target.grid_oob(mapdict) != True:
            print(f"well, you've done it, {target_node} is out of bounds.")
            print(f"possible moves: {n_graph[target_node]}. hope there's one!")

            least_distance = float("inf")
            best_node = None
            min_y, max_y, min_x, max_x = 0,1,0,1
            if n_graph[target_node] == []:
                best_node = target_node
                while n_graph[best_node] == []:
                    if while_stuck < 1000000:
                        while_stuck += 1
                    else:
                        raise TimeoutError(f"initial point OOB loop stuck for {self.name}. fix the map maybe?")
                    min_x-=1
                    min_y-=1
                    max_x+=1
                    max_y+=1
                    start_x = best_node[0]
                    start_y = best_node[1]
                    for y in range(min_y, max_y):
                        for x in range(min_x, max_x):
                            check_x = start_x + x
                            check_y = start_y + y
                            if check_x < 0:
                                check_x = 0
                            if check_y < 0:
                                check_y = 0
                            if check_y > len(n_grid)-1:
                                check_y = len(n_grid)-1
                            if check_x > len(n_grid[check_y])-1:
                                check_x = len(n_grid[check_y])-1
                            print(f"{check_x}, {check_y} wtf check")
                            check_node = (check_x, check_y)
                            print(f"checking {check_node}")
                            if n_graph[check_node] != [] and n_graph[check_node] != None and n_grid[check_node[1]][check_node[0]]:
                                best_node = check_node
            else:
                for node in n_graph[target_node]:
                    n_d = abs(node[0] - target_node[0]) + abs(node[1] - target_node[1])
                    if n_d < least_distance and n_grid[node[1]][node[0]] == True:
                        least_distance = n_d
                        best_node = node
            target_node = best_node
            print(f"found a suitable node at {target_node}. moves: {n_graph[target_node]}. In bounds: {n_grid[target_node[1]][target_node[0]]}")
      
        #print(f"start node: {startnode}, end node: {target_node}. distance: {coord_distance_tup(startnode, target_node)}")
        frontier = queue.PriorityQueue()
        frontier.put((0, startnode))
        cost_to_target = {}
        path_to_target = {}
        path_to_target[startnode] = None
        cost_to_target[startnode] = 0
        #tired of typing so much every check!
        p_change_x = 0
        p_change_y = 0
        while_stuck = 0
        while not frontier.empty():
            if while_stuck < 1000000:
                while_stuck += 1
            else:
                raise TimeoutError(f"frontier search loop stuck for {self.name}. trying to find path from {startnode} to {target_node}.\npath to target so far: {path_to_target}")
            current = frontier.get()[1]
            if current == target_node:
                break
            for next in n_graph[current]:
                n_change_x = abs(next[0] - current[0])
                n_change_y = abs(next[1] - current[1])
                new_cost = cost_to_target[current] + coord_distance_tup(target_node, next) + max(n_change_x, n_change_y)
                if next not in cost_to_target or new_cost < cost_to_target[next]:
                    cost_to_target[next] = new_cost
                    priority = new_cost + coord_distance_tup(target_node, next)
                    frontier.put((priority, next))
                    path_to_target[next] = current
                    p_change_x = n_change_x
                    p_change_y = n_change_y
                elif new_cost == cost_to_target[next]:
                    next_cost = cost_to_target[next] + coord_distance_tiebreaker_tup(next, target_node, startnode) + max(n_change_x, n_change_y)
                    current_cost = cost_to_target[current] + coord_distance_tiebreaker_tup(current, target_node, startnode) + max(p_change_x, p_change_y)
                    #print(f"comparing costs, {oldnew_cost} and {newer_cost}")
                    if next_cost < current_cost: #and oldnew_cost < cost_to_target[next]:
                        cost_to_target[next] = next_cost
                        priority = next_cost + coord_distance_tup(target_node, next)
                        frontier.put((priority, next))
                        path_to_target[next] = current
        
        #print(f"path to target: {path_to_target}")
        pathnode = target_node
        pathway = []
        pathway.append(((target_node[0]*tw)+(tw//2), (pathnode[1]*th)+(th//2)))                
        if pathnode not in path_to_target:
            print(f"{self.name}: invalid path node: {pathnode}. let's search for a new one")
            least_distance = float("inf")
            min_y, max_y, min_x, max_x = 0,1,0,1
            best_node = pathnode
            #print(f"beginning check, current node is {best_node}. Paths: {n_graph[best_node]}")
            while n_grid[best_node[1]][best_node[0]] != True:
                if while_stuck < 1000000:
                    while_stuck += 1
                else:
                    raise TimeoutError(f"OOB correction loop stuck for {self.name}. i have no suggestions")
                min_x-=1
                min_y-=1
                max_x+=1
                max_y+=1
                start_x = best_node[0]
                start_y = best_node[1]
                for y in range(min_y, max_y):
                    for x in range(min_x, max_x):
                        check_x = start_x + x
                        check_y = start_y + y
                        #print(f"{check_x}, {check_y} wtf check")
                        check_node = (check_x, check_y)
                        #print(f"checking {check_node}")
                        if check_node in path_to_target:
                            best_node = check_node
            pathnode = best_node
            
        while pathnode != startnode:
            if while_stuck < 1000000:
                while_stuck += 1
            else:
                raise TimeoutError(f"pathfinding loop stuck for {self.name}. trying to find path from {startnode} to {target_node}.\npath to target: {path_to_target}")
            fixed_pathnode = ((pathnode[0] * tw) + (tw//2), (pathnode[1] * th) + (th//2))
            #if n_grid[pathnode[1]][pathnode[0]] == True:
            if pathnode in path_to_target.keys():
                pathway.append(fixed_pathnode)
                #print(f"cost to node: {cost_to_target[pathnode]}")
                pathnode = path_to_target[pathnode]

        path_pings = []
        for p in pathway:
            path_pings.append(PingObject(p[0], p[1]))
        #print(f"pathfinding complete, here's the results:\n----------\n{pathway}\n----------\nfull grid:\n==========\n{path_to_target}")
        
        self.destination = pathway
        self.in_transit = False

    def grid_position(self, mapdict):
        s_node_x = int(self.position.x // mapdict["tilewidth"])
        s_node_y = int(self.position.y // mapdict["tileheight"])
        return (s_node_x, s_node_y)
    
    def grid_oob(self, mapdict):
        g_pos = self.grid_position(mapdict)
        return mapdict["nodegrid"][g_pos[1]][g_pos[0]]
    
    def grid_distance(self, target, mapdict):
        s_grid = self.grid_position(mapdict)
        t_grid = target.grid_position(mapdict)
        #return abs(s_grid[0] - t_grid[0]) + abs(s_grid[1] - t_grid[1])
        return coord_distance_tup(s_grid, t_grid)
    
    

class PingObject(RootObject):
    def __init__(self, x, y):
        super().__init__(x, y, 32)
        self.timer = 1
        self.color = "blue"

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius, 3)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.kill()

def coord_distance_tup(t_a, t_b):
    dx1 = t_a[0]
    dy1 = t_a[1]
    dx2 = t_b[0]
    dy2 = t_b[1]
    return coord_distance_xy(dx1, dy1, dx2, dy2)

def coord_distance_tiebreaker_tup(t_a, t_b, t_c):
    dx1 = abs(t_a[0] - t_b[0])
    dy1 = abs(t_a[1] - t_b[1])
    dx2 = abs(t_c[0] - t_b[0])
    dy2 = abs(t_c[1] - t_b[1])
    cross = abs(dx1*dy2 - dx2*dy1)
    h = coord_distance_tup(t_a, t_b) + (cross * 0.001)
    return h

def coord_distance_xy(x1, y1, x2, y2):
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    d_value = 1
    #dtwo_value = 1 #math.sqrt(2)
    #return d_value * (dx + dy) + (dtwo_value - 2*d_value) * min(dx, dy)
    return d_value * math.sqrt(dx * dx + dy * dy)
    

