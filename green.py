from button_module import Button
from pygame import mixer
import pygame
import sys
import os
import random
import csv



pygame.init()
mixer.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
MONITOR_SIZE = [pygame.display.Info().current_w, pygame.display.Info().current_h]
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

start_bg = pygame.image.load('images/start_bg.png').convert_alpha()

#Music and audio
pygame.mixer.music.load('sounds/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1,0.0,5000)
jump_audio = pygame.mixer.Sound('sounds/jump.wav')
jump_audio.set_volume(0.5)
shot_audio = pygame.mixer.Sound('sounds/shot.wav')
shot_audio.set_volume(0.5)
bomb_audio = pygame.mixer.Sound('sounds/bomb.wav')
bomb_audio.set_volume(0.5)

#Setting up the clock
clock = pygame.time.Clock()
FSP = 60

pygame.display.set_caption("shooter game")
pygame.display.set_icon(pygame.image.load('images/player/Idle/0.png'))

#bullet
bullet_img = pygame.image.load(r'images\SpongeBullet.png').convert_alpha()
#bullet_img = pygame.image.load(r'images\bullet.png').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img,(int(bullet_img.get_width()*3),int(bullet_img.get_height()*3)))
#pygame.transform.scale(img, (int(img.get_width()*scale),int(img.get_height()*scale)))
bomb_img = pygame.image.load(r'images\bomb.png').convert_alpha()
bomb_img = pygame.transform.scale(bomb_img,(int(bomb_img.get_width()*1),int(bomb_img.get_height()*1)))
#item boxes
health_box_img = pygame.image.load('images\health_box.png')
grenade_box_img = pygame.image.load('images\grenade_box.png')
bullet_box_img = pygame.image.load(r'images/ammo_box.png')
item_boxes = {
    'health_box'     : health_box_img,
    'grenade_box'    : grenade_box_img,
    'bullet_box'     : bullet_box_img
}


pine1 = pygame.image.load('images/pine1.png').convert_alpha()
pine2 = pygame.image.load('images/pine2.png').convert_alpha()
mountain_img = pygame.image.load('images/mountain.png').convert_alpha()
sky_cloud_img = pygame.image.load('images/sky_cloud.png').convert_alpha()

start_btn = pygame.image.load('images/start_btn.png').convert_alpha()
quit_btn = pygame.image.load('images/quit_btn.png').convert_alpha()
restart_btn = pygame.image.load('images/restart_btn.png').convert_alpha()

SCROLL_THRESH = 150

moving_right = False
moving_left = False
moving_up = False
moving_down = False
shoot = False
fire_bomb = False
bomb_thrown = False
max_ammo = 30
max_bombs = 5
start_game = False
start_intro = False

BG = (50, 50, 50)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLACK = (0,0,0)
RED = (255,20,20)

GRAVITY = 0.50
ROWS = 16
COLS = 150
#TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_SIZE = 32
TILE_TYPES = 21
MAX_LEVELS = 6

screen_scroll = 0
bg_scroll = 0
level = 1

player_scale = 1.5

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'images/tile/{x}.png')
    img_list.append(img)


font = pygame.font.SysFont('Futura' , 20)
font1 = pygame.font.SysFont('Futura' , 50)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))




