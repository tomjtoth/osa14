#TODO:
# more levels
# remember stats
# remember score

import pygame, math
from random import randint, randrange, choice

pygame.init()
naytto = pygame.display.set_mode((1024, 768))
nw = naytto.get_width()
nh = naytto.get_height()
pygame.display.set_caption("Obviously Superb Application 14 (osa14)")
pygame.mouse.set_visible(False)
kello = pygame.time.Clock()
font_hud = pygame.font.SysFont("Arial", 24)
font_pop_up = pygame.font.SysFont("Arial", 34)
crossh = (0,0)
main_menu_text = """Keys:

W, A, S, D - up, down, left, right
H - heal
LSHIFT - run
LMB, RMB - charge (takes about 3 seconds) and fire left, right eyes

R - reset game
ESC - exit
ENTER - new game

Gameplay:

1. collect all coins
2. door appears
3. exit through the door
"""

render = lambda s: pygame.transform.rotate(font_pop_up.render(s, True, (255, 255, 255)), randint(-15,15))

def main_menu():
    def __redraw():
        naytto.fill((0,0,0))
        y = 10
        for s in main_menu_text.split("\n"):
            naytto.blit(font_pop_up.render(s,True, (255, 255, 255)), (10, y))
            y += 24

        pygame.display.flip()

    __redraw()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    exit()
                if ev.key == pygame.K_RETURN:
                    while new_game():
                        pass # needed for "reset game"
                    __redraw()
        kello.tick(60)

# TODO
def select_difficulty():
    pass

def new_game():
    
    global player, crossh, ev_list, rendered_texts, enemies, collectibles

    rendered_texts = []
    player = Player()
    door = Door()
    collectibles = [choice([
        # 5 to 10 powerups worth 10 points
        PUEnergy(), PUMEnergy(), PUHealth(), PUMHealth(),
        PUFirePower(), PUEnergyEfficiency(), PUEnergyRegen(), 
        PUHealingEfficiency(), PUHealingRate()
    ]) for _ in range(randint(5,10))] + [
        # 10 to 20 simple coins worth 1 point
        Collectible() for _ in range(randint(10,20))
    ]

    # 2:1 chance for simple Ghost
    enemies = [choice([Ghost(),Ghost(),Nightmare()]) for _ in range(randint(5,10))]
    Ghost.timeout = Ghost.original_timeout

    while True:
        # caching all the events, so that other routines can browse them
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

        # ghosts wont attack in the beginning...
        if Ghost.timeout > 0:
            Ghost.timeout -= 1

        for enemy in enemies:
            enemy.update()

        player.update()

        if door.update():
            congrats()
            return False

        # draw HUD
        naytto.blit(font_hud.render(
            f"INTEGRITY: {player.health:4.0f}, ENERGY: {player.energy:4.0f}, SCORE: {player.score:.0f}", 
            True, (255, 255, 255)), (10, Player.sy + Player.height-20))

        # draw crosshair
        pygame.draw.line(naytto, (255 - player.eyes[0].level, 255, 255)
            , (crossh[0]-20, crossh[1])
            , (crossh[0]+20, crossh[1])
            , 2)
        
        pygame.draw.line(naytto, (255 - player.eyes[1].level, 255, 255)
            , (crossh[0], crossh[1]-20)
            , (crossh[0], crossh[1]+20)
            , 2)

        # show floating text messages for a certain amount of frames
        expired_texts = []
        for obj in rendered_texts:
            if obj[2] > 0:
                naytto.blit(obj[0], (obj[1].pos[0] + obj[1].__class__.width, obj[1].pos[1] - 20)) 
                obj[2] -= 1
            else:
                expired_texts.append(obj)
        
        for obj in expired_texts:
            rendered_texts.remove(obj)
        
        pygame.display.flip()
        kello.tick(60)

def congrats():
    naytto.fill((0,0,0))
    y = 320
    for s in f"CONGRATULATIONS!\nYOU DID IT!\nYOUR SCORE: {player.score:.0f}".split("\n"):
        naytto.blit(font_pop_up.render(s ,True, (255, 255, 255)), (400, y))
        y += 36

    pygame.display.flip()
    pygame.time.wait(3000)

# Pythagoras + center points (?)
distance = lambda x, y: math.sqrt(
    math.pow((x.pos[0] + x.__class__.width/2) - (y.pos[0] + y.__class__.width/2), 2) # x^2
    + 
    math.pow((x.pos[1] + x.__class__.height/2) - (y.pos[1] + y.__class__.height/2), 2) # y^2
)

