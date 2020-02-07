"""
Created on Fri Jan 24 07:32:32 2020

@author: David A. Nash
"""

import numpy as np
from itertools import permutations
#from sympy.utilities.iterables import multiset_permutations ##alternative way for generating all permutations
#import random


class Player:
    def __init__(self, position, cards, cursed):
        self.position = position
        self.cards = cards
        self.cursed = cursed
        
def initGame(numPlayers):
    global PlayerList
    global Deck
    if numPlayers<1 or numPlayers>4:
        print("Error, can only be played with 1 to 4 players")
    else:
        PlayerList = [Player([0,0],[], False), Player([0,0],[], False), Player([0,0],[], False), Player([0,0],[], False)]
        PlayerList = PlayerList[:numPlayers]
        ##Shuffle the deck of cards
        Deck = np.random.permutation(Deck)
    return PlayerList

def rollGenerator(n):
    r = np.random.randint(1,high=n+1,size=2)
    return r

def posCreator(): ##top is currently 101
    count = 1
    Positions = np.zeros((5153,2))
    for i in range(102):
        for j in range(i+1,102):
            Positions[count,:] = (i,j);
            count = count+1;
    Positions[count,:] = (101,101)
    return Positions

def cleanPositions(iP1): ##check for positions that are not allowed and eliminate duplicates
    iP1.sort(axis=1)  ##make sure positions are always increasing
    iP1.view('i8,i8,i8').sort(order=['f0','f1'], axis=0)  ##sort them into increasing order
    deleteRows=np.array([])
    compareRow=0
    for i in range(iP1.shape[0]):
        if (iP1[i,0] not in Spots) or (iP1[i,1] not in Spots):
            deleteRows = np.append(deleteRows, i) ##mark row for deletion if off the board
        elif (compareRow!=i) and (np.array_equal(iP1[i,:], iP1[compareRow,:])):
            deleteRows = np.append(deleteRows, i) ##mark duplicates for deletion
        else:
            compareRow=i  ##reassign currentRow if we run into a different allowable position
    deleteRows = deleteRows.astype(int)
    iP1 = np.delete(iP1, deleteRows, axis=0)
    return iP1
    

def applyDie(iP1,die,curse): ##apply a single die in all *allowable* ways
    if die==0:
        die=10
    iP2 = np.array([])
    if iP1[0,0]==101:  ##do not allow movement away from position 101
        print("You already won... No need to keep rolling.")
    else:
        iP2 = np.append(iP2, iP1-(die,0,0))
        iP2 = np.append(iP2, iP1/(die,1,1))
        if curse==False:  ##when cursed, you can only subtract or divide
            iP2 = np.append(iP2, iP1+(die,0,0))
            iP2 = np.append(iP2, iP1*(die,1,1))
        if iP1[0,1]!=101: ##do not allow movement away from position 101
            iP2 = np.append(iP2, iP1-(0,die,0))
            iP2 = np.append(iP2, iP1/(1,die,1))
            if curse==False:  ##when cursed, you can only subtract or divide
                iP2 = np.append(iP2, iP1+(0,die,0))
                iP2 = np.append(iP2, iP1*(1,die,1))
        num = np.int(iP2.shape[0]/3)
        ##transfer data to iP1
        iP1 = iP2.reshape((num,3))
        iP1 = cleanPositions(iP1) #sort, eliminate duplicates and unallowable positions
    return iP1

def applyCard(iP1, card):
    global PlayerList
    iP2 = np.array([])
    if iP1[0,0]==101:
        print("No need to apply cards... you already won!")
    else:
        if 0<card<10:
            ##make sure you only apply cards which haven't already been used
            for i in range(iP1.shape[0]):
                if str(iP1[i,2])[card] == '1': ##then card has already been used
                    continue
                iP2 = np.append(iP2, iP1[i,:]+(card,0,10**(11-card))) ##so card corresponds to digit number card
                iP2 = np.append(iP2, iP1[i,:]-(card,0,-10**(11-card)))
                if iP1[i,1]!=101:
                    iP2 = np.append(iP2, iP1[i,:]+(0,card,10**(11-card)))
                    iP2 = np.append(iP2, iP1[i,:]-(0,card,-10**(11-card)))
        elif 9<card<12:  ##these cards will bump a pawn back to start
            for i in range(iP1.shape[0]):
                iP2 = np.append(iP2,np.array([0,iP1[i,1],100000000000+10**(11-card)]))  ##move lower pawn
                if iP1[i,1]!=101:
                    iP2 = np.append(iP2,np.array([0,iP1[i,0],100000000000+10**(11-card)]))  ##move higher pawn
        num = np.int(iP2.shape[0]/3)
        iP1 = iP2.reshape((num,3))
        iP1 = cleanPositions(iP1)
    return iP1

