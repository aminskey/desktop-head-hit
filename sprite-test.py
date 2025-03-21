import pygame

pygame.init()
screen = pygame.display.set_mode((400, 400))

clock = pygame.time.Clock()

FPS = 60

class SimpleSurface(pygame.sprite.Sprite):
    def __init__(self, size, color, pos=(0, 0)):
        super().__init__()

        self.image = pygame.Surface(size)
        self.image.fill(color)

        self.rect = self.image.get_rect()

        self.rect.center = pos

class Player(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect()

        self.image.fill((255, 100, 100))

        self.rect.center = screen.get_rect().center

        self.vel = pygame.math.Vector2(0, 0)
        self.grav_acc = pygame.math.Vector2(0, 0.65)
        self.friction = 0.8

        self.canJump = False

    def gravity(self, platforms):
        if pygame.sprite.spritecollideany(self, platforms):
            self.vel.y = 0
            self.canJump = True
            self.vel.x *= self.friction

        else:
            self.canJump = False
            self.vel += self.grav_acc


    def movement(self):
        keys = pygame.key.get_pressed()

        if self.canJump:
            if keys[pygame.K_SPACE]:
                self.vel.y = -30
        if keys[pygame.K_RIGHT]:
            self.vel.x = 5
        elif keys[pygame.K_LEFT]:
            self.vel.x = -5

    def update(self, platforms):
        self.gravity(platforms)
        self.movement()

        self.rect.center += self.vel
        if self.vel.length() > 5:
            self.vel.normalize_ip()
            self.vel *= 5

class Text(pygame.sprite.Sprite):
    def __init__(self, msg, script, textColor, pos=(0, 0), shadow : tuple =None, pos2=(2, 3)):
        super().__init__()

        img = script.render(msg, None, textColor)
        self.msg = msg
        # If shadow is not None, then we must expect it to be the shadow color

        if isinstance(shadow, tuple) and len(shadow) == 3:
            self.image = pygame.Surface((img.get_width()*1.02, img.get_height()*1.02)).convert_alpha()
            self.image.fill((23, 16, 1))
            self.image.set_colorkey((23, 16, 1))
            shadowText = Text(msg, script, shadow)
            shadowText.rect.topleft = pos2

            self.image.blit(shadowText.image, shadowText.rect)
            self.image.blit(img, (0, 0))
        else:
            self.image = img.copy()

        self.rect = self.image.get_rect()
        self.color = textColor
        self.rect.center = pos
        self.alphaValue = 255
        self.deltaA = -20

def startScreen():
    textGrp = pygame.sprite.Group()

    fnt1 = pygame.font.Font("pixelart.ttf", 35)
    fnt2 = pygame.font.Font("pixelart.ttf", 20)

    title = Text("Simple Platformer", fnt1, (255, 255, 255), shadow=(0, 0, 0), pos=(screen.get_width()//2, screen.get_height()//3))
    options = [
        "Start",
        "Quit"
    ]

    labels = []

    cursor = Text(">", fnt1, (0, 255, 0))
    index = 0

    textGrp.add(title, cursor)
    for k, i in enumerate(options):
        tmp = Text(i, fnt2, (255, 255, 255), shadow=(0, 0, 0), pos=(screen.get_width()//2, screen.get_height()* (6+k)//10))
        textGrp.add(tmp)
        labels.append(tmp)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    index += 1 if index < len(options) - 1 else 0
                    break
                if event.key == pygame.K_UP:
                    index -= 1 if index > 0 else 0
                    break

                if options[index] == "Start":
                    main()
                    break
                elif options[index] == "Quit":
                    pygame.quit()
                    quit()


        cursor.rect.midright = labels[index].rect.midleft + pygame.math.Vector2(-5, 0)

        screen.fill((100, 100, 255))
        textGrp.draw(screen)

        pygame.display.update()
        clock.tick(FPS)


def main():
    allSprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    players = pygame.sprite.Group()


    gnd = SimpleSurface((screen.get_width(), 50), (0, 255, 0))
    gnd.rect.topleft = (0, screen.get_height() - gnd.image.get_height())

    player = Player((20, 20))
    players.add(player)

    platforms.add(gnd)
    allSprites.add(gnd, player)

    for i in range(3):
        tmp = SimpleSurface((150, 25), (100, 255, 0), pos=(screen.get_width()-100, screen.get_height() * (2+i)/5))
        tmp2 = SimpleSurface((150, 25), (100, 255, 0), pos=(100, screen.get_height() * (2+i)/5 - 50))

        platforms.add(tmp, tmp2)
        allSprites.add(tmp, tmp2)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        players.update(platforms)

        screen.fill((0, 0, 255))
        allSprites.draw(screen)

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    startScreen()