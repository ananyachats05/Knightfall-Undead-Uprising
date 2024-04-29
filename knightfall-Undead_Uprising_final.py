import pygame, random #edit added csv
from csv import *
#idea - add invincibility if possible refer 136 line
#defining vectors for kinematic motions

#edit : 162 , pausegame() ,172 ,176 , 212 pe text , added highscore bottom game class
vector = pygame.math.Vector2
pygame.init()

#Setting display surface (tile size 32x32)
WINDOW_WIDTH = 1280   # 1280/32 = 40
WINDOW_HEIGHT = 736   # 736/32 = 23
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Knightfall: Undead Uprising")

ping = 60
clock = pygame.time.Clock()

class Game():
    """Container for all the game functons"""
    def __init__(self, player, zombie_group, platform_group, portal_group, bullet_group, ruby_group):
        
        self.STARTING_ROUND_TIME = 60
        self.STARTING_ZOMBIE_CREATION_TIME = 5
        self.CLOCK = 0 #edit added clock 

        #intial values
        self.score = 0
        self.round_number = 1
        self.frame_count = 0
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME
        self.clock = self.CLOCK

        self.title_font = pygame.font.Font("fonts\Poultrygeist.ttf", 81)
        self.HUD_font = pygame.font.Font("fonts/Pixel.ttf", 24)

        self.lost_ruby_sound = pygame.mixer.Sound("sounds/lost_ruby.wav")
        self.ruby_pickup_sound = pygame.mixer.Sound("sounds/ruby_pickup.wav")
        pygame.mixer.music.load("sounds/BossMain.wav")

        #Attaching sprite groups
        self.player = player
        self.zombie_group = zombie_group
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group
        self.ruby_group = ruby_group


    def update(self):
        
        self.frame_count += 1
        if self.frame_count % ping == 0:
            self.round_time -= 1
            self.frame_count = 0
            self.clock +=1   # for every 15 sec , make zombies faster(randomly) refer 104 and zombie class

        self.check_collisions()
        self.add_zombie()
        self.check_round_completion()
        self.check_game_over()


    def draw(self):
        
        #constant colour palette
        WHITE = (255, 255, 255)
        MONZA = (208, 12, 17)
        GREEN = (25,200,25)

    
        score_text = self.HUD_font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, WINDOW_HEIGHT - 50)

        health_text = self.HUD_font.render("Health: " + str(self.player.health), True, WHITE)
        health_rect = health_text.get_rect()
        health_rect.topleft = (10, WINDOW_HEIGHT - 25)

        title_text = self.title_font.render("Knightfall", True, MONZA)
        title_rect = title_text.get_rect()
        title_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT - 33)

        round_text = self.HUD_font.render("Apocalypse: " + str(self.round_number), True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 50)

        time_text = self.HUD_font.render("Sunrise In: " + str(self.round_time), True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 25)

        #blitting the HUD and title
        display_surface.blit(score_text, score_rect)
        display_surface.blit(health_text, health_rect)
        display_surface.blit(title_text, title_rect)
        display_surface.blit(round_text, round_rect)
        display_surface.blit(time_text, time_rect)
        

    def add_zombie(self):

        #Checking every second
        if self.frame_count % ping == 0:
            #adding zombie past default 5 seconds
            if self.round_time % self.zombie_creation_time == 0:
                zombie = Zombie(self.platform_group, self.portal_group, self.round_number, 5 + self.round_number) #edit to 5+ self.clock%15
                self.zombie_group.add(zombie)


    def check_collisions(self):
        
        #Seeing if any bullet in the bullet group hit a zombie in the zombie group
        collision_dict = pygame.sprite.groupcollide(self.bullet_group, self.zombie_group, True, False)
        if collision_dict:
            for i in collision_dict.values():
                for zombie in i:
                    zombie.hit_sound.play()
                    zombie.is_dead = True
                    zombie.animate_death = True
        
        #collision detection between player and zombie
        collision_list = pygame.sprite.spritecollide(self.player, self.zombie_group, False)
        if collision_list:
            for zombie in collision_list:
                #The zombie is hit, go over it to generate ruby
                if zombie.is_dead == True:
                    zombie.kick_sound.play()
                    zombie.kill()
                    self.score += 10

                    ruby = Ruby(self.platform_group, self.portal_group)
                    self.ruby_group.add(ruby)
                #The zombie isn't dead, so take damage
                else:
                    self.player.health -= 20
                    self.player.hit_sound.play()
                    #Move the player to not continually take damage
                    self.player.position.x -= 256*zombie.direction  #idea add invincibility if possible
                    self.player.rect.bottomleft = self.player.position

        #player ruby collision
        # ruby collection means increase in score by 20 and life by 5
        if pygame.sprite.spritecollide(self.player, self.ruby_group, True):
            self.ruby_pickup_sound.play()
            self.score += 20
            self.player.health += 5
            #max health cap is 100
            if self.player.health > self.player.STARTING_HEALTH:
                self.player.health = self.player.STARTING_HEALTH

        #zombie-ruby collision
        for zombie in self.zombie_group:
            if zombie.is_dead == False:
                #zombie won't disappear, the ruby would; new zombie generated
                if pygame.sprite.spritecollide(zombie, self.ruby_group, True):
                    self.lost_ruby_sound.play()
                    zombie = Zombie(self.platform_group, self.portal_group, self.round_number, 5 + self.round_number)
                    self.zombie_group.add(zombie)


    def check_round_completion(self): 
        #single night passed
        if self.round_time == 0:
            self.start_new_round()


    def check_game_over(self):
        #losing the game
        if self.player.health <= 0:
            pygame.mixer.music.stop()
            display_score = self.highscore( self.score)
            self.pause_game("Game Over! Final Score: " + str(self.score) , "Press Enter - start new apocalypse.." , "High score: " + str(display_score))
            self.reset_game()


    def start_new_round(self):
        
        self.round_number += 1

        #Decrease zombie creation time...more zombies
        if self.round_number < self.STARTING_ZOMBIE_CREATION_TIME:
            self.zombie_creation_time -= 1

        
        self.round_time = self.STARTING_ROUND_TIME

        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()

        self.player.reset()

        self.pause_game("You survived the apocalypse!", "Press 'Enter' to keep on the killing...")


    def pause_game(self, main_text, sub_text , high_score_text):
        
        global running

        pygame.mixer.music.pause()

        CARNATION = (241, 87, 87)
        BLACK = (0, 0, 0)
        MONZA = (208, 12, 17)

        main_text = self.title_font.render(main_text, True, MONZA)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

        sub_text = self.title_font.render(sub_text, True, CARNATION)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 90)

        high_score_text = self.title_font.render(high_score_text , True , MONZA)
        high_score_rect = high_score_text.get_rect()
        high_score_rect.center = (WINDOW_WIDTH//2 , WINDOW_HEIGHT//2 + 190)

        #pause text
        display_surface.fill(BLACK)
        display_surface.blit(main_text, main_rect)
        display_surface.blit(sub_text, sub_rect)
        display_surface.blit(high_score_text , high_score_rect)
        pygame.display.update()

        #Game paused until user wishes to proceed
        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    #continue
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                        pygame.mixer.music.unpause()
                #quit
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False
                    pygame.mixer.music.stop()


    def reset_game(self):
        """Resetting the game"""

        self.score = 0
        self.round_number = 1
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME

        
        self.player.health = self.player.STARTING_HEALTH
        self.player.reset()

        
        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()

        pygame.mixer.music.play(-1, 0.0)

    def highscore(self , score): # final edit function
        file = open("score.csv" , 'a+' , newline='')

        write = writer(file)
        list =[[score]]
        write.writerows(list)

        file.seek(0)

        read_file= reader(file)

        score_list = []

        for lines in read_file:
            data = int(lines[0])
            score_list.append(data)
    
        return max(score_list)

class Tile(pygame.sprite.Sprite):
    '''tile mapping'''

    def __init__(self, x, y, image_int, main_group, sub_group=""):
        
        super().__init__()
        
        #Dirt tiles
        if image_int == 1:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (1).png"), (32,32))
        #Platform tiles
        elif image_int == 2:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (2).png"), (32,32))
            sub_group.add(self)
        elif image_int == 3:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (3).png"), (32,32))
            sub_group.add(self)
        elif image_int == 4:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (4).png"), (32,32))
            sub_group.add(self)
        elif image_int == 5:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/Tile (5).png"), (32,32))
            sub_group.add(self)

        #Adding every tile to the main group
        main_group.add(self)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        #masking
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    """A class the user can control"""

    def __init__(self, x, y, platform_group, portal_group, bullet_group):

        super().__init__() 

        #horizontal kinematics
        self.HORIZONTAL_ACCELERATION = 2
        self.HORIZONTAL_FRICTION = 0.2
        self.VERTICAL_ACCELERATION = 0.8 #Gravity
        self.VERTICAL_JUMP_SPEED = 18 #Determines how high the player can jump
        self.STARTING_HEALTH = 100 #maxcap

        #Animation frames
        self.move_right_sprites = []
        self.move_left_sprites = []
        self.idle_right_sprites = []
        self.idle_left_sprites = []
        self.jump_right_sprites = []
        self.jump_left_sprites = []
        self.attack_right_sprites = []
        self.attack_left_sprites = []

        #Moving
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (1).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (2).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (3).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (4).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (5).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (6).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (7).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (8).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (9).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/Run (10).png"), (64,64)))
        for sprite in self.move_right_sprites:
            self.move_left_sprites.append(pygame.transform.flip(sprite, True, False))

        #Idling
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (1).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (2).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (3).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (4).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (5).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (6).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (7).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (8).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (9).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/idle/Idle (10).png"), (64,64)))
        for sprite in self.idle_right_sprites:
            self.idle_left_sprites.append(pygame.transform.flip(sprite, True, False))

        #Jumping
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (1).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (2).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (3).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (4).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (5).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (6).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (7).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (8).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (9).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/jump/Jump (10).png"), (64,64)))
        for sprite in self.jump_right_sprites:
            self.jump_left_sprites.append(pygame.transform.flip(sprite, True, False))

        #Attacking
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (1).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (2).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (3).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (4).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (5).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (6).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (7).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (8).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (9).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/attack/Attack (10).png"), (64,64)))
        for sprite in self.attack_right_sprites:
            self.attack_left_sprites.append(pygame.transform.flip(sprite, True, False))

        self.current_sprite = 0
        self.image = self.idle_right_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        #spritegroups
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group

        #Animation booleans
        self.animate_jump = False
        self.animate_fire = False

        #Load sounds
        self.jump_sound = pygame.mixer.Sound("sounds/jump_sound.wav")
        self.slash_sound = pygame.mixer.Sound("sounds/slash_sound.wav")
        self.portal_sound = pygame.mixer.Sound("sounds/portal_sound.wav")
        self.hit_sound = pygame.mixer.Sound("sounds/player_hit.wav")

        #Kinematics vectors
        self.position = vector(x, y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        #Set intial player values
        self.health = self.STARTING_HEALTH
        self.starting_x = x
        self.starting_y = y

# upkar please check player updations once
    def update(self):
        '''player updation'''
        self.move()
        self.check_collisions()
        self.check_animations()

        #Update the player's mask
        self.mask = pygame.mask.from_surface(self.image)


    def move(self):
        """Moving the warrior"""
        
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        #If any key pressed horizontal acceleration non zero
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acceleration.x = -1*self.HORIZONTAL_ACCELERATION
            self.animate(self.move_left_sprites, .5)
        elif keys[pygame.K_RIGHT]:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION
            self.animate(self.move_right_sprites, .5)
        else:
            if self.velocity.x > 0:
                self.animate(self.idle_right_sprites, .5)
            else:
                self.animate(self.idle_left_sprites, .5)

        #Calculating new kinematics values
        self.acceleration.x -= self.velocity.x*self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5*self.acceleration

        #Updating rect based on above calculations and adding wrap around movement
        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x > WINDOW_WIDTH:
            self.position.x = 0
        
        self.rect.bottomleft = self.position


    def check_collisions(self):
        """Collision with platform and portal"""
        #Collision checking between player and platforms when falling
        if self.velocity.y > 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False, pygame.sprite.collide_mask)
            if collided_platforms:
                self.position.y = collided_platforms[0].rect.top + 5
                self.velocity.y = 0

        #Collision check between player and platform if jumping up
        if self.velocity.y < 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False, pygame.sprite.collide_mask)
            if collided_platforms:
                self.velocity.y = 0
                while pygame.sprite.spritecollide(self, self.platform_group, False):
                    self.position.y += 1
                    self.rect.bottomleft = self.position

        #Collision check for portals
        #teleportation
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            #Determining which portal player is moving to
            #Left and right
            if self.position.x > WINDOW_WIDTH//2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            #Top and bottom
            if self.position.y > WINDOW_HEIGHT//2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.position


    def check_animations(self):
        
        #Animation of the player jump
        if self.animate_jump:
            if self.velocity.x > 0:
                self.animate(self.jump_right_sprites, .1)
            else:
                self.animate(self.jump_left_sprites, .1)

        #Animation of the player attack
        if self.animate_fire:
            if self.velocity.x > 0:
                self.animate(self.attack_right_sprites, .25)
            else:
                self.animate(self.attack_left_sprites, .25)


    def jump(self):
        """ Jump upwards if on a platform """
        #Only jump if collision with platform
        if pygame.sprite.spritecollide(self, self.platform_group, False):
            self.jump_sound.play()
            self.velocity.y = -1*self.VERTICAL_JUMP_SPEED
            self.animate_jump = True


    def fire(self):
        self.slash_sound.play()
        Bullet(self.rect.centerx, self.rect.centery, self.bullet_group, self)
        self.animate_fire = True


    def reset(self):
        self.velocity = vector(0,0)
        self.position = vector(self.starting_x, self.starting_y)
        self.rect.bottomleft = self.position


    def animate(self, sprite_list, speed):
        if self.current_sprite < len(sprite_list) -1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            #Ending of the jump animation
            if self.animate_jump:
                self.animate_jump = False
            #Ending of the attack animation
            if self.animate_fire:
                self.animate_fire = False

        self.image = sprite_list[int(self.current_sprite)]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_group, player):
        
        super().__init__()

        self.VELOCITY = 20
        self.RANGE = 350

        if player.velocity.x > 0:
            self.image = pygame.transform.scale(pygame.image.load("images/player/slash.png"), (32,32))
        else:
            self.image = pygame.transform.scale(pygame.transform.flip(pygame.image.load("images/player/slash.png"), True, False), (32,32))
            self.VELOCITY = -1*self.VELOCITY
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.starting_x = x

        bullet_group.add(self)

    
    def update(self):
        """Bullet updation"""
        self.rect.x += self.VELOCITY

        #bullet disappears after 350
        if abs(self.rect.x - self.starting_x) > self.RANGE:
            self.kill()