def cursePlayer(card, playerNum):
    global DiscardPile
    global PlayerList
    if card !=12 and card != 13:
        print('Error.  You cannot curse with card ', card)
    else:
        if len(PlayerList)>1:  ##only curse other players if other players exist
            pToCurse = playerNum
            while pToCurse == playerNum or PlayerList[pToCurse].curse == True:  ##don't curse a player who is already cursed
                pToCurse = np.random.randint(0,len(PlayerList))
            PlayerList[pToCurse].curse = True
        PlayerList[playerNum].cards.remove(card)
        DiscardPile.append(card)

def sendPlayerHome(card, playerNum):
    global DiscardPile
    global PlayerList
    if card !=10 and card != 11:
        print('Error.  You cannot bump with card ', card)
    else:
        offStart = 0
        for j in range(len(PlayerList)):
            if j!= playerNum:
                offStart = offStart + PlayerList[j].position[1]
        if offStart>0:  ##then there are players to bump which aren't at the start 
            pToBump = playerNum
            while pToBump == playerNum or PlayerList[pToBump].position[1]==0:  ##don't bump a player who's pawns are both at the start
                pToBump = np.random.randint(0,len(PlayerList))
            if PlayerList[pToBump].position[0]==0:
                pawnChosen = 1
            else:
                pawnChosen=np.random.randint(0,2)
            PlayerList[pToBump].position[pawnChosen]=0
            PlayerList[pToBump].position.sort()
            PlayerList[playerNum].cards.remove(card)
            DiscardPile.append(card)
        else:
            print("No one to bump.")
    
##function to determine all possible moves given a particular roll and starting position
def moveMapper(roll, pos, availCards, curse):
    partialFlag = 0
    intermediatePos1 = np.array(pos)
    intermediatePos1 = np.append(intermediatePos1, 100000000000)
    #intermediatePos2 = intermediatePos1.reshape((1,3)) ##hopefully a distinct copy of the array
    #intermediatePos1 = intermediatePos1.reshape((1,3))
    ##use the digits to keep track of which cards have been used i.e. 4 has been used means add 10^4
    ##create all possible orderings for applying cards and dice
    if roll[0] == roll[1]:   ##rolled doubles so get 4 copies
        scheme = np.array([str(roll[0]),str(roll[0]),str(roll[0]),str(roll[0])])
    else:
        scheme = np.array([str(roll[0]),str(roll[1])])
    for c in range(len(availCards)):
        if 0<availCards[c]<12:  ##this now includes the send home cards
            scheme = np.append(scheme, 'c'+str(availCards[c]))
    scheme = set(permutations(scheme))
    ##it only makes logical sense to move yourself home at the beginning of your turn, otherwise you waste dice
    if 10 in availCards or 11 in availCards:
        keepset = []
        for x in scheme:
            if x[0]=='c10' or x[0]=='c11':
                keepset.append(x)
        if 10 in availCards and 11 in availCards:
            scheme = []
            for x in keepset:
                if x[1]=='c10' or x[1]=='c11':
                    scheme.append(x)
        else:
            scheme = keepset
    intermediatePos3 = np.array([])
    for order in scheme:
        #print(order)
        intermediatePos2 = intermediatePos1.reshape((1,3))  ##hopefully a distinct copy of the original array
        for item in order:
            #print(item)
            if item[0] == 'c':    ##if the first character is c, apply the given card
                ##ALSO Keep track of positions without using the card!
                intermediatePos2 = np.append(intermediatePos2, applyCard(intermediatePos2, int(item[1:])), axis=0)
            else:
                intermediatePos2 = applyDie(intermediatePos2, int(item), curse)
            if 101 in intermediatePos2[:,0]: ##you can win on a partial turn
                intermediatePos2 = np.array([101,101,100000000000])
                partialFlag = 1
                break
        intermediatePos3 = np.append(intermediatePos3,intermediatePos2)
        if partialFlag == 1:
            break
    num = np.int(intermediatePos3.shape[0]/3)
    intermediatePos3 = intermediatePos3.reshape((num,3))
    finalPos = cleanPositions(intermediatePos3)
    ##take care of self bumping
    delRow = np.array([])
    for i in range(finalPos.shape[0]):
        if finalPos[i,0]==finalPos[i,1] and finalPos[i,0]!=101:
            if finalPos[i,1] !=0 and [0, finalPos[i,1]] in finalPos.tolist():
                delRow = np.append(delRow, i)
            else:
                finalPos[i,0]=0
    ##RE-SORT AND REMOVE DUPLICATES##
    finalPos = np.delete(finalPos, delRow.astype('i8'), axis=0)
    finalPos.view('i8,i8,i8').sort(order=['f0','f1'], axis=0)
    return finalPos.astype('i8')

