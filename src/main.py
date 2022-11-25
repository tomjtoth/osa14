# TODO:
# make use of the rest of the sprites
# haamut
# kolikot
# door
# 
# BONUS:
# powerups to increase energy, increase/restore integrity
# animate ghosts' movement
# 

# TEE PELI TÄHÄN
import pygame
from random import randint, randrange



class Collectible:
    spr = pygame.image.load("kolikko.png")
    width = spr.get_width()
    height = spr.get_height()

    def __init__(self):
        global sx, sy
        self._value = 1
        self._pos = (randint(0,sx-1), randint(0,sy-1))
        self._collected = False

    def redraw(self):
        #global naytto

        naytto.blit(Collectible.spr, self._pos)

class PowerUp(Collectible):
    types = ['max_energy', 'max_integrity', 'energy', 'integrity']

    def __init__(self):
        self._value = 10
        self._type = PowerUp.types[randint(0,len(PowerUp.types)-1)]

class Weapon:
    def __init__(self, chargeable = False):
        self.level = 0
        self.charging = False
        self._chargeable = chargeable

class Eye(Weapon):

    cost = 30

    left = (
        # standing still
        (17, 14),
        
        # tilted 5 deg
        (
            (20,14), (15, 15)
        ),


        # tilted 10 deg
        (
            (22,14), (13, 16)
        )
    )

    right = (
        # standing still
        (32, 14),
        
        # tilted 5 deg
        (
            (34,16), (29, 14)
        ),


        # tilted 10 deg
        (
            (36,16), (27, 14)
        )
    )

    def __init__(self, side: int):
        super().__init__()
        self.pos = Eye.left if side == 0 else Eye.right

class Character:
    
    def __init__(self):
        global sx, sy

        self._energy = \
        self._max_energy = \
        self._health = \
        self._max_health = 1000
        
        self._up = False
        self._down = False
        self._left = False
        self._right = False
        self._running = False
        #self._dashing = False

        self._speeds = [
            2,   # walking
            3    # running
        ]
        self._mov_anim_tick = 0
        self._pos = [randint(0, sx), randint(0, sy)]

    def _translate(self):
        global sx, sy

        px = self._pos[0]
        py = self._pos[1]
        v = self._speeds[1 if self._running else 0]

        state = 0

        if self._up:
            if self._pos[1] - v >= 0:
                self._pos[1] -= v
            else:
                self._up = False

        if self._down:
            if self._pos[1] + v <= sy:
                self._pos[1] += v
            else:
                self._down = False

        if self._left:
            if self._pos[0] - v >=0:
                self._pos[0] -= v
            else:
                self._left = False

        if self._right:
            if self._pos[0] + v <= sx:
                self._pos[0] += v
            else:
                self._right = False
        
        if self._left or self._right or self._up or self._down:
            self._mov_anim_tick += 1
            state += 1

            if self._running:
                state += 1
        
        else:
            self._mov_anim_tick = 0
        
        return state
  
class Enemy(Character):

    # standing still
    spr_mov = [[pygame.image.load("hirvio.png")]]
    spr_mov[0].append(pygame.transform.flip(spr_mov[0][0], True, False))
    # walking
    spr_mov.append([pygame.transform.rotate(spr_mov[0][0],-5), pygame.transform.rotate(spr_mov[0][0],5)])
    spr_mov.append([pygame.transform.rotate(spr_mov[0][1],-5), pygame.transform.rotate(spr_mov[0][1],5)])
    # running
    spr_mov.append([pygame.transform.rotate(spr_mov[0][0],-10), pygame.transform.rotate(spr_mov[0][0],10)])
    spr_mov.append([pygame.transform.rotate(spr_mov[0][1],-10), pygame.transform.rotate(spr_mov[0][1],10)])

    def handle_events(self):
        global naytto

        naytto.blit(Enemy.spr_mov[0][0], self._pos)

