import os
from sys import exit
from random import randint
import pygame

# Sprite Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = loadImage('player.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image,0,0.3)
        self.rect = self.image.get_rect(midbottom=(400,875))
        
        self.laser_sound = loadAudio('laser_sound.mp3')
        self.explosion = loadAudio('explosion.mp3')
        self.explosion.set_volume(0.4)
        self.lose = loadAudio('lose.wav')

    def move(self,direction):
        if self.rect.left < 20: self.rect.left = 20
        if self.rect.right > 780: self.rect.right = 780 
        if direction == 0: self.rect.x -= 10
        else: self.rect.x += 10

    def update(self):
        pass

class Laser(pygame.sprite.Sprite):
    def __init__(self,type):
        super().__init__()
        self.image = loadImage('laser.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image,90,0.5)

        ship_x_pos,ship_y_pos = PS.rect.centerx,PS.rect.centery - 10
        if type == "left": ship_x_pos -= 50
        else: ship_x_pos += 50
        self.rect = self.image.get_rect(midbottom=(ship_x_pos,ship_y_pos))

    def disappear(self):
        if self.rect.y < 0: self.kill()

    def update(self):
        self.disappear()

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = loadImage('alien.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image,0,0.3)
        self.rect = self.image.get_rect(midtop=(randint(100,700),-100))

    def disappear(self):
        global score
        if self.rect.y > 900: 
            self.kill()
            score -= 1
        
    def update(self):
        self.disappear()

# Functions to load resources
def loadImage(name):
    working_dir = os.path.dirname(__file__)
    return pygame.image.load(working_dir + "/images/" + name)

def loadAudio(name):
    working_dir = os.path.dirname(__file__)
    return pygame.mixer.Sound(working_dir + "/audio/" + name)

def loadFont(name,size):
    working_dir = os.path.dirname(__file__)
    full_path = working_dir + "/font/" + name
    return pygame.font.Font(full_path,size)

# Function to display score
def displayScore():
    global score
    if score < 0: score = 0
    score_surface = spacefont40.render(f"Score: {score}",False,'White')
    score_rect = score_surface.get_rect(center=(400,450))
    screen.blit(score_surface,score_rect)

# Setup - ADMIN
pygame.init()
pygame.display.set_caption("Shooter")
screen = pygame.display.set_mode((800,900))
spacefont90 = loadFont('spacefont.ttf',90)
spacefont40 = loadFont('spacefont.ttf',40)
game_active = False
score = 0
bg_music = loadAudio('space_music.ogg')
bg_music.set_volume(0.5)
bg_music.play()

# Setup - TIMERS
clock = pygame.time.Clock()
alien_timer = pygame.USEREVENT + 1
pygame.time.set_timer(alien_timer,2000)

# Surfaces - ACTIVE
background = loadImage('background.png').convert()
background_rect = background.get_rect(center=(400,450))

# Surfaces - NONACTIVE
title = spacefont90.render("Space Shooter",False,'White')
title_rect = title.get_rect(center = (400,200))

player_display = loadImage('player.png').convert_alpha()
player_display = pygame.transform.rotozoom(player_display,45,0.5)
player_display_rect = player_display.get_rect(center=(400,450))

laser_display = loadImage('laser.png').convert_alpha()
laser_display = pygame.transform.rotozoom(laser_display,135,0.5)
laser_display_rect = laser_display.get_rect(center=(258,415))

laser_display2 = loadImage('laser.png').convert_alpha()
laser_display2 = pygame.transform.rotozoom(laser_display2,135,0.5)
laser_display_rect2 = laser_display2.get_rect(center=(370,312))

# Sprites
player_group = pygame.sprite.GroupSingle()
player_group.add(Player())
PS = player_group.sprite
laser_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()

while True:

    keys = pygame.key.get_pressed()

    # loop to check for events
    for event in pygame.event.get():

        # QUIT event
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # TIMER event (spawn alien)
        if event.type == alien_timer:
            alien_group.add(Alien())

        # IF game is ACTIVE...
        if game_active:
            # ...SPACE event (lasers)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                PS.laser_sound.play()
                laser_group.add(Laser("left"))
                laser_group.add(Laser("right"))
        
        # IF game is NONACTIVE...
        else:
            # ...SPACE event (restart)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                alien_group.empty()
                laser_group.empty()
                score = 0
                game_active = True 

    # ACTIVE            
    if game_active:
        
        # player movement
        if keys[pygame.K_LEFT]: PS.move(0)
        elif keys[pygame.K_RIGHT]: PS.move(1)

        # laser movement
        for laser in laser_group.sprites(): laser.rect.y -= 10

        # alien movement
        for alien in alien_group.sprites(): alien.rect.y += 3

        # collision between laser/alien (score ++ )
        if pygame.sprite.groupcollide(laser_group,alien_group,True,True): 
            score += 1
            PS.explosion.play()

        # collision between player/alien (lose game)
        if pygame.sprite.spritecollide(PS,alien_group,True): 
            PS.lose.play()
            game_active = False

        # display
        screen.blit(background,background_rect)
        player_group.draw(screen)
        player_group.update()
        laser_group.draw(screen)
        laser_group.update()
        alien_group.draw(screen)
        alien_group.update()
        displayScore()

    # NONACTIVE
    else:

        # display
        screen.fill("#1e4c6a")
        screen.blit(title,title_rect)
        screen.blit(player_display,player_display_rect)
        screen.blit(laser_display,laser_display_rect)
        screen.blit(laser_display2,laser_display_rect2)

        # display score if restarting game | display message if starting game 
        if score == 0: msg = spacefont40.render("Press SPACE to start",False,'White')
        else:msg = spacefont40.render(f"Your score: {score}",False,'White')
        msg_rect = msg.get_rect(center=(400,700)) 
        screen.blit(msg,msg_rect)

    # update the whole screen every frame
    pygame.display.update()

    # set frame rate = 60 FPS
    clock.tick_busy_loop(60)