def bumpChecker(playerNum):
    global PlayerList
    for i in range(len(PlayerList)):
        if i == playerNum:
            continue
        if 0<PlayerList[playerNum].position[0] <101 and PlayerList[playerNum].position[0] in PlayerList[i].position:
            loc = np.where(PlayerList[playerNum].position[0] in PlayerList[i].position)[0][0]
            PlayerList[i].position[loc] = 0
            #print("Player ", i, " bumped back to start!")
        if 0<PlayerList[playerNum].position[1] <101 and PlayerList[playerNum].position[1] in PlayerList[i].position:
            loc = np.where(PlayerList[playerNum].position[1] in PlayerList[i].position)[0][0]
            PlayerList[i].position[loc] = 0
            #print("Player ", i, " bumped back to start!")

def drawACard(playerNum,oldPos,newPos):
    global Deck
    global DiscardPile
    global PlayerList
    global Primes
    newPrimeFlag = -1
    rollAgain = 0
    posChangeFlag = 0
    ##If at least one pawn lands on a new prime, draw a card
    if newPos[0] in Primes and newPos[0] not in oldPos:
        newPrimeFlag += 1
    if newPos[1] in Primes and newPos[1] not in oldPos:
            newPrimeFlag += 2
    ##so 0 means 1st pos only, 1 means 2nd pos only, 2 means both are new
    if newPrimeFlag==2: ##then we need to choose which pawn to apply the card to
        ##for now, let's do that randomly
        newPrimeFlag = np.random.randint(0,2)
    if newPrimeFlag>-1:
        Draw = Deck[-1]
        #print("Card drawn:", Cards[str(Draw)])
        Deck = Deck[:-1]
        ##above 13 are the action cards which must be used immediately
        if Draw>13:  ##action card
            DiscardPile.append(Draw)
            if Draw<17:  ##roll Again
                rollAgain = 1
            elif 16<Draw<19:##50/50
                posChangeFlag = 1
                if newPos[newPrimeFlag] < 50:
                    newPos[newPrimeFlag] += 50
                else:
                    newPos[newPrimeFlag] -= 50
                #print("50/50 Card changed your position to:", newPos)
            elif 18<Draw<21: ##advance/reverse to nearest
                currLocs = []
                for i in range(len(PlayerList)):
                    currLocs.append(PlayerList[i].position[0])
                    if PlayerList[i].position[1] != 101: #ignore pawns that have already left the board
                        currLocs.append(PlayerList[i].position[1])
                currLocs.sort()
                idx = currLocs.index(newPos[newPrimeFlag])  ##locate chosen pawn in the list
                if idx!=len(currLocs)-1 and Draw==19:  ##move forward if possible to nearest pawn and (later) bump it back to start
                    newPos[newPrimeFlag] = currLocs[idx+1]
                    posChangeFlag = 1
                elif idx!=0 and Draw==20:  ##move backward if possible to nearest pawn and (later) bump it back to start
                    newPos[newPrimeFlag] = currLocs[idx-1]
                    posChangeFlag = 1
            elif Draw == 21:  ##reverse digits
                digits = str(newPos[newPrimeFlag]) ##there are always exactly two digits on Primes
                digits = digits[1]+digits[0]
                newPos[newPrimeFlag] = int(digits)
                posChangeFlag = 1
                #print("Swap digits changed your position to:", newPos)
            elif Draw == 22:  ##Swap any two pawns
                if len(PlayerList)>1:  ##If there's only one player, swapping pawns is meaningless
                    swaps = np.array([0,0])
                    while swaps[0]==swaps[1]:  ##it is also meaningless to swap two pawns from the same player
                        swaps = np.random.randint(0,len(PlayerList),size=2)
                    p1 = np.random.randint(0,2)  ##choose a pawn for the first player
                    if p1 == 1 and PlayerList[swaps[0]].position[1]==101: ##cannot swap with a pawn at 101
                        p1 = 0
                    p2 = np.random.randint(0,2)  ##choose a pawn for the second player
                    if p2 == 1 and PlayerList[swaps[1]].position[1] == 101:
                        p2 = 0
                    temp = PlayerList[swaps[0]].position[p1]
                    PlayerList[swaps[0]].position[p1] = PlayerList[swaps[1]].position[p2]
                    PlayerList[swaps[1]].position[p2] = temp
                    PlayerList[swaps[0]].position.sort()
                    PlayerList[swaps[1]].position.sort()
                    ##no need for change flag, since changes have been made and this cannot result in bumping
            elif Draw == 23:  ##Send to 64
                newPos[newPrimeFlag] = 64
                posChangeFlag = 1
                #print("Send to 64 changed your position to:", newPos)
            elif Draw == 24:  ##Steal a card
                ##First find the players who have cards
                stealable = []
                for i in range(len(PlayerList)):
                    if i != playerNum and len(PlayerList[i].cards)>0:
                        stealable.append(i)
                if len(stealable)>0:  ##then at least one other person has cards
                    stealable = np.random.permutation(stealable)
                    stealfrom = stealable[0]
                    stealcard = PlayerList[stealfrom].cards[np.random.randint(0,len(PlayerList[stealfrom].cards))]
                    PlayerList[playerNum].cards.append(stealcard)
                    PlayerList[stealfrom].cards.remove(stealcard)
        else:  ##the card must be added to the hand, it cannot be used this turn
            PlayerList[playerNum].cards.append(Draw)
        ##Shuffle the discard pile to form a new deck when it is empty
        if len(Deck)<1:
            print("RESHUFFLING THE DISCARD PILE")
            Deck = np.random.permutation(DiscardPile)
            DiscardPile = []
        #print("Current Hand:", PlayerList[playerNum].cards)  
    if posChangeFlag == 1:  ##an action card changed the players position, so recheck for bumping
        if newPos[0]==newPos[1]:
            newPos[0] = 0
            PlayerList[playerNum].position = newPos
        else:
            bumpChecker(playerNum)
    return rollAgain

