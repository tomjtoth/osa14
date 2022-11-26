import pygame, math
from random import randint, randrange

pygame.init()
naytto = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("Obviously Superb Application 14 (osa14)")
pygame.mouse.set_visible(False)
kello = pygame.time.Clock()
font_hud = pygame.font.SysFont("Arial", 24)
font_pop_up = pygame.font.SysFont("Arial", 34)

yells = [
    pygame.transform.rotate(font_pop_up.render(x, True, (255, 255, 255)), randint(-15,15)) \
    for x in "PEW!,PSSHT!,BZZZZ!,ZAP!,KSSSH!,KFFF!,AAAARGH!!!!".split(",")
]

crossh = (0,0)


def main_menu():
    naytto.fill((0,0,0))
    y = 10
    for s in """
    Keyboard shortcuts:

    W,A,S,D - up,down,left,right
    LSHIFT - run
    LMB,RMB - charge and fire left,right eyes
    R - restart/reset

    ESC - exit
    ENTER - new game""".split("\n"):
        naytto.blit(font_hud.render(s,True, (255, 255, 255)), (10, y))
        y += 24

    pygame.display.flip()
    
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT \
            or ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                exit()
                

        kello.tick(60)


def new_game():
    
    global player, ev_list, crossh, persistents

    persistents = []

    player = Player()

    # spawn collectibles
    collectibles = [Collectible() for _ in range(randint(10,20))]
    enemies = [Enemy() for _ in range(randint(10,20))]

    Enemy.timeout = Enemy.original_timeout

    while True:
        
        # caching all the events
        ev_list = pygame.event.get()
        for ev in ev_list:
            if ev.type == pygame.QUIT:
                exit()

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                # back to main menu
                return False

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                
                return True

            elif ev.type == pygame.MOUSEMOTION:
                crossh = ev.pos

        naytto.fill((40, 40, 40))
        
        for collectible in collectibles:
            collectible.update()

        if Enemy.timeout > 0:
            Enemy.timeout -= 1

        for enemy in enemies:
            enemy.update()

        player.update()

        naytto.blit(font_hud.render(
            f"INTEGRITY: {player._health:.0f}, ENERGY: {player._energy:.0f}, POINTS: {player._score:.0f}", 
            True, (255, 255, 255)), (10, Player.sy + Player.height-20))


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

class Collectible:
    spr = pygame.image.load("kolikko.png")
    width = spr.get_width()
    height = spr.get_height()

    sx = naytto.get_width() - width
    sy = naytto.get_height() - height

    def __init__(self):
        global sx, sy
        self._value = 1
        self._pos = (randint(0, Collectible.sx-1), randint(0, Collectible.sy-1))
        self._collected = False

    def update(self):
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
        

    def _translate(self):
        sx = Player.sx if self is Player else Enemy.sx
        sy = Player.sy if self is Player else Enemy.sy

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

    global naytto

    original_timeout = timeout = 120

    # standing still
    sprite = pygame.image.load("hirvio.png")
    
    width = sprite.get_width()
    height = sprite.get_height()
    sx = naytto.get_width() - width 
    sy = naytto.get_height() - height 

    def __init__(self):
        super().__init__()
        self._pos = [randint(0, Enemy.sx), randint(0, Enemy.sy)]

    def update(self):
        global naytto

        self.__seek()
        naytto.blit(Enemy.sprite, self._pos)
    
    def __attack(interval: int):
        player._health -= 1

    def __seek(self):
        
        # Pythagoraan lause
        distance = math.sqrt(
            math.pow(self._pos[0] - player._pos[0], 2) # x^2
            + 
            math.pow(self._pos[1] - player._pos[1], 2) # y^2
        )
        
        if distance > 200:
            self.__idle()
        elif distance > 15:
            if Enemy.timeout == 0:
                self.__close_in(self._speeds[0 if distance > 100 else 1])
        else:
            self.__attack()

    def __idle(self):
        dx = randint(-self._speeds[0], self._speeds[0])
        dy = randint(-self._speeds[0], self._speeds[0])

        if self._pos[0] + dx in range(0, Enemy.sx):
            self._pos[0] += dx

        if self._pos[1] + dy in range(0, Enemy.sy):
            self._pos[1] += dy

    def __close_in(self, v: int):
                
        # direction x
        if player._pos[0] > self._pos[0]:
            self._pos[0] += v
        else:
            self._pos[0] -= v

        # direction y
        if player._pos[1] > self._pos[1]:
            self._pos[1] += v
        else:
            self._pos[1] -= v

class Player(Character):

    # standing still
    spr_mov = [pygame.image.load("robo.png")]
    # walking
    spr_mov.append([pygame.transform.rotate(spr_mov[0],-5), pygame.transform.rotate(spr_mov[0],5)])
    # running
    spr_mov.append([pygame.transform.rotate(spr_mov[0],-10), pygame.transform.rotate(spr_mov[0],10)])

    width = spr_mov[0].get_width()
    height = spr_mov[0].get_height()

    sx = naytto.get_width() - width
    sy = naytto.get_height() - height


    def __init__(self):
        super().__init__()
        self._eyes = [Eye(0), Eye(1)]
        self._energy_regen = 1
        self._score = 0
        self._pos = [randint(0, Player.sx), randint(0, Player.sy)]

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

    def update(self):
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
        global crossh, naytto, yells, persistents
        
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
            yells[randint(0, len(yells)-1)], 
            
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


while True:
    main_menu()

while new_game():
    pass