def draw_bg():
    screen.fill(BG)
    width1 = sky_cloud_img.get_width()
    for x in range(4):
        screen.blit(sky_cloud_img, ((x * width1)-bg_scroll * 0.5,0))
        screen.blit(mountain_img, ((x * width1)-bg_scroll * 0.7, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1, ((x * width1)-bg_scroll * 0.8, SCREEN_HEIGHT - pine1.get_height()- 150))
        screen.blit(pine2, ((x * width1)-bg_scroll * 0.9, SCREEN_HEIGHT - pine2.get_height())) 

def restart_level():
    enemy_g.empty()
    bullet_g.empty()
    bomb_g.empty()
    explosion_g.empty()
    item_box_g.empty()
    decoration_g.empty()
    water_g.empty()
    exit_g.empty()

    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data



class Soldier(pygame.sprite.Sprite):
    def __init__(self,character,x,y,scale,speed, ammo, bombs):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.chara = character
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.bombs = bombs
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.velocity_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.time_passed = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0,200,20)
        self.idling = False
        self.idling_counter = 0
        
        #load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []
            #count number of files in the folder
            n = len(os.listdir(f'images\{self.chara}\{animation}'))
            for i in range(n):
                img = pygame.image.load(f'images\{self.chara}\{animation}\{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()*scale),int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        

        self.img = self.animation_list[self.action][self.frame_index]
        self.rect = self.img.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.player_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0
        if moving_right:
            dx += self.speed      
            self.flip = False
            self.direction = 1
        if moving_left:
            dx -= self.speed
            self.flip = True
            self.direction = -1
            
        #jump
        if self.jump == True and self.in_air == False:
            self.velocity_y = -11
            self.jump = False
            self.in_air = True

        #applying gravity 
        self.velocity_y += GRAVITY
        
        if self.velocity_y > 10:
            self.velocity_y
        dy += self.velocity_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.img.get_width(), self.img.get_height()):
                dx = 0
                #for ai to chande direction
                if self.chara == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0

            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.img.get_width(), self.img.get_height()):
                if self.velocity_y < 0:
                    self.velocity_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.velocity_y >= 0:
                    self.velocity_y = 0
                    dy = tile[1].top - self.rect.bottom
                    self.in_air = False
    
        if pygame.sprite.spritecollide(self, water_g, False):
            self.health = 0

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_g, False):
            level_complete = True

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0
            
        
        if self.chara == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
        
        self.rect.x += dx
        self.rect.y += dy

        #Scrolling
        if self.chara == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length*TILE_SIZE)-SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 30
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * self.direction*0.5) , self.rect.centery, self.direction)
            bullet_g.add(bullet)
            #ammo reduction
            self.ammo -= 1
            shot_audio.play()


    def AI(self):
        if self.alive and soldier.alive:
            if self.idling == False and random.randint(1, 100) == 1:
                self.update_action(0)#0: idle
                self.idling = True
                self.idling_counter = 50
                #check if the ai is near the player
            if self.vision.colliderect(soldier.rect):
                #stop running and face the player
                self.update_action(0)#0 idle
                #shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction  == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction,self.rect.centery)
                    
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1

                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll

    def player_animation(self):
        #animation frame
        frame_time = 100
        self.img = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.time_passed > frame_time:
            self.time_passed = pygame.time.get_ticks()
            #self.img = self.animation_list[self.action][self.frame_index]
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]) - 1:
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
    
    def update_action(self,action):
        if self.action != action:
            self.action = action
            self.frame_index = 0
            self.time_passed = pygame.time.get_ticks()
    
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.img,self.flip,False), self.rect)
        #pygame.draw.rect(screen, bg, self.rect,1)


                    
class Itembox(pygame.sprite.Sprite):
    def __init__(self, item_type,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height())) 

    def update(self):
        self.rect.x += screen_scroll
        #check if player has picked item box
        if pygame.sprite.collide_rect(self, soldier):
            if self.item_type == 'health_box':
                soldier.health += 20
                if soldier.health >= soldier.max_health:
                    soldier.health = 100
            elif self.item_type == 'bullet_box':
                soldier.ammo += 20
                if soldier.ammo >= max_ammo:
                    soldier.ammo = max_ammo
            elif self.item_type == 'grenade_box':
                soldier.bombs += 2
                if soldier.bombs >= max_bombs:
                    soldier.bombs = max_bombs
            self.kill()

        


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height())) 

    def update(self):
        self.rect.x += screen_scroll
        
