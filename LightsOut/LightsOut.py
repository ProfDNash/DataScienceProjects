# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 03:17:42 2020

@author: Nash
"""

import pygame
from pygame.locals import *
import numpy as np

 
class PygView(object):

  
    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments 
        """
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()  
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 24, bold=True)

    def paint(self,Mat = np.ones((5,5))):
        """painting on the surface"""
        #------- try out some pygame draw functions --------
        # pygame.draw.line(Surface, color, start, end, width) 
        # pygame.draw.rect(Surface, color, Rect, width=0): return Rect
        #pygame.draw.rect(self.background, (0,255,0), (50,50,100,25)) # rect: (x1, y1, width, height)
        # pygame.draw.circle(Surface, color, pos, radius, width=0): return Rect
        # pygame.draw.polygon(Surface, color, pointlist, width=0): return Rect
        # pygame.draw.arc(Surface, color, Rect, start_angle, stop_angle, width=1): return Rect
        # ------------------- blitting a Board --------------
        myboard = Board(mat=Mat)
        myboard.blit(self.background)

    def run(self):
        """The mainloop
        """
        randMat = np.random.randint(2,size=25).reshape((5,5))
        size = 5
        self.paint(Mat = randMat) 
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if pos[0]%55<=50 and pos[1]%55<=50:  ##make sure the click isn't on a boundary
                        row = pos[0]//55
                        col = pos[1]//55
                        print(row,col)
                        for i in range(size):
                            for j in range(size):
                                if (np.abs(row-i)<2 and col==j) or (row==i and np.abs(col-j)<2):
                                    randMat[i,j] = (randMat[i,j]+1)%2 ##toggle light and adjacent lights
                        self.paint(Mat = randMat)

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            self.draw_text("FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
                           self.clock.get_fps(), " "*5, self.playtime))

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            
        pygame.quit()


    def draw_text(self, text):
        """Center text in window
        """
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(surface, (50,350))
        
class Board(object):
    """This is meant to be a method to draw the current board"""
    def __init__(self, size = 5, length = 50, x = 5, y = 5, mat=np.ones((5,5))):
        self.size = size
        self.length = length
        self.x = x
        self.y = y
        self.mat = mat
        ##create a surface to fit a size-by-size grid of boxes
        self.surface = pygame.Surface(((self.length+5)*self.size, (self.length+5)*self.size))
        for i in range(self.size):
            for j in range(self.size):
                pygame.draw.rect(self.surface, (0,255*mat[i,j],255), ((self.length+5)*i, (self.length+5)*j, self.length, self.length))
        self.surface = self.surface.convert() # for faster blitting. 
        # to avoid the black background, make black the transparent color:
        #self.surface.set_colorkey((0,0,0))
        #self.surface = self.surface.convert_alpha() # faster blitting with transparent color
                
    def blit(self,background):
        background.blit(self.surface, (0,0))
            

class Box(object):
    """this is not a native pygame sprite but instead a pygame surface"""
    def __init__(self, side = 50, color=(0,0,255), x=320, y=240):
        """create a (black) surface and paint a blue ball on it"""
        self.side = side
        self.color = color
        self.x = x
        self.y = y
        # create a rectangular surface for the ball 50x50
        self.surface = pygame.Surface((2*self.side,2*self.side))    
        # pygame.draw.circle(Surface, color, pos, radius, width=0) # from pygame documentation
        #pygame.draw.circle(self.surface, color, (radius, radius), radius) # draw blue filled circle on ball surface
        pygame.draw.rect(self.surface, color, (0,0,side,side)) # rect: (x1, y1, width, height)
        self.surface = self.surface.convert() # for faster blitting. 
        # to avoid the black background, make black the transparent color:
        self.surface.set_colorkey((0,0,0))
        self.surface = self.surface.convert_alpha() # faster blitting with transparent color
        
    def blit(self, background):
        """blit the Ball on the background"""
        background.blit(self.surface, ( self.x, self.y))


    
####

if __name__ == '__main__':

    # call with width of window and fps
    PygView().run()