def takeTurn(playerNum):
    global PlayerList
    curseFlag = 0  ##used to decide whether to curse another player
    if 12 in PlayerList[playerNum].cards:
        curseFlag = np.random.randint(0,2) ##randomly choose whether to use the card or not
        card = 12
    elif 13 in PlayerList[playerNum].cards:
        curseFlag = np.random.randint(0,2)
        card = 13
    if curseFlag == 1:
        cursePlayer(card,playerNum)
    pos = PlayerList[playerNum].position
    #print("Current position:", pos)
    roll = [np.random.randint(0,10),np.random.randint(0,10)]
    #print("Roll:", roll)
    possibleMoves = moveMapper(roll,pos,PlayerList[playerNum].cards,PlayerList[playerNum].cursed)
    #print("Possible Moves:\n", possibleMoves)
    if 101 in possibleMoves[:,0]:
        Move = np.array([101,101]).reshape((1,2)) ##win if you can
        print("Player ", playerNum, " wins!!!!")
        return -1*(playerNum+1)
    elif 101 in possibleMoves: ##if 101 is an option, don't consider other options
        #print("101 is here!")
        TryToWin = np.where(possibleMoves[:,1]==101)[0]
        #print(TryToWin)
        possibleMoves = possibleMoves[TryToWin]
        ##choose a random move
        Move = possibleMoves[np.random.randint(0,possibleMoves.shape[0])]
    else:
        ##choose a random move
        Move = possibleMoves[np.random.randint(0,possibleMoves.shape[0])]
    #print("******\n",possibleMoves,"\n******")
    if Move.shape[0]>2 and Move[2] != 100000000000: ##if cards were used, remove them from hand
        ##ADD CHECK TO AVOID USING CARDS IF IT IS POSSIBLE TO GET TO THE CHOSEN LOCATION WITH FEWER OF THEM
        x = np.where(possibleMoves[:,0]==Move[0])[0]
        y = np.where(possibleMoves[:,1]==Move[1])[0]
        matches = np.intersect1d(x,y)  ##finds indices of all locations matching chosen Move
        bestMove = possibleMoves[matches[0],:]  ##first in the list should have the lowest third entry (saving lower cards)
        for j in range(len(matches)):
            if sum(int(digit) for digit in str(possibleMoves[j,2])[1:]) < sum(int(digit) for digit in str(bestMove[2])[1:]):
                bestMove = possibleMoves[j,:]
        #if bestMove[2] != Move[2]:
        #    print("Move Changed!", Move[2], " to ", bestMove[2])
        Move = bestMove
        if Move[2] != 100000000000:  ##recheck if any cards were used
            for i in range(1,len(str(Move[2]))):
                if str(Move[2])[i]=='1':
                    PlayerList[playerNum].cards.remove(i)
                    DiscardPile.append(i) ##add used cards to discard pile
    PlayerList[playerNum].position = Move[0:2]
    #print("New position:", Move[0:2])
    ##Check for bumping, note: self bumping is already achieved in moveMapper
    bumpChecker(playerNum)
    ##Check for drawing a card and using it if it is an action card
    PlayerList[playerNum].curse = False  ##undo any curses at the end of the turn
    ##if the player did not use the send home cards to augment their own move, they can choose to send someone else back
    if 10 in PlayerList[playerNum].cards:
        if np.random.randint(0,2)==1:
            sendPlayerHome(10,playerNum)
    if 11 in PlayerList[playerNum].cards:
        if np.random.randint(0,2)==1:
            sendPlayerHome(11,playerNum)
    ## after all actions, check to see if they get to draw a card 
    if drawACard(playerNum, pos, Move[0:2]):
        return playerNum ##take another turn!
    else:
        return (playerNum+1)%len(PlayerList)  ##move to next player


