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
from random import randint


class Character:
    
    def __init__(self):

        # should have gone with simple booleans....
        self.movement = 0b000000

    def _up():
        return True if self._movement & 0b000001 == 0b000001 else False

    def _down():
        return True if self._movement & 0b000010 == 0b000010 else False

    def _left():
        return True if self._movement & 0b000100 == 0b000100 else False
    
    def _right():
        return True if self._movement & 0b001000 == 0b001000 else False

    def _running():
        return True if self._movement & 0b010000 == 0b010000 else False

    def _dashing():
        return True if self._movement & 0b100000 == 0b100000 else False


print(0b10 & 0b01)

exit()


pygame.init()
naytto = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("unambitious osa14 yritys")
pygame.mouse.set_visible(False)
kello = pygame.time.Clock()
fHUD = pygame.font.SysFont("Arial", 24)
fPopUp = pygame.font.SysFont("Arial", 34)

mov_anim_tick = 0
robo_still = pygame.image.load("robo.png")
robo_walk = [pygame.transform.rotate(robo_still,-5), pygame.transform.rotate(robo_still,5)]
robo_run = [pygame.transform.rotate(robo_still,-10), pygame.transform.rotate(robo_still,10)]

# näitä vilautetaan kun ammutaan
float_txt = [
    pygame.transform.rotate(fPopUp.render(x, True, (255, 255, 255)),randint(-15,15)) \
    for x in "PEW!,PSSHT!,BZZZZ!,ZAP!,KSSSH!,KFFF!,AAAARGH!!!!".split(",")
]
persistents = []
crossh = (0,0)



eyes = [{
        'level': 0,
        'charging': False,

        # GIMP:sta tyyliin suurin piirtein
        'pos': (
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
    },{
        'level': 0,
        'charging': False,
        'pos': (
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
    }
]

rw = robo_still.get_width()
rh = robo_still.get_height()
sx = naytto.get_width() - rw
sy = naytto.get_height() - rh


# player pos and stats
x = randint(0, sx)
y = randint(0, sy)
speed0 = speed = 2
max_energy = energy = 100
max_hull = hull = 1000
points = 0
eye_cost = 30

up = down = left = right = running = dashing = False


def use_energy(diff: int):
    global energy, max_energy, speed, speed0
    if energy + diff in range(0, max_energy+1):
        energy += diff
        return True
    else:
        # revert to walking
        speed = speed0
    return False

def shoot(eye: dict):
    global x, y, rw, crossh, naytto, running, left, right, up, down, mov_anim_tick, float_txt, persistents
    
    if running:
        pos = eye["pos"][2][mov_anim_tick//5 % 2]
    elif up or down or left or right:
        pos = eye["pos"][1][mov_anim_tick//5 % 2]
    else:
        pos = eye["pos"][0]


    # draw line from the eye to the mouse cursor
    pygame.draw.line(naytto, (255, 0, 0)
        , (x+pos[0], y+pos[1])
        , crossh
        , 10)

    # firing sound made visible
    persistents.append([
        
        # the pre-rendered text itself
        float_txt[randint(0, len(float_txt)-1)], 
        
        # n frames to show the text near the robot
        15

    ])
    
def weapons():
    global eyes, eye_cost
    for eye in eyes:
        if eye["charging"]:
            if use_energy(-1):
                eye["level"] += 1
            if eye["level"] == eye_cost:
                shoot(eye)
                eye["level"] = 0
                eye["charging"] = False
        else:
            if eye["level"] -1 >= 0:
                eye["level"] -= 1



while True:
    
    for tapahtuma in pygame.event.get():
        if tapahtuma.type == pygame.KEYDOWN:
            if tapahtuma.key == pygame.K_ESCAPE:
                exit()
            if tapahtuma.key == pygame.K_w:
                up = True
            if tapahtuma.key == pygame.K_s:
                down = True
            if tapahtuma.key == pygame.K_a:
                left = True
            if tapahtuma.key == pygame.K_d:
                right = True
            if tapahtuma.key == pygame.K_LSHIFT:
                speed *= 2
                running = True
            if tapahtuma.key == pygame.K_SPACE:
                speed *= 20
                dashing = True
            

        if tapahtuma.type == pygame.KEYUP:
            if tapahtuma.key == pygame.K_w:
                up = False
            if tapahtuma.key == pygame.K_s:
                down = False
            if tapahtuma.key == pygame.K_a:
                left = False
            if tapahtuma.key == pygame.K_d:
                right = False
            if tapahtuma.key == pygame.K_LSHIFT:
                speed /= 2
                running = False

        if tapahtuma.type == pygame.MOUSEMOTION:
            crossh = tapahtuma.pos
        
        if tapahtuma.type == pygame.MOUSEBUTTONDOWN:
            if tapahtuma.button == pygame.BUTTON_LEFT:
                eyes[0]['charging'] = True
                speed /= 2

            if tapahtuma.button == pygame.BUTTON_RIGHT:
                eyes[1]['charging'] = True
                speed /= 2

        if tapahtuma.type == pygame.MOUSEBUTTONUP:

            if tapahtuma.button == pygame.BUTTON_LEFT:
                eyes[0]['charging'] = False
                speed *= 2
                
            if tapahtuma.button == pygame.BUTTON_RIGHT:
                eyes[1]['charging'] = False
                speed *= 2

        if tapahtuma.type == pygame.QUIT:
            exit()


    if dashing:
        if not use_energy(-speed):
            speed /= 20

    if up:
        if y-speed >= 0:
            y -= speed
        else:
            up = False

    if down:
        if y+speed <= sy:
            y += speed
        else:
            down = False

    if left:
        if x-speed >=0:
            x -= speed
        else:
            left = False

    if right:
        if x+speed <= sx:
            x += speed
        else:
            right = False
    
    if left or right or up or down:
        mov_anim_tick += 1
        
        if running:
            use_energy(-speed)
            robo = robo_run[mov_anim_tick//5 % 2]
        elif dashing:
            dashing = False
        else:
            speed = speed0
            robo = robo_walk[mov_anim_tick//5 % 2]
    else:
        robo = robo_still
        mov_anim_tick = 0
        use_energy(speed)


    naytto.fill((40, 40, 40))
    
    naytto.blit(robo, (x, y))

    weapons()

    hud = fHUD.render(f"INTEGRITY: {hull:.0f}, ENERGY: {energy:.0f}, POINTS: {points}", True, (255, 255, 255))
    naytto.blit(hud, (10, sy+rh-20))


    # draw crosshair, dimming hor and ver hairs by charge level
    pygame.draw.line(naytto, (255 - eyes[0]['level'], 255, 255)
        , (crossh[0]-20, crossh[1])
        , (crossh[0]+20, crossh[1])
        , 2)
    
    pygame.draw.line(naytto, (255 - eyes[1]['level'], 255, 255)
        , (crossh[0], crossh[1]-20)
        , (crossh[0], crossh[1]+20)
        , 2)


    cleanup_persistents = []

    # show floating text messages for a certain amount of frames
    for obj in persistents:
        if obj[1] > 0:
            naytto.blit(obj[0], (x + rw, y - 20)) 
            obj[1] -= 1

        else:
            cleanup_persistents.append(obj)
    
    # remove above texts
    for obj in cleanup_persistents:
        persistents.remove(obj)

    
    pygame.display.flip()

    kello.tick(60)