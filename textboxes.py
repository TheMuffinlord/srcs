import pygame, math, random

from constants import *

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