#ananya add kar dena for left also- done
class Zombie(pygame.sprite.Sprite):

    def __init__(self, platform_group, portal_group, min_speed, max_speed):
        
        super().__init__()

        
        self.VERTICAL_ACCELERATION = 3 #Gravity
        self.RISE_TIME = 2

        #Animation frames
        self.walk_right_sprites = []
        self.walk_left_sprites = []
        self.die_right_sprites = []
        self.die_left_sprites = []
        self.rise_right_sprites = []
        self.rise_left_sprites = []

        gender = random.randint(0,1)
        if gender == 0:
            #Boy zombie Walking
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (1).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (2).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (3).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (4).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (5).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (6).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (7).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (8).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (9).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk (10).png"), (64,64)))
            for sprite in self.walk_right_sprites:
                self.walk_left_sprites.append(pygame.transform.flip(sprite, True, False))

            #Boy Zombie Dying
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (1).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (2).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (3).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (4).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (5).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (6).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (7).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (8).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (9).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (10).png"), (64,64)))
            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite, True, False))

            #Boy zombie rising after dying
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (10).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (9).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (8).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (7).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (6).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (5).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (4).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (3).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (2).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Dead (1).png"), (64,64)))
            for sprite in self.rise_right_sprites:
                self.rise_left_sprites.append(pygame.transform.flip(sprite, True, False))
        else:
            #Girl zombie walking
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (1).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (2).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (3).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (4).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (5).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (6).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (7).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (8).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (9).png"), (64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/walk/Walk (10).png"), (64,64)))
            for sprite in self.walk_right_sprites:
                self.walk_left_sprites.append(pygame.transform.flip(sprite, True, False))

            #Girl zombie dying
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (1).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (2).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (3).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (4).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (5).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (6).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (7).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (8).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (9).png"), (64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (10).png"), (64,64)))
            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite, True, False))

            #Girl zombie rising after dying
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (10).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (9).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (8).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (7).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (6).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (5).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (4).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (3).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (2).png"), (64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("images/zombie/girl/dead/Dead (1).png"), (64,64)))
            for sprite in self.rise_right_sprites:
                self.rise_left_sprites.append(pygame.transform.flip(sprite, True, False))

        #Loading an image and getting it's rect
        self.direction = random.choice([-1, 1])

        self.current_sprite = 0
        if self.direction == -1:
            self.image = self.walk_left_sprites[self.current_sprite]
        else:
            self.image = self.walk_right_sprites[self.current_sprite]
        
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (random.randint(100, WINDOW_WIDTH - 100), -100)

        #adding platform to spritegroup
        self.platform_group = platform_group
        self.portal_group = portal_group

        #animations

        self.animate_death = False
        self.animate_rise = False

        #Load sounds
        self.hit_sound = pygame.mixer.Sound("sounds/zombie_hit.wav")
        self.kick_sound = pygame.mixer.Sound("sounds/zombie_kick.wav")
        self.portal_sound = pygame.mixer.Sound("sounds/portal_sound.wav")

        self.position = vector(self.rect.x, self.rect.y)
        self.velocity = vector(self.direction*random.randint(min_speed, max_speed), 0)
        #speed for individual zombie
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        #Intial zombie values
        self.is_dead = False
        self.round_time = 0
        self.frame_count = 0


    def update(self):
        '''Zombie updates'''
        self.move()
        self.check_collisions()
        self.check_animations()

        #how long to get up after being dead - time change? no
        if self.is_dead:
            self.frame_count += 1
            if self.frame_count % ping == 0:
                self.round_time += 1
                if self.round_time == self.RISE_TIME:
                    self.animate_rise = True
                    #how?
                    #When the zombie died, we kept the image as the last image
                    #When it rose, we started at index 0 of our rise_sprite lists
                    self.current_sprite = 0


    def move(self):
        """Move the zombie"""\
        #velocity does not change horizontally
        if not self.is_dead:
            if self.direction == -1:
                self.animate(self.walk_left_sprites, .5)
            else:
                self.animate(self.walk_right_sprites, .5)


            self.velocity += self.acceleration
            self.position += self.velocity + 0.5*self.acceleration

            #updation of rect and warping
            if self.position.x < 0:
                self.position.x = WINDOW_WIDTH
            elif self.position.x > WINDOW_WIDTH:
                self.position.x = 0
            
            self.rect.bottomleft = self.position


    def check_collisions(self):
        """Check for collisions with platforms and portals"""
        #Collision checking between zombie and platforms when falling
        #upkar this i think is not working properly
        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0

        #Collision check for portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            #Determine which portal you are moving to
            #Left+right
            if self.position.x > WINDOW_WIDTH//2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            #Top+bottom
            if self.position.y > WINDOW_HEIGHT//2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.position


    def check_animations(self):
        """Check to see if death/rise animations should run"""
        #Animating zombie death
        if self.animate_death:
            if self.direction == 1:
                self.animate(self.die_right_sprites, .095)
            else:
                self.animate(self.die_left_sprites, .095)

        #Animating zombie rise
        if self.animate_rise:
            if self.direction == 1:
                self.animate(self.rise_right_sprites, .095)
            else:
                self.animate(self.rise_left_sprites, .095)


    def animate(self, sprite_list, speed):
        """Animating zombie's functioning"""
        if self.current_sprite < len(sprite_list) -1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            #End the death animation
            if self.animate_death:
                self.current_sprite = len(sprite_list) - 1
                self.animate_death = False
            #End the rise animation
            if self.animate_rise:
                self.animate_rise = False
                self.is_dead = False
                self.frame_count = 0
                self.round_time = 0

        self.image = sprite_list[int(self.current_sprite)]


