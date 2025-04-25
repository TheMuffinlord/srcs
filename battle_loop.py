import pygame, math, random
from constants import *
from enum import Enum

def kbd_interpreter(pressed_key):
    global PlayerGroup
    toggle_unit = 0
    match(pressed_key):
        case pygame.K_1:
            toggle_unit = 1
        case pygame.K_2:
            toggle_unit = 2
    for unit in PlayerGroup:
        if unit.unit_number == toggle_unit:
            toggle_selection(unit)
        

def toggle_selection(unit):
    global SelectionGroup
    if SelectionGroup.has(unit):
        print(f"removing {unit.name} from selected units")
        SelectionGroup.remove(unit)
        unit.selected = False
    else:
        print(f"adding {unit.name} to selected units")
        SelectionGroup.add(unit)
        unit.selected = True
    
def mouse_interpreter(clicked_position, clicked_button):
    global SelectionGroup
    if clicked_button[0] or clicked_button[1]:
        go_here = SelectionCursor(clicked_position[0], clicked_position[1])
        for unit in SelectionGroup:
            unit.destination = go_here
            print(f"setting {unit.name} destination to {unit.destination.position}")
            toggle_selection(unit)        

# classes go in here

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

    def push_away(self, dt, vector, strength):
        self.position += vector * strength * dt

    def find_angle(self, target):
        angle = math.atan2(self.position.y -target.position.y, self.position.x - target.position.x)
        degrees = math.degrees(angle)+90
        while degrees < 180:
            degrees += 360
        while degrees > 180:
            degrees -= 360
        return degrees

class SelectionCursor(RootObject):
    def __init__(self, x, y):
        super().__init__(x, y, SELECTION_RADIUS)
        self.color = pygame.color.Color(0,255,0)
        global SelectionGroup
        self.selected_units = SelectionGroup.copy()
        self.in_use = True
        
    
    def draw(self, screen):
        return pygame.draw.circle(screen, self.color, self.position, self.radius, 3)

    def update(self, *args):
        if self.color.g > 0:
            self.color.g -= 5
        if self.color.g <= 0:
            if self.color.r < 250:
                self.color.r += 5
            self.in_use = False
        for unit in self.selected_units:
            if unit.destination == self:
                self.in_use = True
        if self.in_use == False:
            self.kill()
        
