# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 03:17:42 2020

@author: Nash
"""

import pygame
from pygame.locals import *
import numpy as np
import time

##define global variable to keep track of known solutions##
KnownSols = {'10001': '11000',
        '01010': '10010',
        '11100': '01000',
        '00111': '00010',
        '10110': '00001',
        '01101': '10000',
        '11011': '00100'}

 
class PygView(object):

    def __init__(self, width=700, height=400, fps=30):
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
        
    def ChooseInitBoard(self):
        ##Not all 5x5 puzzles are solvable, so only pick a solvable one##
        Check1 = np.array([0,1,1,1,0, 1,0,1,0,1, 1,1,0,1,1, 1,0,1,0,1, 0,1,1,1,0])
        Check2 = np.array([1,0,1,0,1, 1,0,1,0,1, 0,0,0,0,0, 1,0,1,0,1, 1,0,1,0,1])
        randMat = np.random.randint(2,size=25)
        while np.dot(randMat,Check1)%2>0 or np.dot(randMat,Check2)%2>0:
            randMat = np.random.randint(2,size=25)
        randMat = randMat.reshape((5,5))
        return randMat
    
    def checkWin(self, flag, Mat = np.ones((5,5))):
        size = len(Mat)
        if flag == True:
            for i in range(size):
                if flag == True:
                    for j in range(size):
                        if Mat[i,j]==1:
                            flag = False
                            break
        return flag

    def paint(self,Mat = np.ones((5,5)),sM = np.zeros((5,5))):
        """painting on the surface"""
        #------- try out some pygame draw functions --------
        # pygame.draw.line(Surface, color, start, end, width) 
        # pygame.draw.rect(Surface, color, Rect, width=0): return Rect
        #pygame.draw.rect(self.background, (0,255,0), (50,50,100,25)) # rect: (x1, y1, width, height)
        # pygame.draw.circle(Surface, color, pos, radius, width=0): return Rect
        # pygame.draw.polygon(Surface, color, pointlist, width=0): return Rect
        # pygame.draw.arc(Surface, color, Rect, start_angle, stop_angle, width=1): return Rect
        # ------------------- blitting a Board --------------
        myboard = Board(mat=Mat,sB = sM)
        myboard.blit(self.background)
        # ------------- drawing the "solve" button ----------
        pygame.draw.rect(self.background, (0,255,255), (97,290,80,35)) # rect: (x1, y1, width, height)
        button = self.font.render('Solve', True, (0,255,0), (0,0,128))
        buttonRect = button.get_rect()
        buttonRect.center = (137,307)
        self.background.blit(button,buttonRect) 
        
        
    def click(self, row, col, M = np.ones((5,5))):
        size = len(M)
        if row>=size or col >=size:
            pass
        else:
            for i in range(size):
                for j in range(size):
                    if (np.abs(row-i)<2 and col==j) or (row==i and np.abs(col-j)<2):
                        M[i,j] = (M[i,j]+1)%2 ##toggle light and adjacent lights
            self.paint(Mat = M)
        return M
    
    def stepOne(self, M = np.ones((5,5)), sM = np.zeros((5,5))):
        size = len(M)
        if 1 in M[:size-1,:]: ##if any lights in the first n-1 cols are lit
            for i in range(size-1): 
                for j in range(size):
                    if M[i,j] == 1:  ##if a light is lit, use the next col over to clear it
                        M = self.click(i+1,j,M)
                        sM[i+1,j] += 1
        ##create a string of the arrangement in the last column
        arr = ''
        for j in range(size):
            arr = arr + str(M[-1,j])    
        return arr, M, sM
    
    def stepTwo(self, M = np.ones((5,5)), sM = np.zeros((5,5)), arr='00000'):
        size = len(M)
        if '1' in arr:  ##if any lights are still on keep solving
            if arr in KnownSols:
                nxt = KnownSols[arr]
                for j in range(size):
                    if nxt[j] == '1':
                        M = self.click(0,j,M) ##click the required boxes in column 0
                        sM[0,j] += 1
            else:
                pass ##add algorithm in unknown cases
        return M, sM
            

    def run(self):
        """The mainloop
        """
        matrix = self.ChooseInitBoard()
        size = matrix.shape[0]
        self.paint(Mat = matrix)
        solMatrix = np.zeros((size,size))  ## keep track of the buttons pressed in working to solve
        running = True
        checkflag = False
        stop = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    checkflag = True  ##check for a win after clicking anything
                    if 97<=pos[0]<=177 and 290<=pos[1]<=325:  ##then we clicked on the 'solve' button
                        left = '11111'
                        while '1' in left: ##if any lights are still on, keep solving
                            left, matrix, solMatrix = self.stepOne(M = matrix, sM=solMatrix)
                            print(left)
                            if '1' in left:
                                matrix, solMatrix = self.stepTwo(M=matrix, sM=solMatrix, arr=left)
                        self.draw_text('Minimal Solution', loc = (40,330))
                    elif 5<=pos[0]%55 and 5<=pos[1]%55:  ##make sure the click isn't on a boundary
                        #checkflag = True  
                        row = pos[0]//55
                        col = pos[1]//55
                        #print(row,col)
                        matrix = self.click(row, col, matrix)
                    
            if stop == False:
                checkflag = self.checkWin(checkflag, Mat=matrix)
            if stop == False:
                if checkflag == True:
                    print('You Win!!')
                    self.paint(Mat=matrix, sM = solMatrix%2)
                    stop = True
                else:
                    milliseconds = self.clock.tick(self.fps)
                    self.playtime += milliseconds / 1000.0
            self.draw_text("Clicks: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
                    np.sum(solMatrix), " "*5, self.playtime))
            self.draw_text("Min Clicks: {:6.3}".format(np.sum(solMatrix%2)), loc=(50,370))

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            
        pygame.quit()


    def draw_text(self, text,loc=(50,350)):
        """Center text in window
        """
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(surface, loc)
        
class Board(object):
    """This is meant to be a method to draw the current board"""
    def __init__(self, size = 5, length = 50, x = 5, y = 5, mat=np.ones((5,5)), sB = np.zeros((5,5))):
        self.size = size
        self.length = length
        self.x = x
        self.y = y
        self.mat = mat
        ##create a surface to fit a size-by-size grid of boxes
        self.surface = pygame.Surface((x+(self.length+5)*self.size*2+150, y+(self.length+5)*self.size*2))
        shift = x + (self.length+5)*self.size+100
        ##draw background for playing board##
        pygame.draw.rect(self.surface, (0,0,1), (0,0,x+(self.length+5)*self.size, y+(self.length+5)*self.size))
        ##draw background for solution board##
        pygame.draw.rect(self.surface, (0,0,1), (shift,0,
                                        x+(self.length+5)*self.size, y+(self.length+5)*self.size))
        ##draw the two boards##
        for i in range(self.size):
            for j in range(self.size):
                pygame.draw.rect(self.surface, (0,255*mat[i,j],255), (x+(self.length+5)*i, 
                                                y+(self.length+5)*j, self.length, self.length))
                pygame.draw.rect(self.surface, (255*sB[i,j],0,255), (shift+x+(self.length+5)*i, 
                                                y+(self.length+5)*j, self.length, self.length))
        self.surface = self.surface.convert() # for faster blitting. 
        self.surface.set_colorkey((0,0,0))
        self.surface = self.surface.convert_alpha() # faster blitting with transparent color
                
    def blit(self,background):
        background.blit(self.surface, (0,0))
            

    
####

if __name__ == '__main__':

    # call with width of window and fps
    PygView().run()