class RubyMaker(pygame.sprite.Sprite):
    """ A ruby will be generated once zombie is killed"""

    def __init__(self, x, y, main_group):
        super().__init__()

        #Animation frames
        self.ruby_sprites = []

        #Rotating
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile000.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile001.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile002.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile003.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile004.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile005.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile006.png"), (64,64)))

        
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        #Adding to the main group for drawing
        main_group.add(self)


    def update(self):
        
        self.animate(self.ruby_sprites, .25)


    def animate(self, sprite_list, speed):
    
        if self.current_sprite < len(sprite_list) -1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]


class Ruby(pygame.sprite.Sprite):
    '''Ruby perks- both for zombie and player'''

    def __init__(self, platform_group, portal_group):
        
        super().__init__()

        self.VERTICAL_ACCELERATION = 3 #Gravity
        self.HORIZONTAL_VELOCITY = 5

        self.ruby_sprites = []

        #Rotating the ruby
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile000.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile001.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile002.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile003.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile004.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile005.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile006.png"), (64,64)))

        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WINDOW_WIDTH//2, 100)

        self.platform_group = platform_group
        self.portal_group = portal_group

        self.portal_sound = pygame.mixer.Sound("sounds/portal_sound.wav")

        #vectors
        self.position = vector(self.rect.x, self.rect.y)
        self.velocity = vector(random.choice([-1*self.HORIZONTAL_VELOCITY, self.HORIZONTAL_VELOCITY]), 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)


    def update(self):
        """Updation of ruby"""
        self.animate(self.ruby_sprites, .25)
        self.move()
        self.check_collisions()


    def move(self):
        """Move the ruby"""
        #acceleration is 0

        self.velocity += self.acceleration
        self.position += self.velocity + 0.5*self.acceleration

        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x > WINDOW_WIDTH:
            self.position.x = 0
        
        self.rect.bottomleft = self.position


    def check_collisions(self):

        #Collision checking between ruby and platforms when falling
        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0

        #Collision checking portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            #Determines which portal we are moving to
            #Left+right
            if self.position.x > WINDOW_WIDTH//2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            #Top+bottom
            if self.position.y > WINDOW_HEIGHT//2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.position


    def animate(self, sprite_list, speed):
        #ruby animation
        if self.current_sprite < len(sprite_list) -1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]


