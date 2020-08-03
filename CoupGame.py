import random

class CoupGame:
    def __init__(self, Name: str):
        self.name = Name
        self._playerDict = {}
        self._deck = []
        self.initDeck()
    
    def AddPlayer(self, playerName: str):
        if playerName in self._playerDict:
            errStr = player + " is already added to the game"
            return errStr
        else:
            self._playerDict[playerName] = Player(playerName)
            returnString = playerName + " added to game"
            return returnString

    def initDeck(self, numCopiesPerCard = 3):
        for i in range(0, numCopiesPerCard):
            self._deck.append(Card("Assassin"))
            self._deck.append(Card("Contessa"))
            self._deck.append(Card("Captain"))
            self._deck.append(Card("Duke"))
            self._deck.append(Card("Ambassador"))

    def isValidPlayer(self, playerName: str):
        return playerName in self._playerDict.keys()
    
    def getPlayerHand(self, playerName: str):
        ret = ""
        if self.isValidPlayer(playerName):
            ret = _playerDict[playerName].getHand()
        return ret
    
    def playerDrawsCard(self, playerName: str):
        ret = ""
        if self.isValidPlayer(playerName):
            cardsInDeck = len(self._deck)
            if cardsInDeck > 0:
                index = random.randint(0, cardsInDeck - 1)
                cardDrawn = self._deck.pop(index)
                ret = cardDrawn.name()
                self._playerDict[playerName].addCard(cardDrawn)
        return ret
            


class Card:
    def __init__(self, name: str):
        self._name = name
    def name(self):
        return self._name

class Player:
    def __init__(self, name: str):
        self._name = name
        self._cards = []
        self._coins = 0
    
    def addCoin(self, numCoins = 1):
        self._coins += abs(numCoins)
    
    def removeCoins(self, numCoins = 1):
        self._coins -= abs(numCoins)
        self._coins = max(self._coins, 0)

    def addCard(self, card: Card):
        self._cards.append(card)
    
    def removeCard(self, card: Card):
        len1 = len(self._cards)
        success = True
        try:
            self._cards.remove(card)
        except:
            success = False
        return success
    
    def getHand(self):
        ret = []
        for card in self._cards:
            ret.append(card.name())
        return ', '.join(ret)