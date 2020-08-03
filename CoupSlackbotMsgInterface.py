import slack
from slack import WebClient
from CoupGame import CoupGame
import sys
from functionWrapper import functionWrapper

def matchTextInArray(textToFind: str, textList: list, separator = ' ', removeMatchedTextFromSearchList = False):
    ret = False
    for i in range(1, len(textList) + 1):
        joinedList = separator.join(textList[0:i])
        if joinedList == textToFind:
            ret = True
            if removeMatchedTextFromSearchList:
                newList = textList[i:]
                textList[:] = newList
            break
    return ret

ADMIN_USER = "U016EFT271A"

class CoupSlackBotMsgInterface:
    ''' ************* Error messages ************* '''
    SUCCESS_MSG = "Success!"
    ERR_PLAYER_ID_NOT_FOUND = "Player not found."
    ERR_UNABLE_TO_ADD_PLAYER = "Unable to add player."
    ERR_NO_GAME_CREATED = "No game has been created yet."
    ERR_CREATE_CHANNEL_FAILED = "Failed to create channel."
    ERR_CHANNEL_ALREADY_EXISTS = "Channel already exists, try a different name."
    ERR_COMMAND_NOT_RECOGNIZED = "Command not recognized, type \'help\' for a list of commands."
    ERR_NO_ADMIN_PRIVILEGES = "Nice try, you don't have admin privileges..."
    ERR_PLAYER_IS_ALREADY_IN_GAME = "Player is already in the game."

    def __init__(self, webclient):
        self._webclient = webclient
        self._gameChannelID = ""
        self._username = "coupslackbot"
        self.icon_emoji = ":robot_face:"
        self._playerRoster = {}
        self._channelIdMap = {}
        self._workspaceUsers = []
        self._ValidAdminCommands = {
            'help':         functionWrapper(0, self._adminInterfaceFn_sendInstructionListAdmin),
            'startnewgame': functionWrapper(1, self._adminInterfaceFn_startNewGame), #name of game as arg
            'addplayer':    functionWrapper(1, self._adminInterfaceFn_AddPlayer)         #name of user as arg
        }
        self._ValidCommands = {
            'help':                     functionWrapper(0, self._interfaceFn_sendInsructionList),
            'draw card':                functionWrapper(0, self._interfaceFn_userDrawCard),
            'replace card':             functionWrapper(1, self._interfaceFn_userReplaceCard, "Please specify card."),   #card name as arg
            'status':                   functionWrapper(1, self._interfaceFn_sendStatusMsg, "Please specify player name, or type \'status me\' or \'status all\'."),   #player name as arg
            'status me':                functionWrapper(0, self._interfaceFn_sendStatusMeMsg),
            'status all':               functionWrapper(0, self._interfaceFn_sendStatusAllMsg),
            'take coins':               functionWrapper(1, self._interfaceFn_userTakeCoins, "Please specify how many coins."),   #number of coins as arg
            'steal two coins from':     functionWrapper(1, self._interfaceFn_userStealCoinsFrom, "Please specify player name."), #player name as arg
            'return two coins to':      functionWrapper(1, self._interfaceFn_userReturnCoinsTo, "Please specify player name."),  #playe name as arg
            'return coins':             functionWrapper(1, self._interfaceFn_userReturnCoinsToBank, "Please specify how many coins."),   #number of coins as arg
            'join game':                functionWrapper(0, self._interfaceFn_joinGame)
        }

    ''' ************* Loading functions ************* '''
    def _loadUserIdsFromWorkspace(self):
        if len(self._workspaceUsers) > 0:
            return
        
        response = {}
        try:
            response = self._webclient.users_list()
        except:
            print(sys.exc_info()[0])
        else:
            self._workspaceUsers = response.get('members')
            #todo: remove users with "deleted" = True and "is_bot" = True

    ''' ************* User ID and Channel ID mapping functions ************* '''
    def _getUserIdFromDisplayName(self, playerNameArgs: list):
        for user in self._workspaceUsers:
            if matchTextInArray(user.get('profile').get('display_name'), playerNameArgs):
                return user.get('id')
        return ""

    def _getDisplayNameFromUserId(self, userId: str):
        for user in self._workspaceUsers:
            if user.get('id') == userId:
                return user.get('profile').get('display_name')
        return ""

    def _getChannelIDFromUserId(self, userId: str):
        for user in self._channelIdMap.keys():
            if user == userId:
                return self._channelIdMap[user]
        return ""
    
    def _addChannelToMap(self, userId: str, channelId: str):
        if not userId in self._channelIdMap.keys():
            self._channelIdMap[userId] = channelId

    ''' ************* Messaging functions ************* '''
    def _sendMessageToAdmin(self, text):
        self._sendMessageToUser(text, ADMIN_USER)

    def _sendMessageToUser(self, text, userId):
        self._loadUserIdsFromWorkspace()
        channelId = self._getChannelIDFromUserId(userId)
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
    
    def _postGeneralMessage(self, text):
        if len(self._gameChannelID < 1):
            return
        payload = {
            "channel": self._gameChannelID,
            "username": self._username,
            "icon_emoji": self.icon_emoji,
            "text": text
        }
        self._webclient.chat_postMessage(**payload)

    ''' ************* 'Public' functions ************* '''
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

        #direct the message to the correct action
        userId = event.get('user')
        self._addChannelToMap(userId, event.get('channel'))
        messageBody = event.get('text').split(' ')
        if len(messageBody) < 1:
            return
        
        if 'admin' in messageBody:
            messageBody.remove('admin')
            if userId == ADMIN_USER:
                commandFound = False
                for key in self._ValidAdminCommands.keys():
                    if matchTextInArray(key, messageBody, removeMatchedTextFromSearchList=True):
                        errorMsg = self._ValidAdminCommands[key].execute(messageBody, userId)
                        if len(errorMsg > 0):
                            self._sendMessageToAdmin(errorMsg)
                        commandFound = True
                        break
                if not commandFound:
                    self._sendMessageToAdmin(self.ERR_COMMAND_NOT_RECOGNIZED)
            else:
                self._sendMessageToUser(self.ERR_NO_ADMIN_PRIVILEGES, userId)
            return
        else:
            commandFound = False
            for key in self._ValidCommands.keys():
                if matchTextInArray(key, messageBody, removeMatchedTextFromSearchList=True):
                    errMsg = self._ValidCommands[key].execute(messageBody, userId)
                    if len(errMsg) > 0:
                        self._sendMessageToUser(errMsg, userId)
                    commandFound = True
                    break
            if not commandFound:
                    self._sendMessageToUser(self.ERR_COMMAND_NOT_RECOGNIZED, userId)

    ''' ************* Admin interface functions ************* '''
    def _adminInterfaceFn_startNewGame(self, gameNameArgs: list, userId: str):
        if not userId == ADMIN_USER:
            return

        #turn list argument into string
        gameNameStr = ' '.join(gameNameArgs)

        #create channel and initialize new game
        result = self._createChannel(gameNameStr)
        if result == self.SUCCESS_MSG:
            self._coupgame = CoupGame(gameNameStr)
        self._sendMessageToAdmin(result)

    def _adminInterfaceFn_AddPlayer(self, playerNameArgs: list, userId: str):
        if not userId == ADMIN_USER:
            return
            
        #if game has not been created yet (channel name is blank), return
        if len(self._gameChannelID) < 1:
            self._sendMessageToAdmin(self.ERR_NO_GAME_CREATED)
            return

        #if player is already on the roster, return
        for playerName in self._playerRoster.values():
            if matchTextInArray(playerName, playerNameArgs):
                self._sendMessageToAdmin(ERR_PLAYER_IS_ALREADY_IN_GAME)
                return

        #check if the user exists in the workspace
        playerID = self._getUserIdFromDisplayName(playerNameArgs)
        if (len(playerID) < 1):
            self._sendMessageToAdmin(self.ERR_PLAYER_ID_NOT_FOUND)
            return

        #add the user to the roster, invite the user to join the channel
        playerDisplayName = self._getDisplayNameFromUserId(playerID)
        try:
            self._webclient.conversations_invite(channel=self._gameChannelID,users=playerID)
        except:
            print(sys.exc_info()[0])
            self._sendMessageToAdmin(self.ERR_UNABLE_TO_ADD_PLAYER)
            return
        else:
            self._playerRoster[playerID] = playerDisplayName
            self._coupgame.AddPlayer(playerDisplayName)
            self._sendMessageToAdmin(self.SUCCESS_MSG)
            return

    def _adminInterfaceFn_sendInstructionListAdmin(self, dummyArgs: list):
        if not userId == ADMIN_USER:
            return
            
        txt = "List of commands:\n"
        txt += "startnewgame <channelName>\n"
        txt += "addplayer <player name (no quotes)>\n"
        txt += "undo\n"
        txt += "debug"
        self._sendMessageToAdmin(txt)

    ''' ************* Normal interface functions ************* '''
    def _interfaceFn_sendInsructionList(self, dummyArgs: list, userId: str):
        txt = "List of commands:\n"
        txt += "\t-draw card\n"
        txt += "\t-replace card <card name>\n"
        txt += "\t-status <playername>\n"
        txt += "\t-status me\n"
        txt += "\t-status all\n"
        txt += "\t-take coins <number of coins (1 to 3)\n"
        txt += "\t-steal two coins <player name>\n"
        txt += "\t-return two coins to <player name>\n"
        txt += "\t-return coins <number of coins>"
        self._sendMessageToUser(txt, userId)

    def _interfaceFn_userDrawCard(self, dummyArgs: list, userId: str):
        return #todo

    def _interfaceFn_userReplaceCard(self, cardNameArgList: list, userId: str):
        return #todo

    def _interfaceFn_sendStatusMsg(self, playerNameArgList: list, userId: str):
        return #todo

    def _interfaceFn_sendStatusMeMsg(self, dummyArgs: list, userId: str):
        return #todo

    def _interfaceFn_sendStatusAllMsg(self, dummyArgs: list, userId: str):
        return #todo

    def _interfaceFn_userTakeCoins(self, numCoinsArgList: list, userId: str):
        return #todo

    def _interfaceFn_userStealCoinsFrom(self, playerNameArgList: list, userId: str):
        return #todo

    def _interfaceFn_userReturnCoinsTo(self, playerNameArgList: list, userId: str):
        return #todo

    def _interfaceFn_userReturnCoinsToBank(self, numCoinsArgList: list, userId: str):
        return #todo

    def _interfaceFn_joinGame(self, dummyArgs: list, userId: str):
        return #todo

    ''' ************* New game/new channel creation ************* '''
    def _createChannel(self, channelName: str):
        chan = self._checkIfChannelExists(channelName)
        if (len(chan) > 0):
            return self.ERR_CHANNEL_ALREADY_EXISTS

        #create new channel with the game's name
        response = {}
        try:
            response = self._webclient.conversations_create(name=channelName)
        except:
            print(sys.exc_info()[0])
            return self.ERR_CREATE_CHANNEL_FAILED
        else:
            self._gameChannelID = response.get("channel").get("id")
            return self.SUCCESS_MSG

    def _checkIfChannelExists(self, channelName: str):
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