class Portal(pygame.sprite.Sprite):
    """if collision --> teleport """

    def __init__(self, x, y, color, portal_group):
        
        super().__init__()

        #Animation frames
        self.portal_sprites = []

        #Portal animation
        if color == "green":
            #colour == green
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile000.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile001.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile002.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile003.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile004.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile005.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile006.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile007.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile008.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile009.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile010.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile011.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile012.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile013.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile014.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile015.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile016.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile017.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile018.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile019.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile020.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/green/tile021.png"), (72,72)))
        else:
            #colour == purple
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile000.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile001.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile002.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile003.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile004.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile005.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile006.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile007.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile008.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile009.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile010.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile011.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile012.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile013.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile014.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile015.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile016.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile017.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile018.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile019.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile020.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("images/portals/purple/tile021.png"), (72,72)))

        self.current_sprite = random.randint(0, len(self.portal_sprites)-1)
        self.image = self.portal_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        #Adding to the portal group
        portal_group.add(self)


    def update(self):
        """Updating the portal"""
        self.animate(self.portal_sprites, .2)


    def animate(self, sprite_list, speed):
        """Animating the portal"""
        if self.current_sprite < len(sprite_list) -1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]


