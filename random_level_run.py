# THIS ACTUALLY JUST WORKS
# LETS GO

from random_gen_map import prep, generate_food, generate_platforms
import time, random, sys, os, pygame
import neat

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
        
    def position(self): # top, bottom, left, right
        return [self.x, self.y, self.width, self.height]

class Food(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        pygame.sprite.Sprite.__init__(self, Foods)  # Add to Foods group only
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.size = [width,height]
        self.image = pygame.Surface(self.size)
        self.rect = self.image.get_rect()
        self.rect.left = self.x
        self.rect.right = self.x + self.width
        self.rect.top = self.y
        self.rect.bottom = self.y + height
        self.image.fill((255,0,0))
        # Set rect position to match visual position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def position(self): # top, bottom, left, right
        return [self.x, self.y, self.width, self.height]

    def draw(self, Images):
        display.blit(pygame.transform.scale(Images["apple"],(self.width,self.height)),(self.x,self.y))

class Person(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, People)
        self.alive = True
        self.health = 0
        self.nn = None
        self.count = 0
        
        self.x = 20
        self.y = WINDOW_HEIGHT-300
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
                
    def KeyPress(self,left=False,right=False,up=False):
        if self.chose == True:
            key = pygame.key.get_pressed()
            if up and self.JumpAllowed == True and self.gravity >= 0:
                self.gravity = -10
                self.JumpAllowed = False
            if key[ord('d')] or right:
                self.x_change = 5
                self.direction = "Right"
            if key[ord('a')] or left:
                self.x_change = -5
                self.direction = "Left"
            if self.x_change == 5 and right == 0:
                self.x_change = 0
            if self.x_change == -5 and left == 0:
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
            self.alive = False
            #self.gravity = -50
            #self.y = WINDOW_HEIGHT - 50
            #self.JumpAllowed = True
            
    def Collision(self):
        for platform in Platforms:
            if pygame.sprite.collide_rect(self, platform):
                #print("GOOOD")
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
    
    def update(self, Images, left, right, up):
        # Update rect position BEFORE collision detection
        
        self.KeyPress(left, right, up)
        self.Gravity()
        
        self.rect.x = self.x
        self.rect.y = self.y
        self.rect.width = self.width
        self.rect.height = self.height
        
        self.Collision()
        self.draw(Images)

    def state(self): # x,y
        return [self.x, self.y, self.width, self.height, self.JumpAllowed, self.gravity, self.x_change, self.gravity, self.health]

def drawGrid():
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(display, WHITE, rect, 1)

#def generate_platforms():
#    platforms = [Platform(20,600,20,20),
#            Platform(140,600,20,20),
#            Platform(300,200,20,20),
#            Platform(450,600,20,20),
#            Platform(0,300,20,20),
#            Platform(650,450,20,20),
#            Platform(650,220,20,20),
#            Platform(780,320,20,20),
#            Platform(600,100,20,20)]
#    
#    for platform in platforms:
#        Platforms.add(platform)
#    return platforms

#def generate_food():
#    # Create foods at positions that don't overlap with player start
#    apple1 = Food(-10, 260, 40, 50)#Food(590,60,40,50)   # Position matches platform at (600,100)
#    #apple2 = Food(-10, 260, 40, 50)  # Position matches platform at (650,450)
#    foods = [apple1]
#    return foods
#    # No need to manually add to Foods group - it's done in __init__


#CALCULATE DISTANCE BETWEEN ALL THE PLATFORM AND FOOD CENTERS ONCE
#THESE WILL BE INPUTS WITHOUT CHANGE ALONG WITH ALL OF THEIR VALUES
# APART FROM FRUIT SORTA

def distance_between(x,y, x2, y2):
    return [x-x2, y-y2]

#def prep():
#    platforms = generate_platforms()
#    foods = generate_food()
#    
#    vals = []
#    
#    for platform in platforms:
#        vals.append(platform.position())
#        for food in foods:
#            vals.append(distance_between(platform.x,platform.y, food.x, food.y))
#    for i, platform in enumerate(platforms):
#        for platform2 in platforms[i:]:
#            vals.append(distance_between(platform.x,platform.y, platform2.x, platform2.y))
#    
#    for food in foods:
#        vals.append(food.position())
#    
#    return [platforms, foods, vals]
            


import neat
import pickle

# XOR test cases: input -> expected output
#xor_outputs = [(0.0,),    (1.0,),    (1.0,),    (0.0,)]


#platforms = generate_platforms()



def eval_genomes(genomes, config):
    """Fitness function: evaluates how well each genome solves XOR."""
    
    for genome_id, genome in genomes:
        # Create a neural network from this genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        # Start with perfect fitness, subtract error
        # Test on all 4 XOR cases
        
        Platforms.empty()
        People.empty()
        Foods.empty()
        
        platforms, foods, INPUTS = prep()
#print(INPUTS)
#foods = generate_food()
    
        dude = Person()
        Platforms.add(platforms)
        Foods.add(foods)
        People.add(dude)

        distances = []
        for platform in platforms:
            distances.append(distance_between(dude.x, dude.y, platform.x, platform.y))
            
        for food in foods:
            distances.append(distance_between(dude.x, dude.y, food.x, food.y))

        game_state = [item for sublist in [*INPUTS,*distances] for item in sublist]
        genome.fitness = 0
        Images = load_images("Images")
        x_diff, y_diff = distance_between(dude.x, dude.y, foods[0].x, foods[0].y)
        prev = abs(x_diff) + abs(y_diff)
        
        prev_x = dude.x
        steps_no_x_progress = 0
        highest_plat_y = dude.y
        
        for step in range(400):
            display.fill(BLACK)
            #print(game_state)
            output = net.activate(game_state)
            left, right, up = [round(i) for i in output]
            dude.update(Images, left, right, up)
            if dude.alive == False:
                genome.fitness -= .1
                break
            elif dude.health != 0:
                genome.fitness += .2
                #break
                dude.health = 0
            else:
                
                if dude.JumpAllowed and dude.y < highest_plat_y:
                    genome.fitness += (highest_plat_y - dude.y) * 0.00125 *2
                    highest_plat_y = dude.y
                
                if abs(dude.x - prev_x) < 1:
                    steps_no_x_progress += 1
                
                if steps_no_x_progress > 30:
                    #pass
                    genome.fitness -= 0.02
                prev_x = dude.x
            distances = []
            #genome.fitness += max(0, 1 - (abs(x_diff) + abs(y_diff))/200)
            #print(max(0, 1 - (abs(x_diff) + abs(y_diff))/200))
            #genome.fitness += 0.00001# survival bonus
            
            
            for platform in platforms:
                distances.append(distance_between(dude.x,dude.y, platform.x, platform.y))
            
            for food in foods:
                distances.append(distance_between(dude.x, dude.y, food.x, food.y))
            
            game_state = [item for sublist in [*INPUTS,*distances] for item in sublist]
            
            x_diff, y_diff = distance_between(dude.x, dude.y, foods[0].x, foods[0].y)
            val = abs(x_diff) + abs(y_diff)
            
            if genome_id % 1000 == 0:
            
                #display.fill(BLACK)
            
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
        
                # Draw all foods
                for food in Foods:
                    food.draw(Images)
            
                # Draw all platforms
                for platform in platforms:
                    platform.draw()
        
                pygame.display.flip()
                clock.tick(120)
        
    #platforms = generate_platforms()
        #reward = prev-val
        #print(reward * .01)
        #print(reward)
        #genome.fitness += reward * .005


# Load configuration
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-xor')

# Create population
p = neat.Population(config)
p.add_reporter(neat.StdOutReporter(True))

# Run evolution for up to 300 generations
winner = p.run(eval_genomes, 300)

#with open("/Users/frankie/Downloads/assignment_3-2 (2)/final_project/winner.pkl", "wb") as f:
#    pickle.dump(winner, f)
#    f.close()

# Test the winner
#print('\nBest genome:\n{!s}'.format(winner))


#with open("winner.pkl", "wb") as f:
#    genome = pickle.load(f)

def show_winner(genomes, config):
    """Fitness function: evaluates how well each genome solves XOR."""
    
    for genome_id, genome in genomes:
        # Create a neural network from this genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        # Start with perfect fitness, subtract error
        #genome.fitness = 4.0
        # Test on all 4 XOR cases
        
        Platforms.empty()
        People.empty()
        Foods.empty()
        
        platforms, foods, INPUTS = prep()
        
        Platforms.add(platforms)
        Foods.add(foods)
    
        dude = Person()
        dude.x = platforms[0].x
        dude.y = platforms[0].y-10
        People.add(dude)

        distances = []
        for platform in platforms:
            distances.append(distance_between(dude.x, dude.y, platform.x, platform.y))
            
        for food in foods:
            distances.append(distance_between(dude.x, dude.y, food.x, food.y))

        game_state = [item for sublist in [*INPUTS,*distances] for item in sublist]
        genome.fitness = 0
        Images = load_images("Images")
        x_diff, y_diff = distance_between(dude.x, dude.y, foods[0].x, foods[0].y)
        prev = abs(x_diff) + abs(y_diff)
        
        prev_x = dude.x
        steps_no_x_progress = 0
        highest_plat_y = dude.y
        
        for step in range(500):
            display.fill(BLACK)
            #print(game_state)
            output = net.activate(game_state)
            left, right, up = [round(i) for i in output]
            dude.update(Images, left, right, up)
            if dude.alive == False:
                break
            elif dude.health != 0:
                pass
                #genome.fitness += 100
                #break
            else:
                
                if dude.JumpAllowed and dude.y < highest_plat_y:
                    genome.fitness += (highest_plat_y - dude.y) * 0.025
                    highest_plat_y = dude.y
                
                if abs(dude.x - prev_x) < 1:
                    steps_no_x_progress += 1
                
                if steps_no_x_progress > 30:
                    genome.fitness -= 0.02
                prev_x = dude.x
            distances = []
            #genome.fitness += max(0, 1 - (abs(x_diff) + abs(y_diff))/200)
            #print(max(0, 1 - (abs(x_diff) + abs(y_diff))/200))
            #genome.fitness += 0.00001# survival bonus
            
            
            for platform in platforms:
                distances.append(distance_between(dude.x,dude.y, platform.x, platform.y))
            
            for food in foods:
                distances.append(distance_between(dude.x, dude.y, food.x, food.y))
            
            game_state = [item for sublist in [*INPUTS,*distances] for item in sublist]
            
            x_diff, y_diff = distance_between(dude.x, dude.y, foods[0].x, foods[0].y)
            val = abs(x_diff) + abs(y_diff)
            
            if True:
            
                #display.fill(BLACK)
            
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
        
                # Draw all foods
                for food in Foods:
                    food.draw(Images)
            
                # Draw all platforms
                for platform in platforms:
                    platform.draw()
        
                pygame.display.flip()
                clock.tick(120)
        
    #platforms = generate_platforms()
        reward = prev-val
        #print(reward * .01)
        #print(reward)
        #genome.fitness += reward * .01

while True:
    show_winner([(1, winner)], config)