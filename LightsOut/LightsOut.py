# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 03:17:42 2020

@author: Nash
"""

import pygame
from pygame.locals import *
import numpy as np
import time

##define global dictionary to keep track of known solutions##
KnownSols = {'10001': '11000',
        '01010': '10010',
        '11100': '01000',
        '00111': '00010',
        '10110': '00001',
        '01101': '10000',
        '11011': '00100'}

 
class PygView(object):

    def __init__(self, width=700, height=400, fps=60):
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
        # ------------- drawing the "solve" button ----------
        pygame.draw.rect(self.background, (0,255,255), (97,290,80,35)) # rect: (x1, y1, width, height)
        button = self.font.render('Solve', True, (0,255,0), (0,0,128))
        buttonRect = button.get_rect()
        buttonRect.center = (137,307)
        self.background.blit(button,buttonRect) 
        
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
    
    def paintInit(self, Mat = np.ones((5,5)), sM = np.zeros((5,5))):
        '''paint the initial boards'''
        size = len(Mat)
        shift = size + 2
        for row in range(size):
            for col in range(size):
                mycell = Cell(col=col, row=row, color=(0,255*Mat[row,col],255),
                              background=self.background)
                mycell.blit(self.background)
                solcell = Cell(col=col+shift, row=row, color=(255*sM[row,col],0,255),
                               background=self.background)
                solcell.blit(self.background)
        

    def paint(self,col=0, row=0, color=(0,0,255)):
        """update a single cell"""
        #------- try out some pygame draw functions --------
        # pygame.draw.line(Surface, color, start, end, width) 
        # pygame.draw.rect(Surface, color, Rect, width=0): return Rect
        #pygame.draw.rect(self.background, (0,255,0), (50,50,100,25)) # rect: (x1, y1, width, height)
        # pygame.draw.circle(Surface, color, pos, radius, width=0): return Rect
        # pygame.draw.polygon(Surface, color, pointlist, width=0): return Rect
        # pygame.draw.arc(Surface, color, Rect, start_angle, stop_angle, width=1): return Rect
        # ------------------- blitting a cell --------------
        mycell = Cell(col=col,row=row,color=color,background=self.background)
        mycell.blit(self.background)
        
        
        
    def click(self, row, col, M = np.ones((5,5)),sM = np.zeros((5,5))):
        size = len(M)
        shift = size + 2
        if row>=size or col >=size:
            pass
        else:
            for i in range(size):
                for j in range(size):
                    if (np.abs(row-i)<2 and col==j) or (row==i and np.abs(col-j)<2):
                        M[i,j] = (M[i,j]+1)%2 ##toggle light and adjacent lights
                        self.paint(row=i,col=j,color=(0,255*M[i,j],255))
            sM[row,col] = sM[row,col]+1
            ##paint the cell clicked on in the solution
            self.paint(col=col+shift,row=row,color=(255*(sM[row,col]%2),0,255)) 
        return M, sM
    
    def lastRow(self, M=np.ones((5,5))):
        ##create a string of the arrangement in the last column
        size = len(M)
        arr = ''
        for j in range(size):
            arr = arr + str(M[-1,j])    
        return arr
    
    def iterate(self, i, j, step2, size):
        if j<size-1:
            j += 1
        elif step2 == True:
            j = 0
            step2 = False
        else:
            i += 1
            j = 0
            if i == size-1:
                step2 = True
        return i, j, step2
            

##Edit this to run one step of the solving algorithm each frame##
    def run(self):
        """The mainloop"""
        matrix = self.ChooseInitBoard()
        size = matrix.shape[0]
        solMatrix = np.zeros((size,size))  ## keep track of the buttons pressed in working to solve
        self.paintInit(Mat=matrix, sM=solMatrix)
        running = True
        checkflag = False
        stop = False
        solving = False
        step2 = False
        finalRow = ''
        attempt = ''  ##attempt at a solution if solution is unknown
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                ##don't allow clicking while it's solving##
                elif solving == False and event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    checkflag = True  ##check for a win after clicking anything
                    if 97<=pos[0]<=177 and 290<=pos[1]<=325:  ##then we clicked on the 'solve' button
                        solving = True
                        #set initial position for the solving algorithm#
                        i=0
                        j=0
                    elif 5<=pos[0]%55 and 5<=pos[1]%55:  ##make sure the click isn't on a boundary 
                        row = pos[1]//55
                        col = pos[0]//55
                        #print(row,col)
                        matrix, solMatrix = self.click(row, col, matrix, solMatrix)
                elif solving == True:
                    checkFlag=True
                    ##run through the next step in the solving process##
                    if i == 0 and step2 == True:
                        if attempt[j]=='1':
                            matrix, solMatrix = self.click(row=i,col=j,M=matrix, sM=solMatrix)
                    elif i<size-1:  ##then we're running the first part of the algorithm
                        ##if a light is lit, use the next row down to clear it
                        if matrix[i,j] == 1:  
                            matrix, solMatrix = self.click(row=i+1,col=j,M=matrix, sM=solMatrix)
                    elif i == size-1:
                        ##when reaching the last row, get a string for the arrangement
                        temp = self.lastRow(M = matrix)
                        if '1' in temp:  ##if we haven't finished solving yet
                            finalRow = temp
                            print(finalRow)
                            if finalRow in KnownSols:
                                attempt = KnownSols[finalRow]
                                step2 = True
                                i=0
                                j=-1
                            else:
                                pass ##add later when allowing non 5x5 boards
                        else:  ##if we finished, add the information to the dictionary if it is missing
                            solving = False
                            if finalRow not in KnownSols:
                                KnownSols[finalRow] = attempt
                    i,j,step2 = self.iterate(i,j,step2,size)                       
                            
                    
            #if stop == False:
            #    checkflag = self.checkWin(checkflag, Mat=matrix)
            if stop == False:
                if self.checkWin(True, Mat = matrix): #checkflag == True:
                    print('You Win!!')
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
        
class Cell(object):
    """This is meant to be a method to draw a single cell"""
    def __init__(self, length = 50, col = 0, row = 0, color=(0,0,255), 
                 background = pygame.Surface((400,400))):
        self.length = length
        self.x = col*55
        self.y = row*55
        self.color = color
        self.surface = background
        ##draw background for the cell##
        pygame.draw.rect(self.surface, (0,0,1), (self.x,self.y,self.length+10, self.length+10))
        ##draw the cell##
        pygame.draw.rect(self.surface, self.color, (self.x+5, self.y+5, self.length, self.length))
        self.surface = self.surface.convert() # for faster blitting.
                
    def blit(self,background):
        background.blit(self.surface, (0,0))
            

    
####

if __name__ == '__main__':

    # call with width of window and fps
    PygView().run()