class Player(Character):

    # standing still
    spr_mov = [pygame.image.load("robo.png")]
    # walking
    spr_mov.append([pygame.transform.rotate(spr_mov[0],-5), pygame.transform.rotate(spr_mov[0],5)])
    # running
    spr_mov.append([pygame.transform.rotate(spr_mov[0],-10), pygame.transform.rotate(spr_mov[0],10)])

    width = spr_mov[0].get_width()
    height = spr_mov[0].get_height()

    def __init__(self):
        super().__init__()
        self._eyes = [Eye(0), Eye(1)]
        self._energy_regen = 1

    def __translate(self):
        global naytto
        
        state = super()._translate()
        
        # standing still
        if state == 0:
            spr = Player.spr_mov[0]
        
        # walking
        elif state == 1:
            spr = Player.spr_mov[1][self._mov_anim_tick//5 % 2]
        
        # running
        elif state == 2:
            spr = Player.spr_mov[2][self._mov_anim_tick//5 % 2]

        # draw the character
        naytto.blit(spr, (self._pos[0], self._pos[1]))

    def handle_events(self):
        global ev_list

        for ev in ev_list:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w:
                    self._up = True
                if ev.key == pygame.K_s:
                    self._down = True
                if ev.key == pygame.K_a:
                    self._left = True
                if ev.key == pygame.K_d:
                    self._right = True
                if ev.key == pygame.K_LSHIFT:
                    self._running = True
                if ev.key == pygame.K_SPACE:
                    self._dashing = True
                
            if ev.type == pygame.KEYUP:
                if ev.key == pygame.K_w:
                    self._up = False
                if ev.key == pygame.K_s:
                    self._down = False
                if ev.key == pygame.K_a:
                    self._left = False
                if ev.key == pygame.K_d:
                    self._right = False
                if ev.key == pygame.K_LSHIFT:
                    self._running = False

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == pygame.BUTTON_LEFT:
                    self._eyes[0].charging = True

                if ev.button == pygame.BUTTON_RIGHT:
                    self._eyes[1].charging = True

            if ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == pygame.BUTTON_LEFT:
                    self._eyes[0].charging = False
                    
                if ev.button == pygame.BUTTON_RIGHT:
                    self._eyes[1].charging = False
        
        
        self.__translate()
        self.__manage_energy()
    
    def __shoot(self, eye: Eye):
        global crossh, naytto, float_txt, persistents
        
        if self._running:
            pos = eye.pos[2][self._mov_anim_tick//5 % 2]
        elif self._up or self._down or self._left or self._right:
            pos = eye.pos[1][self._mov_anim_tick//5 % 2]
        else:
            pos = eye.pos[0]


        # draw line from the eye to the mouse cursor
        pygame.draw.line(naytto, (255, 0, 0)
            , (self._pos[0]+pos[0], self._pos[1]+pos[1])
            , crossh
            , 10)

        # firing sound made visible
        persistents.append([
            
            # the pre-rendered text itself
            float_txt[randint(0, len(float_txt)-1)], 
            
            # n frames to show the text near the robot
            15

        ])
        
    def __manage_energy(self):
        
        moving = self._up or self._down or self._left or self._right
        
        # regenerating energy while standing still
        if self._energy < self._max_energy and not moving:
            self._energy += self._energy_regen

        if self._running and moving:
            if self._energy > 0:
                self._energy -= self._energy_regen * 2
            else:
                self._running = False

        for eye in self._eyes:
            if eye.charging:
                if self._energy > 0:
                    self._energy -= 1
                    eye.level += 1
                else:
                    eye.charging = False
                    
                if eye.level == Eye.cost:
                    self.__shoot(eye)
                    eye.level = 0
                    eye.charging = False
            else:
                if eye.level -1 >= 0:
                    eye.level -= 1



pygame.init()
naytto = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("unambitious osa14 yritys")
pygame.mouse.set_visible(False)
kello = pygame.time.Clock()
font_hud = pygame.font.SysFont("Arial", 24)
font_pop_up = pygame.font.SysFont("Arial", 34)

# näitä vilautetaan kun ammutaan
float_txt = [
    pygame.transform.rotate(font_pop_up.render(x, True, (255, 255, 255)), randint(-15,15)) \
    for x in "PEW!,PSSHT!,BZZZZ!,ZAP!,KSSSH!,KFFF!,AAAARGH!!!!".split(",")
]
persistents = []
crossh = (0,0)

sx = naytto.get_width() - Player.width
sy = naytto.get_height() - Player.height

player = Player()

# spawn collectibles
collectibles = [Collectible() for _ in range(randint(10,20))]
enemies = [Enemy() for _ in range(randint(10,20))]

while True:
    
    # caching all the events
    ev_list = pygame.event.get()
    for ev in ev_list:
        if ev.type == pygame.QUIT \
        or ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                exit()

        elif ev.type == pygame.MOUSEMOTION:
            crossh = ev.pos


    naytto.fill((40, 40, 40))
    
    
    for collectible in collectibles:
        collectible.redraw()

    for enemy in enemies:
        enemy.handle_events()
    
    player.handle_events()
    

    naytto.blit(font_hud.render(
        f"INTEGRITY: {player._health:.0f}, ENERGY: {player._energy:.0f}, POINTS: x", 
        True, (255, 255, 255)), (10, sy+Player.height-20))


    # draw crosshair
    pygame.draw.line(naytto, (255 - player._eyes[0].level, 255, 255)
        , (crossh[0]-20, crossh[1])
        , (crossh[0]+20, crossh[1])
        , 2)
    
    pygame.draw.line(naytto, (255 - player._eyes[1].level, 255, 255)
        , (crossh[0], crossh[1]-20)
        , (crossh[0], crossh[1]+20)
        , 2)

    cleanup_persistents = []

    # show floating text messages for a certain amount of frames
    for obj in persistents:
        if obj[1] > 0:
            naytto.blit(obj[0], (player._pos[0] + Player.width, player._pos[1] - 20)) 
            obj[1] -= 1
        else:
            cleanup_persistents.append(obj)
    
    # remove above texts
    for obj in cleanup_persistents:
        persistents.remove(obj)

    
    pygame.display.flip()

    kello.tick(60)