#Creating sprite groups
my_main_tile_group = pygame.sprite.Group()
my_platform_group = pygame.sprite.Group()

my_player_group = pygame.sprite.Group()
my_bullet_group = pygame.sprite.Group()

my_zombie_group = pygame.sprite.Group()

my_portal_group = pygame.sprite.Group()
my_ruby_group = pygame.sprite.Group()

#tile map
#0 -> no tile, 1 -> dirt, 2-5 -> platforms, 6 -> ruby maker, 7-8 -> portals, 9 -> player
#23 rows and 40 columns
tile_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

#Tile objects from the tile map
#Loop through the 23 rows in the tile map i - down
for i in range(len(tile_map)): #j-across
    for j in range(len(tile_map[i])):
        #Dirt tiles
        if tile_map[i][j] == 1:
            Tile(j*32, i*32, 1, my_main_tile_group)
        #Platform tiles
        elif tile_map[i][j] == 2:
            Tile(j*32, i*32, 2, my_main_tile_group, my_platform_group)
        elif tile_map[i][j] == 3:
            Tile(j*32, i*32, 3, my_main_tile_group, my_platform_group)
        elif tile_map[i][j] == 4:
            Tile(j*32, i*32, 4, my_main_tile_group, my_platform_group)
        elif tile_map[i][j] == 5:
            Tile(j*32, i*32, 5, my_main_tile_group, my_platform_group)
        #Ruby Maker
        elif tile_map[i][j] == 6:
            RubyMaker(j*32, i*32, my_main_tile_group)
        #Portals
        elif tile_map[i][j] == 7:
            Portal(j*32, i*32, "green", my_portal_group)
        elif tile_map[i][j] == 8:
            Portal(j*32, i*32, "purple", my_portal_group)
        #Player
        elif tile_map[i][j] == 9:
            my_player = Player(j*32 - 32, i*32 , my_platform_group, my_portal_group, my_bullet_group)
            my_player_group.add(my_player)


