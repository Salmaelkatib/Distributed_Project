import pygame

from src.config.Config import Config
from src.config.images import Images


class IntializeGame:

    def __init__(self):
        self.players = []
        self.connections = 0

    def addConnections(self):
        self.connections += 1

    def addPlayer(self, player):
        self.players.append(player)

    def removePlayer(self, player):
        self.players.remove(player)

class Game:

        FPS = 100
        run = True
        time = pygame.time.Clock()
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        BLUE = (0, 50, 255)
        RED = (255, 0, 0)

        def __init__(self):
            self.players = []
            self.assets = Images()
            self.config = Config()
            self.cur_player = None
            pygame.font.init()
            self.font = pygame.font.Font('../../assets/fonts/Dodgv2.ttf', 18)
            self.font2 = pygame.font.Font('../../assets/fonts/911v2.ttf', 15)
            self.font3 = pygame.font.Font('../../assets/fonts/Dodgv2.ttf', 8)
            self.font4 = pygame.font.Font('../../assets/fonts/911v2.ttf', 150)
            self.font5 = pygame.font.Font('../../assets/fonts/911v2.ttf', 75)
            self.font6 = pygame.font.Font('../../assets/fonts/911v2.ttf', 35)
            self.img = self.font.render('Cars Racing', False, self.BLACK)
            self.countTimer = self.config.timer['countTimer']
            self.showTimer = False
            self.positionTimer = None
            self.clock = pygame.time.Clock()
            # self.game()

        def loadCar(self, id):
            car = pygame.image.load('../../assets/car600.' + str(id) + '.png')
            car = pygame.transform.scale(pygame.image.load('../../assets/car600.' + str(id) + '.png'),
                                         (car.get_width() * 0.5, car.get_height() * 0.5))
            return car

        def constDraw(self):
            # self.screen.blit(self.assets.grass, (0, 0))
            self.screen.blit(self.img, (40, 360))

        def draw(self, screen, images , pLab):
            for img, pos in images:
                screen.blit(img, pos)
            for player in self.players:
                player.draw()

        def draw_counter(self, s):
            counter = self.font4.render(str(int(5 - s)), False, self.BLUE)
            self.screen.blit(counter, (250, 220))

        def draw_end_game_info(self):
            info = self.font6.render("R - Restart | q - quit", False, self.WHITE)
            self.screen.blit(info, (20, 565))

        def drawWinner(self, name):
            winner = self.font5.render(str("Winner is : "), False, self.RED)
            winner2 = self.font5.render(name, False, self.RED)
            self.screen.blit(winner, (50, 220))
            self.screen.blit(winner2, (100, 270))

        def firstDraw(self):
            self.assetsToDraw = [(self.assets.track, (0, 0)), (self.assets.start, (502, 160)),
                                 (self.assets.borders, (0, 0))]
            self.constDraw()

        def drawCar(self, car, angle, position):
            rotated_image = pygame.transform.rotate(car, angle)
            new_rect = rotated_image.get_rect(
                center=car.get_rect(topleft=position).center)
            self.rect = new_rect
            self.screen.blit(rotated_image, new_rect.topleft)

        def drawAll(self):
            self.draw(self.screen, self.assetsToDraw)

        def game(self):
            self.screen = pygame.display.set_mode((self.assets.width, self.assets.height))
            pygame.display.set_caption("Racing Game")




