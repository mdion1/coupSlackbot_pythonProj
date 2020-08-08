import random

class CoupGame:
    CARD_NAMES = [ "assassin", "contessa", "duke", "captain", "ambassador" ]
    def __init__(self, Name: str):
        self._name = Name
        self._playerDict = {}
        self._deck = []
        self._deadCards = []
        self._initDeck()
    
    def getStatus(self, playerName = 'all', maskCards = True):
        ret = []
        playersToReport = []
        if playerName.lower() == 'all':
            playersToReport = self._playerDict.values()
        else:
            if self.isValidPlayer(playerName):
                playersToReport.append(self._playerDict[playerName])
        for player in playersToReport:
            ret.append(player.summary(maskCards))
        ret.append(self.getDeadCards())
        return '\n'.join(ret)
        #todo: add dead cards
    def getDeadCards(self):
        ret = "Dead cards:"
        if len(self._deadCards) < 1:
            return ' '.join([ret, "none"])
        else:
            return ' '.join([ret, ', '.join(self._deadCards)])
    
    def AddPlayer(self, playerName: str):
        if playerName in self._playerDict:
            errStr = player + " is already added to the game"
            return errStr
        else:
            self._playerDict[playerName] = Player(playerName)
            returnString = playerName + " added to game"
            return returnString

    def _initDeck(self, numCopiesPerCard = 3):
        for i in range(0, numCopiesPerCard):
            for cardName in self.CARD_NAMES:
                self._deck.append(cardName.lower())

    def isValidPlayer(self, playerName: str):
        return playerName in self._playerDict.keys()
    
    def getPlayerHand(self, playerName: str, cardsLeft = []):
        ret = ""
        if self.isValidPlayer(playerName):
            ret = self._playerDict[playerName].getHand(cardsLeft)
        return ret

    def cardsRemainingInDeck(self):
        return len(self._deck)
    
    def playerDrawsCard(self, playerName: str):
        ret = ""
        if self.isValidPlayer(playerName):
            cardsInDeck = len(self._deck)
            if cardsInDeck > 0:
                index = random.randint(0, cardsInDeck - 1)
                cardDrawn = self._deck.pop(index)
                ret = cardDrawn
                self._playerDict[playerName].addCard(cardDrawn)
        return ret

    def PlayerTakeCoins(self, playerName:str, numCoins: int):
        if not self.isValidPlayer(playerName):
            return False
        self._playerDict[playerName].addCoin(numCoins)
        return True

    def PlayerReturnCoinsToBank(self, playerName:str, numCoins: int):
        if not self.isValidPlayer(playerName):
            return False
        self._playerDict[playerName].removeCoins(numCoins)
        return True

    def playerStealsFromPlayer(self, playerName_thief: str, playerName_target: str):
        if not self.isValidPlayer(playerName_thief):
            return False
        if not self.isValidPlayer(playerName_target):
            return False
        if self._playerDict[playerName_target].removeCoins(2):
            self._playerDict[playerName_thief].addCoin(2)
            return True
        return False

    def playerGaveCoinsToPlayer(self, playerName_donor: str, playerName_target: str):
        if not self.isValidPlayer(playerName_donor):
            return False
        if not self.isValidPlayer(playerName_target):
            return False
        if self._playerDict[playerName_donor].removeCoins(2):
            self._playerDict[playerName_target].addCoin(2)
            return True
        return False
        
    
    def playerReplaceCard(self, playerName: str, cardName: str):
        if not cardName.lower() in self.CARD_NAMES:
            return False
        if not self.isValidPlayer(playerName):
            return False

        if self._playerDict[playerName].removeCard(cardName):
            self._deck.append(cardName)
            return True
        return False
    
    def playerKillCard(self, playerName: str, cardName: str):
        playerDead = False
        if not cardName.lower() in self.CARD_NAMES:
            return False, playerDead
        if not self.isValidPlayer(playerName):
            return False, playerDead

        if self._playerDict[playerName].removeCard(cardName, kill=True):
            self._deadCards.append(cardName)
            if self._playerDict[playerName].getDeadCards() >= 2:
                playerDead = True
            return True, playerDead
        return False, playerDead
            


'''class Card:
    def __init__(self, name: str):
        self._name = name
    def name(self):
        return self._name'''

class Player:
    def __init__(self, name: str):
        self._name = name
        self._cards = []
        self._coins = 0
        self._deadCards = 0
    
    def summary(self, hideCardIdentities):
        if hideCardIdentities:
            return str(self._name + ": " + str(len(self._cards)) + " cards, " + str(self._coins) + " coins")
        else:
            return str("Your cards: " + self.getHand() + "\nCoins: " + str(self._coins))
    
    def addCoin(self, numCoins = 1):
        self._coins += abs(numCoins)
    
    def removeCoins(self, numCoins = 1):
        numCoins = abs(numCoins)
        if self._coins < numCoins:
            return False
        self._coins -= numCoins
        return True

    def addCard(self, cardName: str):
        self._cards.append(cardName)
    
    def removeCard(self, cardName: str, kill = False):
        len1 = len(self._cards)
        success = True
        try:
            self._cards.remove(cardName)
            if kill:
                self._deadCards += 1
        except:
            success = False
        return success
    
    def getHand(self, cardsLeft = []):
        cardsLeft.append(len(self._cards))
        return ', '.join(self._cards)

    def getDeadCards(self):
        return self._deadCards