class ValidMovements(Enum):
    FollowEnemy = "following enemy"
    FollowAlly = "following ally/squad"
    AvoidHostile = "avoiding hostiles"
    AvoidObject = "moving around object"
    MoveToCursor = "moving to destination"
    WanderAround = "searching"
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

    def update(self, dt):
        self.timer -= dt
        self.Equipment_Check()
        self.Find_Target()
        self.Fire_At_Will(dt)
        self.Move_Closer(dt)
        
        
    def Equipment_Check(self):
        self.movespeed = self.equipment[0].move_speed
        self.turnspeed = self.equipment[0].turn_speed
        self.shot_diff = self.equipment[1].shot_diff

    def take_damage(self, damage):
        #print(self.timer)
        if self.timer <= 0:
            lines = [
                "!!UNIT DAMAGED!!",
                f"!!{damage} DAMAGE!!",
            ]
            dmgbox = DamageAlertBox(self, lines)
            self.health -= damage
            #print(f"{self.name} health: {self.health}")
            self.timer = HIT_COOLDOWN
            #print(f"time to next hit: {self.timer}")
        #else:
            #print(f"too soon for {self.name} to take damage")
        if self.health <= 0:
                #print("something broke")
                self.Something_Broke()

    def Find_Target(self):
        global EnemyGroup
        #print(f"searching for enemies in {self.sight_range} radius")
        target_range = RootObject(self.position.x, self.position.y, self.sight_range)
        valid_targets = []
        for unit in EnemyGroup:
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
            #print(EnemyGroup)
            self.current_target = None

    def aim_rotate(self, dt):
        degrees = self.find_angle(self.current_target)
        if degrees < self.aim_rotation:
            self.aim_rotation += self.rotation_speed * (-1 * dt)
        elif degrees > self.aim_rotation:
            self.aim_rotation += self.rotation_speed * dt
        #print(f"current rotation: {self.aim_rotation}, angle of target: {degrees}")
       
    def Move_Closer(self, dt):
        global PlayerGroup, EnemyGroup #gotta think about this one
        if self.destination != None:
            #print("moving to destination")
            degrees = self.find_angle(self.destination)
            if degrees < self.rotation:
                self.rotate(dt * -1)
            elif degrees > self.rotation:
                self.rotate(dt)
            if self.collision(self.destination) == False:
                self.move(dt)
            else:
                self.destination = None
        
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
            break_text = [
                f"!!BROKEN!!",
                f"{self.equipment[break_roll].short_form()}",
                f"!!BROKEN!!"
            ]
            break_box = DamageAlertBox(self, break_text)
            self.health = self.maxhealth

    def Unit_Destroyed(self):
        sad_end = [
            "ALERT ALERT ALERT UH OH",
            f"UNIT {self.name}",
            "!!!!!DESTROYED!!!!!"
        ]
        sad_box = DamageAlertBox(self, sad_end)
        self.kill()
        #put a big explosion here or something, i dunno
        

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
    
    def __repr__(self):
        return f"Primary Weapon: Minigun, {self.shot_diff*2} degree arc, {self.rate_of_fire} shot timer; intact: {self.intact}"

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
        

    def Start_Shooting(self, dt, direction, b_x, b_y):
        if self.timer <= 0:
            bullet = BasicBullet(b_x, b_y, direction * BASIC_BULLET_VELOCITY)
            self.timer = self.rate_of_fire
        self.timer -= dt

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
        self.current_movement = ValidMovements.WanderAround
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

    def update(self, dt):
        global BulletGroup
        self.timer -= dt
        self.Movement_Choice(dt)
        self.Find_Target()
        for bullet in BulletGroup:
            self.check_bullet(bullet, dt)
        if self.destination and self.collision_rough(self.destination) == True and self.destination.can_damage == True:
            self.destination.take_damage(self.damage_value)
            #print(f"{self.name} tried to hit {self.destination.name}")
            if self.destination.alive() == False:
                self.destination = None
                self.current_movement = ValidMovements.WanderAround
                self.current_target = None
        

    def check_bullet(self, bullet, dt):
        if self.collision(bullet):
            bullet.kill()
            self.take_damage(bullet, dt)
            self.push_away(dt, bullet.velocity, bullet.knockback)
        

    def take_damage(self, source, dt):
        if self.timer <= 0:
            #print(f"took {damage} damage")
            self.color = "white"
            self.health -= source.damage
            self.timer = HIT_COOLDOWN
            if self.health <= 0:
                self.kill()
                if self.spawner != None and self.spawner.alive():
                    self.spawner.health += ENEMY_MAX_HEALTH // 2
                    self.spawner.color = "green"

                
                
                

    def Movement_Choice(self, dt):
        match self.current_movement:
            case ValidMovements.WanderAround:
                self.Wander_Around(dt)
            case ValidMovements.FollowEnemy:
                self.Move_Closer(dt)

    def Find_Target(self):
        global PlayerGroup
        if self.destination == None:
            target_range = RootObject(self.position.x, self.position.y, self.sight_range)
            valid_targets = []
            for unit in PlayerGroup:
                if target_range.collision(unit):
                    valid_targets.append(unit)
            if len(valid_targets) > 0:
                c_distance = float('inf')
                for target in valid_targets:
                    #print(f"target found: {target.name}")
                    target_dist = pygame.math.Vector2.distance_to(pygame.Vector2(target.position.x, target.position.y), self.position)
                    if target_dist < c_distance:                      
                        c_distance = target_dist
                        #print(f"set target {target.name} as target. distance to target {c_distance}")
                        self.destination = target
                self.current_movement = ValidMovements.FollowEnemy
                self.sight_range = ENEMY_DETECTION_RANGE
            else:
                self.destination = None
                self.sight_range += 10
                self.current_movement = ValidMovements.WanderAround
        
        
    def Move_Closer(self, dt):
        degrees = self.find_angle(self.destination)
        if self.rotation > degrees:
            self.rotate(dt*-1)
        elif self.rotation < degrees:
            self.rotate(dt)
        if self.collision(self.destination) == False:
            self.move(dt)    

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
        self.maxhealth = ENEMY_MAX_HEALTH*SPAWNER_MULTIPLIER
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
    
    def update(self, dt):
        global BulletGroup
        self.timer -= dt
        self.spawn_timer -= dt
        for bullet in BulletGroup:
            self.check_bullet(bullet)
        if self.color == "white" and self.timer < HIT_COOLDOWN - 0.1:
            self.color = "red"
        if self.health > ENEMY_MAX_HEALTH:            
            self.enemy_spawn()

    def check_bullet(self, bullet):
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
    
    def enemy_spawn(self):
        if self.spawn_timer < 0:
            self.health -= ENEMY_MAX_HEALTH
            new_enemy = EnemyUnit(self.position.x, self.position.y)
            new_enemy.add(self.groups())
            new_enemy.spawner = self
            new_enemy.rotation = random.randrange(0,360)
            new_enemy.name += f" #{self.health}"
            global PlayerGroup
            new_enemy.valid_targets = PlayerGroup
            self.spawn_timer = SPAWN_COOLDOWN