class Collectible:
    sprites = [pygame.image.load("kolikko.png")]
    width = sprites[0].get_width()
    height = sprites[0].get_height()

    sx = nw - width
    sy = nh - height

    def __init__(self):
        self._value = 1
        self.pos = (randint(0, Collectible.sx-1), randint(0, Collectible.sy-1))
        self.collected = False

    def update(self):
        if not self.collected:
            self._get_collected()
            naytto.blit(Collectible.sprites[0], self.pos)

    def _get_collected(self):
        if distance(self, player) < 50:
            player.score += self._value
            self.collected = True
            return True
        return False

# TODO: repaint each coin with different color based on PowerUp type
class PowerUp(Collectible):

    def __init__(self):
        super().__init__()
        self._value = 10

    def _get_collected(self):
        if super()._get_collected():
            global rendered_texts
            rendered_texts.append([
                self.__class__.pick_up_txt,     # the pre-rendered text
                self,                           # the text will be positioned in relation to this object
                50                              # n frames to show the text near the object
            ])
            return True
        return False

class PUEnergy(PowerUp):
    pick_up_txt = render("BATTERIES!")

    def _get_collected(self):
        if super()._get_collected():
            player.energy += 100
            return True
        return False

class PUMEnergy(PUEnergy):
    pick_up_txt = render("BATTERIES EXTENDED!")

    def _get_collected(self):
        if super()._get_collected():
            player.max_energy += 100

class PUHealth(PowerUp):
    pick_up_txt = render("REPAIR KIT!")

    def _get_collected(self):
        if super()._get_collected():
            player.health += 100
            return True
        return False

class PUMHealth(PUHealth):
    pick_up_txt = render("CHASSIS UPGRADED!")

    def _get_collected(self):
        if super()._get_collected():
            player.max_health += 100
            
class PUFirePower(PowerUp):
    pick_up_txt = render("MOAR POWER!")

    def _get_collected(self):
        if super()._get_collected():
            player.fire_power *= 2
            
class PUEnergyEfficiency(PowerUp):
    pick_up_txt = render("CHEAPER ATTACKS!")

    def _get_collected(self):
        if super()._get_collected():
            player.energy_efficiency *= 2
            
class PUEnergyRegen(PowerUp):
    pick_up_txt = render("IMPROVED RECHARGE!")

    def _get_collected(self):
        if super()._get_collected():
            player.energy_regen *= 2
             
class PUHealingEfficiency(PowerUp):
    pick_up_txt = render("IMPROVED RECHARGE!")

    def _get_collected(self):
        if super()._get_collected():
            player.healing_efficiency *= 2
             
class PUHealingRate(PowerUp):
    pick_up_txt = render("IMPROVED RECHARGE!")

    def _get_collected(self):
        if super()._get_collected():
            player.healing_rate *= 2
            
class Door():
    sprite = pygame.image.load("ovi.png")
    width = sprite.get_width()
    height = sprite.get_height()
    sx = nw - width
    sy = nh - height

    def __init__(self):
        self._enabled = False
        self.pos = (randint(0, Door.sx), randint(0, Door.sy))
        
    def update(self):
        global collectibles

        for c in collectibles:
            if not c.collected:
                return False

        if not self._enabled:
            self._enabled = True
        else:
            naytto.blit(Door.sprite, self.pos)

            if distance(self, player) < 50:
                return True
            else:
                return False
        
class Weapon:
    def __init__(self, chargeable = False):
        self.level = 0
        self.charging = False
        self._chargeable = chargeable

class Eye(Weapon):
    effects = [render(x) for x in "PEW!,PSSHT!,BZZZZ!,ZAP!,KSSSH!,KFFF!".split(",")]
    cost = 30
    left = ((17, 14),                # standing still
            ((20,14), (15, 15)),     # tilted 5 deg
            ((22,14), (13, 16)))     # tilted 10 deg
    
    right = ((32, 14),               # standing still
             ((34,16), (29, 14)),    # tilted 5 deg
             ((36,16), (27, 14)))    # tilted 10 deg

    def __init__(self, side: int):
        super().__init__()
        self.pos = Eye.left if side == 0 else Eye.right

# TODO: should be used when enemies mob up on you
class CloseCombat(Weapon):
    cost = 10

