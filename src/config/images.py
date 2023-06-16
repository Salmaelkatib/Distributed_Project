import pygame

class Images:

    def __init__(self):
        self.width = 0
        self.height = 0
        self.track = None
        self.borders = None
        self.LoadImages()

    def LoadImages(self):

        self.track = pygame.image.load("../../assets/track600.png")
        self.borders = pygame.image.load("../../assets/track-border600.png")
        self.block_borders = pygame.image.load("../../assets/track_borders_block600.png")
        self.start = pygame.image.load("../../assets/mStart.png")
        self.start = pygame.transform.scale(self.start, (self.start.get_width() * 1.2, self.start.get_height() * 1.2))
        self.width = self.track.get_width()
        self.height = self.track.get_height()
        self.car1 = pygame.image.load('../../assets/car600.' + str(1) + '.png')
        self.car1 = pygame.transform.scale(pygame.image.load('../../assets/car600.' + str(1) + '.png'), (self.car1.get_width() * 0.5, self.car1.get_height() * 0.5))
        self.car2 = pygame.image.load('../../assets/car600.' + str(2) + '.png')
        self.car2 = pygame.transform.scale(pygame.image.load('../../assets/car600.' + str(2) + '.png'),
                                           (self.car1.get_width() * 0.5, self.car1.get_height() * 0.5))
        self.counter = pygame.image.load('../../assets/coutner.gif')