class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height())) 
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll


    
class HealthBar():
    def __init__(self, x,y,health,max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 15
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(soldier, bullet_g, False):
            if soldier.alive:
                soldier.health -= 5
                self.kill()
        for enemy in enemy_g:
            if pygame.sprite.spritecollide(enemy, bullet_g, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()



class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.velocity_y = -11
        self.speed = 7
        self.image = bomb_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.velocity_y += GRAVITY
        dx = self.direction * self.speed 
        dy = self.velocity_y

        #check collision with level
        for tile in world.obstacle_list:
            #check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y,self.image.get_width(),self.image.get_height()):
                self.direction *= -1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.image.get_width(),self.image.get_height()):
                self.speed = 0
                #thrown up
                if self.velocity_y < 0:
                    self.velocity_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check falling
                elif self.velocity_y >= 0:
                    self.velocity_y = 0
                    dy = tile[1].top - self.rect.bottom
        

        #update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            bomb_audio.play()
            explosion = Explosion(self.rect.x, self.rect.y, 1) 
            explosion_g.add(explosion)
            #do damage to anyone that is nearby
            if abs(self.rect.centerx - soldier.rect.centerx) < TILE_SIZE * 3 and \
                abs(self.rect.centery - soldier.rect.centery) < TILE_SIZE * 3:
                soldier.health -= 50
            for enemy in enemy_g:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 3 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 3:
                    enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(0, 4):
            img = pygame.image.load(f'images/explosion/e{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        #update explosion amimation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]



start_button = Button(SCREEN_WIDTH/2-150,SCREEN_HEIGHT//2-150,start_btn,1)
quit_button = Button(SCREEN_WIDTH/2-150,SCREEN_HEIGHT//2+50,quit_btn,1)
restart_button = Button(SCREEN_WIDTH/2-150,SCREEN_HEIGHT//2-150,restart_btn,1)

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:#whole screen fade
            pygame.draw.rect(screen , self.colour, (0-self.fade_counter,0,SCREEN_WIDTH//2,SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour,(SCREEN_WIDTH//2+self.fade_counter,0,SCREEN_WIDTH,SCREEN_HEIGHT))
            pygame.draw.rect(screen,self.colour, (0,0-self.fade_counter,SCREEN_WIDTH,SCREEN_HEIGHT//2))
            pygame.draw.rect(screen,self.colour, (0,SCREEN_HEIGHT//2 + self.fade_counter,SCREEN_WIDTH,SCREEN_HEIGHT))
        if self.direction == 2:#Vertical screen down:
            pygame.draw.rect(screen, self.colour, (0,0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
            return fade_complete

start_fade = ScreenFade(1,(20,20,20),15)
death_fade = ScreenFade(2, (200,80,80),15)

enemy_g = pygame.sprite.Group()
bullet_g = pygame.sprite.Group()
bomb_g = pygame.sprite.Group()
explosion_g = pygame.sprite.Group()
item_box_g = pygame.sprite.Group()
decoration_g = pygame.sprite.Group()
exit_g = pygame.sprite.Group()
water_g = pygame.sprite.Group()
#temp




#soldier = Soldier('player',300,400,3,5,max_ammo,max_bombs)
#health_bar = HealthBar(10, 10, soldier.health, soldier.health)
#enemy = Soldier('enemy',300,446,3,5,200,50)
#enemy2 = Soldier('enemy',600,446,3,5,200,50)
#print(len(solider.animation_list),len(solider.animation_list[0]),len(solider.animation_list[1]))
#enemy_g.add(enemy)
#enemy_g.add(enemy2)

world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv' , newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            if y < 150:
                world_data[x][y] = int(tile)



#print(world_data)
class World():
    def __init__(self):
        self.obstacle_list = []
    
    def process_data(self, data):
        self.level_length = len(data[0])
        for y , row in enumerate(data):
            for x , tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x*TILE_SIZE
                    img_rect.y = y*TILE_SIZE
                    tile_data = (img,img_rect)
                    if tile >= 0 and tile <=8 :
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile<=10:
                        water = Water(img,x*TILE_SIZE,y*TILE_SIZE)
                        water_g.add(water)
                    elif tile>=11 and tile<=14:
                        decoration = Decoration(img,x*TILE_SIZE,y*TILE_SIZE)
                        decoration_g.add(decoration)
                    elif tile == 15:#create player
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, player_scale, 6, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:#enemy
                        enemy = Soldier('enemy',x*TILE_SIZE,y*TILE_SIZE,player_scale,5,200,50)
                        enemy_g.add(enemy)
                    elif tile == 17:#ammo
                        item_box2 = Itembox('bullet_box',x*TILE_SIZE,y*TILE_SIZE)
                        item_box_g.add(item_box2)
                    elif tile == 18:#bomb
                        item_box1 = Itembox('grenade_box',x*TILE_SIZE,y*TILE_SIZE)
                        item_box_g.add(item_box1)
                    elif tile == 19:#health
                        item_box = Itembox('health_box', x*TILE_SIZE,y*TILE_SIZE)
                        item_box_g.add(item_box)
                    elif tile == 20:#exit btn
                        exit = Exit(img,x*TILE_SIZE,y*TILE_SIZE)
                        exit_g.add(exit)

        return player, health_bar
        
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

world = World()
soldier, health_bar = world.process_data(world_data)





while True:
    clock.tick(FSP)

    if start_game == False:
        screen.blit(start_bg,(0,0))
        #add btn
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if quit_button.draw(screen):
            sys.exit()
    else:
        draw_bg()
        world.draw()
        health_bar.draw(soldier.health)
        #show ammo
        draw_text(f'AMMO ' , font, WHITE, 10, 35)
        for ammo in range(soldier.ammo):
            screen.blit(pygame.transform.rotate(bullet_img,90), ((55 + ammo*6), 38))
        #show bombs
        draw_text(f'GRENADES ' , font, WHITE, 10, 55)
        for bomb1 in range(soldier.bombs):
            screen.blit(bomb_img, ((84 + bomb1*15), 53))
        #show level
        draw_text(f'LEVEL : {level}', font, WHITE, SCREEN_WIDTH//2,10)


        
    

        
        #enemy.draw()

        #enemy.update()

        for enemy in enemy_g:
            enemy.AI()
            enemy.update()
            enemy.draw()
        
        soldier.draw()
        soldier.move(moving_left,moving_right)
        soldier.update()

    
        decoration_g.update()
        water_g.update()
        exit_g.update()
        item_box_g.update()
        item_box_g.draw(screen)
        decoration_g.draw(screen)
        water_g.draw(screen)
        exit_g.draw(screen)
        bullet_g.update()
        bomb_g.update()
        explosion_g.update()
        bullet_g.draw(screen)
        bomb_g.draw(screen)
        explosion_g.draw(screen)
        

        if start_intro == True:
            if start_fade.fade():
                start_intro = False
                start_fade.fade_counter = 0
        

        # enemy.move(moving_left,moving_right)
        if soldier.alive:
            if shoot:
                soldier.shoot()
            elif fire_bomb and bomb_thrown == False and soldier.bombs > 0:
                bomb = Bomb(soldier.rect.centerx + (0.5*soldier.rect.size[0]*soldier.direction), soldier.rect.centery, soldier.direction)
                bomb_g.add(bomb)
                #bombs thrown
                soldier.bombs -= 1
                bomb_thrown = True
            if moving_right and moving_left:         
                soldier.update_action(0)
            elif soldier.in_air or soldier.jump == True:
                soldier.update_action(2)
            elif moving_right or moving_left:
                soldier.update_action(1)
            else:
                soldier.update_action(0)
            screen_scroll, level_complete = soldier.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = restart_level()
                if level <= MAX_LEVELS:
                    if level >= MAX_LEVELS:
                        pass
                    else:
                        with open(f'level{level}_data.csv' , newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    if y <150:
                                        world_data[x][y] = int(tile)
                        world = World()
                        soldier, health_bar = world.process_data(world_data)
                    
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = restart_level()
                    with open(f'level{level}_data.csv' , newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                if y<150:
                                    world_data[x][y] = int(tile)
                    world = World()
                    soldier, health_bar = world.process_data(world_data)

    if level >= MAX_LEVELS:
        screen.blit(start_bg,(0,0))
        draw_text('YOU HAVE COMPLETED THE GAME', font1 , WHITE,12, 20 )
        if quit_button.draw(screen):
            sys.exit()
        if restart_button.draw(screen):
            level = 1
            death_fade.fade_counter = 0
            start_intro = True
            bg_scroll = 0
            world_data = restart_level()
            with open(f'level{level}_data.csv' , newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        if y<150:
                            world_data[x][y] = int(tile)
                
            world = World()
            soldier, health_bar = world.process_data(world_data)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                fire_bomb = True
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = True
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = True  
            elif event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_w and soldier.alive:
                soldier.jump = True
                jump_audio.play()
        
        
        

            

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = False
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = False

            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                fire_bomb = False  
                bomb_thrown = False
                soldier.alive = True



    pygame.display.flip()











"""
import pygame
import sys
import os

pygame.init()

screen = pygame.display.set_mode((800,600))


#Setting up the clock
clock = pygame.time.Clock()
FSP = 60

pygame.display.set_caption("shooter game")

#bullet
bullet_img = pygame.image.load(r'images\bullet.png').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img,(int(bullet_img.get_width()*5*1.5),int(bullet_img.get_height()*1.5*5)))
#pygame.transform.scale(img, (int(img.get_width()*scale),int(img.get_height()*scale)))
bomb_img = pygame.image.load(r'images\bomb.png').convert_alpha()
bomb_img = pygame.transform.scale(bomb_img,(int(bomb_img.get_width()*3),int(bomb_img.get_height()*3)))

moving_right = False
moving_left = False
moving_up = False
moving_down = False
shoot = False
bomb = False

BG = (50, 50, 50)

GRAVITY = 0.75


def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, (255, 0, 0),(0,500),(SCREEN_WIDTH,500))

class Soldier(pygame.sprite.Sprite):
    def __init__(self,character,x,y,scale,speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.chara = character
        self.alive = True 
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.jump = False
        self.in_air = True
        self.velocity_y = 0
        self.direction = 1
        self.shoot_cooldown = 0
        self.ammo = ammo
        self.start_ammo = ammo 
        self.health = 100
        self.max_health = self.health
        self.time_passed = pygame.time.get_ticks()
        animation_type = ['Idle', 'Run' , 'Jump', 'Death']
        for animation in animation_type:
            temp_list = []
            n = len(os.listdir(f'images\{self.chara}\{animation}'))
            for i in range(n):
                img = pygame.image.load(f'images\{self.chara}\{animation}\{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()*scale),int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)      
        self.img = self.animation_list[self.action][self.frame_index]    
        self.rect = self.img.get_rect()
        self.rect.center = (x,y)
        self.speed = speed
        self.flip = False

    def update(self):
        self.player_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        if moving_right:
            dx += self.speed      
            self.flip = False
            self.direction = 1
        if moving_left:
            dx -= self.speed
            self.flip = True
            self.direction = -1
            
   
        #jump
        if self.jump == True and self.in_air == False:
            self.velocity_y = -15
            self.jump = False
            self.in_air = True

        #applying gravity 
        self.velocity_y += GRAVITY
        
        if self.velocity_y > 10:
            self.velocity_y = 10
        dy += self.velocity_y

        if self.rect.bottom + dy > 450:
            dy = 450 - self.rect.bottom
            self.in_air = False
        
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 40
            if soldier.direction == 1:
                bullet = Bullet(self.rect.centerx + (0.1 * self.rect.size[0] * self.direction) + 28*3-10, soldier.rect.centery+((self.rect.y)/8), soldier.direction)        
            elif soldier.direction == -1:
                bullet = Bullet(self.rect.centerx - 28*3+0, self.rect.centery+((self.rect.y)/8), self.direction)
            bullet_g.add(bullet)
            #ammo reduction
            self.ammo -= 1

    def player_animation(self):
        #animation frame
        frame_time = 100
        self.img = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.time_passed > frame_time:
            self.time_passed = pygame.time.get_ticks()
            self.img = self.animation_list[self.action][self.frame_index]
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]) - 1:
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
            
        

    
    def update_action(self,action):
        if self.action != action:
            self.action = action
            self.frame_index = 0

    
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.img,self.flip,False), self.rect.center)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.direction,False), self.rect.center)
        

    def update(self):
        #bullet move
        self.rect.x += (self.direction * self.speed)
        #check if bullet disapear in a distance
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.kill()

 #collision check with npc
        if pygame.sprite.spritecollide(soldier, bullet_g, False):
            if soldier.alive:
                soldier.health -= 5
                self.kill()
                print(soldier,soldier.health,0)

        if pygame.sprite.spritecollide(enemy, bullet_g, False):
            if enemy.alive:
                enemy.health -= 30
                self.kill()
                print(enemy,enemy.health,1)

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.velocity_y = -11
        self.speed = 7
        self.image = bomb_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction


       


bullet_g = pygame.sprite.Group()
bomb_g = pygame.sprite.Group()
        
soldier = Soldier('player',300,400,3,10,20)
enemy = Soldier('enemy',200,400,3,3, 20) 
#print(len(solider.animation_list),len(solider.animation_list[0]),len(solider.animation_list[1]))

while True:
    clock.tick(FSP)
    draw_bg()
    
    enemy.draw()
    soldier.draw()
    soldier.move(moving_left,moving_right)
    soldier.update()
    enemy.update()
    

    bullet_g.update()
    bomb_g.update()
    bullet_g.draw(screen)
    bomb_g.draw(screen)
   
    
    

    # enemy.move(moving_left,moving_right)
    if soldier.alive:
        if shoot:
            soldier.shoot()
        elif bomb:
            bomb = Bomb(soldier.rect.centerx + (0.5 * soldier.rect.size[0] * soldier.direction), soldier.rect.centery, soldier.direction)
            bomb_g.add(bomb)
        if moving_right and moving_left:              
            soldier.update_action(0)
        elif soldier.in_air or soldier.jump == True:
            soldier.update_action(2)
        elif moving_right or moving_left:
            soldier.update_action(1)
        else:
            soldier.update_action(0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = True
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = True  
            elif event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_w and soldier.alive or event.key == pygame.K_UP:
                soldier.jump = True
            
            if event.key == pygame.K_SPACE:
                shoot = True

            elif event.key == pygame.K_q:
                bomb = True
           
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = False
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = False

            if event.key == pygame.K_SPACE:
                shoot = False

            elif event.key == pygame.K_q:
                bomb = False
             

    pygame.display.flip()



"""