class MovingCharacter:
    def __init__(self):
        # public
        self.energy = self.max_energy = \
        self.health = self.max_health = 1000
        self._healing = False
        
        # private and inheritable
        self._up = self._down = self._left = self._right = self._running = False
        self._speeds = [2, 3]   # walking, running
        self._mov_anim_tick = 0

    def _moving(self):
        return self._up or self._down or self._left or self._right

    def _move(self):
        sx = Player.sx if isinstance(self, Player) else Ghost.sx
        sy = Player.sy if isinstance(self, Player) else Ghost.sy
        v = self._speeds[1 if self._running else 0]
        
        if self.health > 0:
            # standing still
            state = 0

            if self._up:
                if self.pos[1] - v >= 0:
                    self.pos[1] -= v
                else:
                    self._up = False

            if self._down:
                if self.pos[1] + v <= sy:
                    self.pos[1] += v
                else:
                    self._down = False

            if self._left:
                if self.pos[0] - v >=0:
                    self.pos[0] -= v
                else:
                    self._left = False

            if self._right:
                if self.pos[0] + v <= sx:
                    self.pos[0] += v
                else:
                    self._right = False
            
            if self._moving():
                state += 1
                self._mov_anim_tick += 1
                
                if self._running:
                    state += 1
            else:
                self._mov_anim_tick = 0
        
            return state
        else:
            return -1

    def dying(self):
        rendered_texts.append([
            choice(self.__class__.yells),    # the pre-rendered text itself
            self,                            # the text will be positioned in relation to this object:
            100                              # n frames to show the text near the robot
        ])

class Ghost(MovingCharacter):

    original_timeout = timeout = 120
    seekout_range = 200
    hunting_range = 30
    sprite = pygame.image.load("hirvio.png")
    yells = [render(x) for x in "BOO!,BOOHOO!!!".split(",")]
    
    width = sprite.get_width()
    height = sprite.get_height()
    sx = nw - width 
    sy = nh - height 

    def __init__(self):
        super().__init__()
        self.pos = [randint(0, Ghost.sx), randint(0, Ghost.sy)]

    def update(self):
        if self.health > 0:
            self.__seek_n_destroy()
            naytto.blit(Ghost.sprite, self.pos)

    def __seek_n_destroy(self):
        dp = distance(self, player)

        if player.health == 0 or dp > self.__class__.seekout_range:
            # look for a collectible to guard instead
            for c in collectibles:
                if c.collected:
                    continue

                dc = distance(self, c)
                if dc in range(50, self.__class__.seekout_range):
                    self.__close_in(c,self._speeds[0])
                    break

            self.__idle()
        else:
            if dp > self.__class__.hunting_range:
                self.__close_in(player, self._speeds[0 if dp > 100 else 1])
                self.__idle()
            else:
                player.health -= 1 # attack
                if player.health <= 0:
                    player.dying()

    def __idle(self):
        dx = choice([-self._speeds[0], 0, self._speeds[0]])
        dy = choice([-self._speeds[0], 0, self._speeds[0]])

        if self.pos[0] + dx in range(0, Ghost.sx):
            self.pos[0] += dx

        if self.pos[1] + dy in range(0, Ghost.sy):
            self.pos[1] += dy

    def __close_in(self, target, v: int):
        if Ghost.timeout != 0:
            return

        # direction x
        if target.pos[0] > self.pos[0]:
            self.pos[0] += v
        else:
            self.pos[0] -= v

        # direction y
        if target.pos[1] > self.pos[1]:
            self.pos[1] += v
        else:
            self.pos[1] -= v


    def got_shot(self):
        global rendered_texts

        self.health -= Eye.cost*player.fire_power*2
        # dying
        if self.health <= 0:
            self.dying()
            player.score += 50
        else:
            rendered_texts.append([render(f"{self.health}/{self.max_health}"), self, 15])

# TODO: repaint sprite, or not? it's actually better to not know which one is the long range...
class Nightmare(Ghost):
    seekout_range = Ghost.seekout_range * 3
    hunting_range = Ghost.hunting_range
    yells = Ghost.yells

    def __init__(self):
        super().__init__()
        self.health = self.max_health = 500
        self._speeds = [1, 2] # slower than Ghost