## Play a game until someone wins
def playGame(numPlayers):
    global PlayerList
    nTurns = 0
    PlayerList = initGame(numPlayers)
    currPlayer = 0
    while currPlayer>-1 and PlayerList[currPlayer].position[0] != 101:
        #print("\nPlayer ", currPlayer, "'s Turn!")
        currPlayer = takeTurn(currPlayer)
        nTurns += 1
        if nTurns>1000:
            print("Something is wrong")
            break
    return nTurns, (-currPlayer-1)
    
    
      
    
    


#Positions=posCreator()
Spots = np.arange(102)
Primes = [11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
Cards = {
        "1" : "Keeper 1",
        "2" : "Keeper 2",
        "3" : "Keeper 3",
        "4" : "Keeper 4",
        "5" : "Keeper 5",
        "6" : "Keeper 6",
        "7" : "Keeper 7",
        "8" : "Keeper 8",
        "9" : "Keeper 9",
        "10" : "Keeper Send Home",
        "11" : "Keeper Send Home",
        "12" : "Keeper Curse",  ##only sub & div on next turn
        "13" : "Keeper Curse",  ##only sub & div on next turn
        "14" : "Action Roll Again",
        "15" : "Action Roll Again",
        "16" : "Action Roll Again",
        "17" : "Action 50/50",  ##if under 50, add 50 -- if above 50, subtract 50
        "18" : "Action 50/50",  ##if under 50, add 50 -- if above 50, subtract 50
        "19" : "Action Advance to Nearest",
        "20" : "Action Reverse to Nearest",
        "21" : "Action Reverse Digits",
        "22" : "Action Swap Two Pawns",  ##any two
        "23" : "Action Send to 64",
        "24" : "Action Steal a card"
        }
DiscardPile = []
Deck = np.arange(1,25)
PlayerList = []
#PlayerList = initGame(2)

##Model the game with one player
numberOfGames = 0
totalTurns = 0
playerWins = [0,0,0,0]
while numberOfGames < 4:
    print("Game Number:", numberOfGames+1)
    Deck = np.arange(1,25)
    DiscardPile = []
    PlayerList = initGame(3)
    turns, winner = playGame(3)
    totalTurns += turns
    playerWins[winner] += 1
    numberOfGames += 1

print("Avg # Turns to Victory:", totalTurns/numberOfGames)
print("Number of Wins for Each Player:", playerWins)
        
##over 40 games playing "randomly" avg number of turns is 54.125 w/o card stealing or pawn swapping
##over 1000 games, with two players, no sending home, avg # of turns is 71.67  wins 518 to 482       

