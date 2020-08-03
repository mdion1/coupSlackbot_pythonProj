import slack
from slack import WebClient
from CoupGame import CoupGame
import sys

def matchTextInArray(name: str, playerNameList: list):
    ret = False
    for i in range(1, len(playerNameList) + 1):
        joinedList = " ".join(playerNameList[0:i])
        if joinedList == name:
            ret = True
            break
    return ret

ADMIN_USER = "U016EFT271A"

class CoupSlackBotMsgInterface:

    def __init__(self, webclient):
        self._webclient = webclient
        self._gameChannelID = ""
        self._username = "coupslackbot"
        self.icon_emoji = ":robot_face:"
        self._admin_user_IM_channel = ""
        self._playerRoster = {}

    def setAdminUserChatChannel(self, channelName: str):
        if len(self._admin_user_IM_channel) < 1:
            self._admin_user_IM_channel = channelName

    def sendMessageToAdmin(self, text):
        self.sendMessage(text, self._admin_user_IM_channel)

    def sendMessage(self, text, channelId):
        if len(channelId) < 1:
            print("Invalid channel.")
            return
        payload = {
            "channel": channelId,
            "username": self._username,
            "icon_emoji": self.icon_emoji,
            "text": text
        }
        try:
            self._webclient.chat_postMessage(**payload)
        except:
            print(sys.exc_info()[0])
    
    def postGeneralMessage(self, text):
        if len(self._gameChannelID < 1):
            return
        payload = {
            "channel": self._gameChannelID,
            "username": self._username,
            "icon_emoji": self.icon_emoji,
            "text": text
        }
        self._webclient.chat_postMessage(**payload)

    def parseMsg(self, jsonMsg):
        #print(jsonMsg)
        event = jsonMsg.get('event')

        #check if event is a message
        if not event.get('type') == 'message':
            return
        
        #ignore events from the bot
        if event.get('username') == self._username:
            return
        
        #check if message is an IM
        if not event.get('channel_type') == 'im':
            return

        channel = event.get('channel')

        #direct the message to the correct action
        messageBody = event.get('text').split(' ')
        if len(messageBody) < 1:
            return
        
        cmd = messageBody.pop(0).lower()
        if cmd == 'admin':
            if event.get('user') == ADMIN_USER:
                self.setAdminUserChatChannel(channel)
                self.parseAdminCmd(messageBody)
            else:
                self.sendMessage(self.getErrorRspNoAdminPrivileges(), channel)
            return
        if cmd == 'help':
            self.sendMessage(self.getHelpRsp(), channel)
            return
        if cmd == 'draw':
            if messageBody[0].lower() == 'card':
                '''
                card = self.drawCardFromDeck()
                returnMsg = self.getDrawCardPayload(card, event)
                self._webclient.chat_postMessage(**returnMsg)'''
                return
        else:
            self.sendMessage(self.getErrorRsp(), channel)
            return

    def parseAdminCmd(self, msgArgs):
        cmd = msgArgs.pop(0).lower()
        if cmd == 'help':
            self.sendMessageToAdmin(self.getHelpRsp(adminRqst=True))
            return
        elif cmd == 'startnewgame':
            if len(msgArgs) > 0:
                self.startNewGame(msgArgs[0])
                return
        elif cmd == 'addplayer':
            if len(msgArgs) > 0:
                self.AddPlayer(msgArgs)
                return
        else:
            self.sendMessageToAdmin(self.getErrorRsp())

    def startNewGame(self, gameName: str):
        result = self.createChannel(gameName)
        if result == self.successMsg():
            self._coupgame = CoupGame(gameName)
        self.sendMessageToAdmin(result)

    def checkIfChannelExists(self, channelName: str):
        response = {}
        try:
            response = self._webclient.conversations_list()
        except:
            print(sys.exc_info()[0])
            return {}
        else:
            channelList = response.get('channels')
            for channel in channelList:
                _name = channel.get('name')
                if _name == channelName:
                    return channel
            #if no channels have been found, return empty dict
            return {}
    
    def createChannel(self, channelName: str):
        chan = self.checkIfChannelExists(channelName)
        if (len(chan) > 0):
            return self.getChannelAlreadyExistsError()

        #create new channel with the game's name
        response = {}
        try:
            response = self._webclient.conversations_create(name=channelName)
        except:
            print(sys.exc_info()[0])
            return self.createChannelFailedError()
        else:
            self._gameChannelID = response.get("channel").get("id")
            return self.successMsg()
    
    def AddPlayer(self, playerNameArgs: list):
        #if game has not been created yet (channel name is blank), return
        if len(self._gameChannelID) < 1:
            self.sendMessageToAdmin(self.NoGameCreatedError())
            return

        #if player is already on the roster, return
        for playerName in self._playerRoster.values():
            if matchTextInArray(playerName, playerNameArgs):
                self.sendMessageToAdmin("Player is already in the game.")
                return

        #check if the user exists in the workspace
        playerID, playerNameFound = self.getUserIdFromWorkspace(playerNameArgs)
        if (len(playerID) < 1):
            self.sendMessageToAdmin(self.playerIDNotFoundError())
            return

        #add the user to the roster, invite the user to join the channel
        try:
            self._webclient.conversations_invite(channel=self._gameChannelID,users=playerID)
        except:
            print(sys.exc_info()[0])
            self.sendMessageToAdmin(self.unableToAddPlayerError())
            return
        else:
            self._playerRoster[playerID] = playerNameFound
            self._coupgame.AddPlayer(playerNameFound)
            self.sendMessageToAdmin(self.successMsg())
            return

    def getUserIdFromWorkspace(self, playerNameArgs: list):
        response = {}
        try:
            response = self._webclient.users_list()
        except:
            print(sys.exc_info()[0])
            return "",""
        else:
            members = response.get('members')
            for member in members:
                if matchTextInArray(member.get('name'), playerNameArgs):
                    return member.get('id'), member.get('name')
                if matchTextInArray(member.get('real_name'), playerNameArgs):
                    return member.get('id'), member.get('real_name')
            return "",""

    @staticmethod
    def successMsg():
        return "Success!"

    @staticmethod
    def playerIDNotFoundError():
        return "Player not found."

    @staticmethod
    def unableToAddPlayerError():
        return "Unable to add player."

    @staticmethod
    def NoGameCreatedError():
        return "No game has been created yet."

    @staticmethod
    def createChannelFailedError():
        return "Failed to create channel."

    @staticmethod
    def getChannelAlreadyExistsError():
        return "Channel already exists, try a different name."

    @staticmethod
    def getErrorRsp():
        return "Command not recognized, type \'help\' for a list of commands."

    @staticmethod
    def getErrorRspNoAdminPrivileges():
        return "Nice try, you don't have admin privileges..."

    @staticmethod
    def getHelpRsp(adminRqst = False):
        txt = "List of commands:\n"
        if adminRqst:
            txt += "startnewgame <channelName>\n"
            txt += "addplayer <player name (no quotes)>\n"
            txt += "undo\n"
            txt += "debug"
        else:
            txt += "draw card\n"
            txt += "replace card <card name>\n"
            txt += "status <playername>\n"
            txt += "status me\n"
            txt += "status all\n"
            txt += "take coin <number of coins, 1-3\n"
            txt += "steal two coins <player name>\n"
            txt += "return two coins <player name>\n"
            txt += "return coins <number of coins>"
        return txt

    def getDrawCardPayload(self, card):
        return "card"