class Player(MovingCharacter):

    # standing still
    sprites = [[pygame.image.load("robo.png")]]
    sprites[0].append(pygame.transform.rotate(sprites[0][0], -90))
    # walking
    sprites.append([pygame.transform.rotate(sprites[0][0], -5), pygame.transform.rotate(sprites[0][0], 5)])
    # running
    sprites.append([pygame.transform.rotate(sprites[0][0], -10), pygame.transform.rotate(sprites[0][0], 10)])

    width = sprites[0][0].get_width()
    height = sprites[0][0].get_height()
    sx = nw - width
    sy = nh - height

    yells = [render(x) for x in "EEK!,AAARGH!!".split(",")]

    def __init__(self):
        super().__init__()
        self.eyes = [Eye(0), Eye(1)]
        self.energy_regen = 1
        self.score = 0
        self.pos = [randint(0, Player.sx), randint(0, Player.sy)]
        self.fire_power = 1
        self.energy_efficiency = 1
        self.healing_rate = 1
        self.healing_efficiency = 5        
            
    def __redraw(self, state: int):
        if self.health > 0:
            # standing still
            if state == 0:
                spr = Player.sprites[0][0]
            
            # walking
            elif state == 1:
                spr = Player.sprites[1][self._mov_anim_tick//5 % 2]
            
            # running
            elif state == 2:
                spr = Player.sprites[2][self._mov_anim_tick//5 % 2]
        else:
            # dead
            spr = Player.sprites[0][1]
        
        # draw the character
        naytto.blit(spr, (self.pos[0], self.pos[1]))

    def __process_events(self):
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
                if ev.key == pygame.K_TAB:
                    self._healing = True
                if ev.key == pygame.K_LSHIFT:
                    self._running = True
                if ev.key == pygame.K_0:
                    # CHEAT CODE HERE!!!
                    global enemies, collectibles
                    for c in collectibles:
                        c.collected = True
                    for e in enemies:
                        e.health = 0
                    # door should be visible now
                
            if ev.type == pygame.KEYUP:
                if ev.key == pygame.K_w:
                    self._up = False
                if ev.key == pygame.K_s:
                    self._down = False
                if ev.key == pygame.K_a:
                    self._left = False
                if ev.key == pygame.K_d:
                    self._right = False
                if ev.key == pygame.K_TAB:
                    self._healing = False
                if ev.key == pygame.K_LSHIFT:
                    self._running = False

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == pygame.BUTTON_LEFT:
                    self.eyes[0].charging = True

                if ev.button == pygame.BUTTON_RIGHT:
                    self.eyes[1].charging = True

            if ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == pygame.BUTTON_LEFT:
                    self.eyes[0].charging = False
                    
                if ev.button == pygame.BUTTON_RIGHT:
                    self.eyes[1].charging = False

    def update(self):
        if self.health > 0:
            self.__process_events()
            self.__manage_energy()
        self.__redraw(self._move())
        self.__ready_weapons()
        self.__heal()
    
    def __heal(self):
        if not self._moving() and self._healing \
        and self.energy - self.healing_efficiency > 0 \
        and self.health + self.healing_rate < self.max_health:
            self.health += self.healing_rate
            self.energy -= self.healing_efficiency

    def __shoot(self, eye: Eye):
        global rendered_texts, enemies
        
        if self._running:
            pos = eye.pos[2][self._mov_anim_tick//5 % 2]
        elif self._up or self._down or self._left or self._right:
            pos = eye.pos[1][self._mov_anim_tick//5 % 2]
        else:
            pos = eye.pos[0]

        # draw LASER BEAM
        pygame.draw.line(naytto, (255, 0, 0)
            , (self.pos[0]+pos[0], self.pos[1]+pos[1])
            , crossh
            , 10)

        rendered_texts.append([choice(eye.effects), self, 15])

        for enemy in enemies:
            if crossh[0] in range(enemy.pos[0], enemy.pos[0] + Ghost.width) \
            and crossh[1] in range(enemy.pos[1], enemy.pos[1] + Ghost.height) \
            and enemy.health > 0:
                enemy.got_shot()
                
                break # 1 shot is for 1 ghost only, would be too easy otherwise...

    def __ready_weapons(self):
        for eye in self.eyes:
            if eye.charging:
                if self.energy > 0:
                    self.energy -= 1 / self.energy_efficiency
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

    def __manage_energy(self):
        # regenerating energy while standing still
        if self.energy < self.max_energy and not self._moving():
            self.energy += self.energy_regen

        if self._running and self._moving():
            if self.energy > 0:
                self.energy -= self.energy_regen * 2
            else:
                self._running = False

# TODO
class SomethingFunny(MovingCharacter):
    pass

main_menu()