import time, random, sys, os, pygame

pygame.init()

screen_width, screen_height = 800, 800
clock = pygame.time.Clock()
display = pygame.display.set_mode((screen_width, screen_height))

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 1200
BLOCK_SIZE = 20

Platforms = pygame.sprite.Group()
People = pygame.sprite.Group()
Foods = pygame.sprite.Group()

def load_images(path_to_directory):
    images = {}
    for dirpath, dirnames, filenames in os.walk(path_to_directory):
        for name in filenames:
            if name.endswith('.png'):
                key = name[:-4]
                img = pygame.image.load(os.path.join(dirpath, name)).convert_alpha()
                images[key] = img
    return images

class Platform(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        pygame.sprite.Sprite.__init__(self, Platforms)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        self.rect.left = self.x
        self.rect.right = self.x + self.width
        self.rect.top = self.y
        self.rect.bottom = self.y + height

    def draw(self):
        rect_copy = self.rect.copy()
        rect_copy.left# -= 30
        rect_copy.right# -= 30
        pygame.draw.rect(display, (150,150,150), rect_copy, 1)

class Food(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        pygame.sprite.Sprite.__init__(self, Foods)  # Add to Foods group only
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.size = [width,height]
        self.image = pygame.Surface(self.size)
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        # Set rect position to match visual position
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, Images):
        display.blit(pygame.transform.scale(Images["apple"],(self.width,self.height)),(self.x,self.y))

class Person(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, People)
        self.hunger = 50
        self.health = 100
        self.horny = 50
        self.nn = None
        self.count = 0
        
        self.x = WINDOW_WIDTH/2
        self.y = WINDOW_HEIGHT
        self.x_change = 0
        self.gravity = 0
        self.width = 20
        self.height = 40
        self.size = [self.width, self.height]  # Match visual size
        self.image = pygame.Surface(self.size)
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.chose = True
        self.JumpAllowed = True
        self.direction = "Right"
        
    def draw(self, Images):
        if self.x_change == 0:
            if self.direction == "Right":
                display.blit(pygame.transform.scale(Images["chill"],(self.width,self.height)),(self.x,self.y+5))
            else:
                display.blit(pygame.transform.scale(Images["chill"],(self.width,self.height)),(self.x,self.y+5))
        else:
            if self.x_change > 0:
                display.blit(pygame.transform.scale(Images["right"],(self.width,self.height)),(self.x,self.y))
            else:
                display.blit(pygame.transform.scale(Images["left"],(self.width,self.height)),(self.x,self.y))
                
    def KeyPress(self):
        if self.chose == True:
            key = pygame.key.get_pressed()
            if key[ord('w')] and self.JumpAllowed == True and self.gravity >= 0:
                self.gravity = -10
                self.JumpAllowed = False
            if key[ord('d')]:
                self.x_change = 5
                self.direction = "Right"
            if key[ord('a')]:
                self.x_change = -5
                self.direction = "Left"
            if self.x_change == 5 and key[ord('d')]  == 0:
                self.x_change = 0
            if self.x_change == -5 and key[ord('a')]  == 0:
                self.x_change = 0
        if self.x_change == 5 and self.x < WINDOW_WIDTH - 75:
            self.x += self.x_change
        if self.x_change == -5 and self.x - 5 > -5:
            self.x += self.x_change
            
    def Gravity(self):
        self.y += self.gravity
        if self.gravity == 0:
            self.gravity = 1
        else:
            self.gravity += .35
            
        if self.y >= WINDOW_HEIGHT - 50:
            self.gravity = 0
            self.y = WINDOW_HEIGHT - 50
            self.JumpAllowed = True
            
    def Collision(self):
        for platform in Platforms:
            if pygame.sprite.collide_rect(self, platform):
                if self.y < platform.y and self.gravity > 0:
                    self.gravity = 0
                    self.y = platform.y - self.height
                    self.JumpAllowed = True
                if self.x_change > 0 and self.y > platform.y and self.y < platform.y + platform.height - 10:
                    self.x = platform.x - self.width
                    self.x_change = 0
                elif self.x_change < 0 and self.y > platform.y and self.y < platform.y + platform.height - 10:
                    self.x = platform.x + platform.width
                    self.x_change = 0
                if self.y > platform.y and self.gravity < 0:
                    self.gravity = 0
        
        if self.gravity != 0:
            self.JumpAllowed = False
            
        # Check for food collisions
        food_collisions = pygame.sprite.spritecollide(self, Foods, True)
        for food in food_collisions:
            self.health += 20
            print(f"Health increased to: {self.health}")
    
    def update(self, Images):
        # Update rect position BEFORE collision detection
        self.rect.x = self.x
        self.rect.y = self.y
        self.rect.width = self.width
        self.rect.height = self.height
        
        self.Collision()
        self.KeyPress()
        self.Gravity()
        self.draw(Images)

def drawGrid():
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(display, WHITE, rect, 1)

def generate_platforms():
    return [Platform(0,700,500,100),
            Platform(450,550,20,20),
            Platform(200,400,20,20),
            Platform(0,300,20,20),
            Platform(650,450,20,20),
            Platform(650,220,20,20),
            Platform(780,320,20,20),
            Platform(600,100,20,20)]

def game_loop():
    game_run = True
    Images = load_images("Images")
    PlatformList = generate_platforms()
    for platform in PlatformList:
        Platforms.add(platform)
        
    dude = Person()
    People.add(dude)
    
    # Create foods at positions that don't overlap with player start
    apple1 = Food(590, 60, 40, 50)   # Position matches platform at (600,100)
    #apple2 = Food(640, 410, 40, 50)  # Position matches platform at (650,450)
    # No need to manually add to Foods group - it's done in __init__

    while game_run == True:
        display.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        dude.update(Images)
        
        # Draw all foods
        for food in Foods:
            food.draw(Images)
            
        # Draw all platforms
        for platform in PlatformList:
            platform.draw()
        
        pygame.display.flip()
        #clock.tick(120)

game_loop()