class TextBoxObject(pygame.sprite.Sprite):
    def __init__(self, origin_x, origin_y, width, height, lines: list):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.text_font = pygame.font.get_default_font() #overwrite in subclasses
        self.text_size = 12 #overwrite in subclasses
        self.text_object = pygame.font.Font(self.text_font, self.text_size)
        self.text_color = "white"
        self.x = origin_x
        self.y = origin_y
        max_w = width
        max_h = height
        overall_h = 0
        for line in lines:
            line_text = self.text_object.render(line, True, self.text_color)
            line_w, line_h = line_text.get_size()
            if line_w > max_w:
                max_w = line_w + 10
            overall_h += line_h + 2 #these probably need to be constants eventually
            if overall_h > max_h:
                max_h = overall_h + 10
        self.width = max_w
        self.height = max_h
        self.color = "white"
        #self.box = pygame.rect.Rect(self.x, self.y, self.width, self.height) #initial location
        self.lines = lines
        
        
    def draw(self, screen):
        pass

    def update(self, dt):
        pass

class DamageAlertBox(TextBoxObject):
    def __init__(self, o_sprite: pygame.sprite.Sprite, lines: list):
        super().__init__(o_sprite.position.x, o_sprite.position.y - DAMAGE_ALERT_WIDTH, DAMAGE_ALERT_WIDTH, DAMAGE_ALERT_HEIGHT, lines)
        self.owner = o_sprite
        self.x = self.owner.position.x
        self.y = self.owner.position.y - DAMAGE_ALERT_HEIGHT
        self.color = "yellow"
        self.timer_start = 3
        self.timer = 0
        self.lifespan = DAMAGE_ALERT_LIFESPAN

    def draw(self, screen):
        self.box = pygame.rect.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, self.box, 2)
        start_y = self.y + 5
        for line in self.lines:
            line_text = self.text_object.render(line, True, self.text_color)
            y_diff = line_text.get_size()[1]
            start_x = self.box.centerx - (line_text.get_width() // 2)
            screen.blit(line_text, (start_x, start_y))
            start_y += y_diff

    def update(self, dt):
        if self.timer < 0:
            self.timer = self.timer_start
            if self.color == "yellow":
                self.color = "red"
            elif self.color == "red":
                self.color = "yellow"
        self.timer -= 1
        self.lifespan -= dt
        #self.x = self.owner.position.x
        #self.y = self.owner.position.y - DAMAGE_ALERT_HEIGHT
        if self.lifespan <= 0:
            self.kill()

# main battle loop

def battle_mode(screen):
    clock = pygame.time.Clock()
    dt = 0

    #create the map, populate with units

    loop_updatable = pygame.sprite.Group()
    loop_drawable = pygame.sprite.Group()
    global EnemyGroup, PlayerGroup, BulletGroup, SelectionGroup
    EnemyGroup = pygame.sprite.Group()
    PlayerGroup = pygame.sprite.Group()
    BulletGroup = pygame.sprite.Group()
    SelectionGroup = pygame.sprite.Group()

    PlayerRobot.containers = (loop_updatable, loop_drawable, PlayerGroup)
    EnemyUnit.containers = (loop_updatable, loop_drawable, EnemyGroup)
    BasicBullet.containers = (loop_updatable, loop_drawable, BulletGroup)
    EnemySpawner.containers = (loop_updatable, loop_drawable, EnemyGroup)
    SelectionCursor.containers = (loop_updatable, loop_drawable)
    TextBoxObject.containers = (loop_updatable, loop_drawable)

    Player = PlayerRobot(250, 300, "john character", 1)
    Player2 = PlayerRobot(250, 650, "jane character", 2)
    
    Spawner = EnemySpawner(900, 500)
    Spawner2 = EnemySpawner(900, 200)

    action_waiting = False
    kbd_waiting = False
    mouse_waiting = False
    
    game_running = True


    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN: #going to have to put mouse logic in ehre too
                pressed_key = event.key
                action_waiting = True
                kbd_waiting = True
                if mouse_waiting == True:
                    print("keyboard overriding mouse") #good enough for debug!
                    mouse_waiting = False
                if pressed_key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #targeting logic, break out
                clicked_location = pygame.mouse.get_pos()
                clicked_button = pygame.mouse.get_pressed()
                print(f"clicked at {clicked_location}")
                action_waiting = True
                mouse_waiting = True
                if kbd_waiting == True:
                    print("mouse overriding keyboard")
                    kbd_waiting = False
            if action_waiting == True:
                print("action caught")
                if mouse_waiting == True:
                    mouse_interpreter(clicked_location, clicked_button)
                    action_waiting = False
                    mouse_waiting = False
                elif kbd_waiting == True:
                    kbd_interpreter(pressed_key)
                    action_waiting = False
                    kbd_waiting = False
                else: 
                    action_waiting = False
                    print("some other action took place?")

        pygame.Surface.fill(screen, "black")

        for item in loop_updatable:
            item.update(dt)
        
        for item in loop_drawable:
            item.draw(screen)    


        pygame.display.flip()
        dt = clock.tick(60)/1000      