background_image = pygame.transform.scale(pygame.image.load("finalBackground.jpg"), (1280, 736))
background_rect = background_image.get_rect()
background_rect.topleft = (0, 0)

#Game intialised
my_game = Game(my_player, my_zombie_group, my_platform_group, my_portal_group, my_bullet_group, my_ruby_group)
my_game.pause_game("Knightfall: Undead Uprising", "Press 'Enter' to Begin" ,"")
pygame.mixer.music.play(-1, 0.0)

#game loop
running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            #Player wants to jump
            if event.key == pygame.K_SPACE:
                my_player.jump()
            #Player wants to fire
            if event.key == pygame.K_UP:
                my_player.fire()
           
    display_surface.blit(background_image, background_rect)

    #Drawing tiles and updating ruby maker
    my_main_tile_group.update()
    my_main_tile_group.draw(display_surface)

    #Update and draw sprite groups
    my_portal_group.update()
    my_portal_group.draw(display_surface)

    my_player_group.update()
    my_player_group.draw(display_surface)

    my_bullet_group.update()
    my_bullet_group.draw(display_surface)

    my_zombie_group.update()
    my_zombie_group.draw(display_surface)

    my_ruby_group.update()
    my_ruby_group.draw(display_surface)

    #Update and draw the game
    my_game.update()
    my_game.draw()

    #Update the display and tick the clock
    pygame.display.update()
    clock.tick(ping)

pygame.quit()