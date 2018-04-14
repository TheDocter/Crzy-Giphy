"""
Programmer: TheCrzyDoctor
Description: This script enables you to use !giphy keywards that will show a giphy on the screen.
Date: 02/19/2017
Version: 2
"""

# ---------------------------------------
# Import Libraries
# ---------------------------------------

import clr
import os
import codecs
import json

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------------------
# [Required] Script Information
# ---------------------------------------
ScriptName = "Crzy Giphy"
Website = "https://www.twitch.tv/thecrzydoc"
Description = "!giphy keywords will pull a giphy from giphy.com and display it on the stream through the web sockets"
Creator = "TheCrzyDoctor"
Version = "1.2.0"

# ---------------------------------------
# Settings fiel setup
# ---------------------------------------

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")


class Settings:
    def __init__(self, settingsFile=None):
        if settingsFile is not None and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
        else:
            self.OnlyLive = False
            self.GiphyApi = ''
            self.Command = '!giphy'
            self.Usage = 'Stream Chat'
            self.Permission = 'Everyone'
            self.PermissionInfo = ''
            self.PermissionResp = '{0} -> only {1} and higher can use this command'
            self.GiphyCreatedMsg = 'Giphy was created. It will show shortly.'
            self.GiphyErrorMsg = '{0}, There was an issue with creating the giphy'
            self.GiphyCost = 5
            self.UseCD = True
            self.CoolDown = 5
            self.OnCoolDown = "{0} the command is still on cooldown for {1} seconds!"
            self.UserCoolDown = 10
            self.OnUserCoolDown = "{0} the command is still on user cooldown for {1} seconds!"
            self.CasterCD = True
            self.NoCurrency = "{0} -> You don't have any currency to create a giphy!"
            self.InfoResponse = 'To create a giphy use !giphy keyword keyword. At this time the giphy command only accepts' \
                                'two keyword.'

    def ReloadSettings(self, data):
        """ Reload settings file. """
        self.__dict__ = json.loads(data, encoding='utf-8-sig')

    def SaveSettings(self, settingsFile):
        """ Saves settings File """
        try:
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
                json.dump(self.__dict__, f, encoding='utf-8-sig')
            with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
        except ValueError:
            Parent.Log(ScriptName, "Failed to save settings to file.")


def ReloadSettings(jsonData):
    """ Reload Settings on Save """
    global CGSettings
    CGSettings.ReloadSettings(jsonData)


# ---------------------------------------
# 	[Required] Functions
# ---------------------------------------
def Init():
    """ Intialize Data (only called on load) """
    global CGSettings
    CGSettings = Settings(settingsFile)
    return


def Execute(data):
    """ Execute data and process the message """
    if data.IsChatMessage() and data.GetParam(0).lower() == CGSettings.Command.lower():

        # make sure the user has enough points
        if Parent.GetPoints(data.User) == 0:
            message = CGSettings.NoCurrency.format(data.UserName)
            SendResp(data, CGSettings.Usage, message)
            return

        # check to see if the user has permissions.
        if not haspermission(data):
            return

        if not CGSettings.OnlyLive or Parent.IsLive():
            # get the parameter
            if data.GetParamCount() > 3:
                # to many params send response
                SendResp(data, CGSettings.Usage, CGSettings.InfoResponse)
                return

            # Remove currency before executing the command.

            Parent.RemovePoints(data.User, CGSettings.GiphyCost)

            # lets start creating the gipy via api.
            giphy = Parent.GetRequest("http://api.giphy.com/v1/gifs/search?"
                                      "q=" + data.GetParam(1) + "+" + data.GetParam(2) + "&"
                                      "api_key=" + str(CGSettings.GiphyApi) + "&"
                                      "limit=1&rating=pg13", {})

            # Take response and correctly format it to json!
            # CAUSE GETREUEST IS SCREWEDUP AND RETURNS STRING INSTEAD OF PURE JSON DATA!!!!
            fixedbracket = giphy.replace('"{', '{')
            fixedendbracket = fixedbracket.replace('}"', '}')
            noslash = fixedendbracket.replace('\\"', '"')
            noslashes = noslash.replace('\\/', '/')

            # Load it to format correctly into json
            jsondata = json.loads(noslashes)

            gifydata = jsondata["response"]['data'][0]['images']['downsized_large']['url']

            if gifydata is None:
                # no image was found. But its okay we have something in place for this.
                message = CGSettings.GiphyErrorMsg.format(data.UserName)
                SendResp(data, CGSettings.Usage, message)
            # Send confirmation that gify was created.
            SendResp(data, CGSettings.Usage, CGSettings.GiphyCreatedMsg)
            # Lets remove currecny from the user.

            # send it to web socket
            Parent.BroadcastWsEvent('EVENT_GIFYCREATED', gifydata)

            # add user cooldown to the user
            addcooldown(data)

            return


def Tick():
    """Required tick function"""
    return


# ---------------------------------------
# 	[Optional] Usage functions
# ---------------------------------------

def SendResp(data, rUsage, sendMessage):
    """Sends message to Stream or discord chat depending on settings"""

    # Set a list with all possible usage options that would trigger Stream chat message
    l = ["Stream Chat", "Chat Both", "All", "Stream Both"]

    # check if message is from Stream, from chat and if chosen usage is in the list above
    if (data.IsFromTwitch() or data.IsFromYoutube()) and (rUsage in l) and not data.IsWhisper():
        # send Stream message
        Parent.SendStreamMessage(sendMessage)

    # Set a list with all possible usage options that would trigger Stream whisper
    l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]

    # check if message is from Stream, from whisper and if chosen usage is in the list above
    if (data.IsFromTwitch() or data.IsFromYoutube()) and data.IsWhisper() and (rUsage in l):
        # send Stream whisper
        Parent.SendStreamWhisper(data.User, sendMessage)

    # Set a list with all possible usage options that would trigger discord message
    l = ["Discord Chat", "Chat Both", "All", "Discord Both"]

    # check if message is from discord
    if data.IsFromDiscord() and not data.IsWhisper() and (rUsage in l):
        # send Discord message
        Parent.SendDiscordMessage(sendMessage)

    # Set a list with all possible usage options that would trigger discord DM
    l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]

    # check if message is from discord, from DM and if chosen usage is in the list above
    if data.IsFromDiscord() and data.IsWhisper() and (rUsage in l):
        # send Discord whisper
        Parent.SendDiscordDM(data.User, sendMessage)

    return


"""

Required custom fucntions needed for plugin.

"""
def openreadme():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return

def haspermission(data):
    """ CHecks to see if the user hs the correct permission.  Based on Castorr91's Gamble"""
    if not Parent.HasPermission(data.User, CGSettings.Permission, CGSettings.PermissionInfo):
        message = CGSettings.PermissionResp.format(data.UserName, CGSettings.Permission, CGSettings.PermissionInfo)
        return False
    return True

def is_on_cooldown(data):
    """ Checks to see if user is on cooldown. """
    # check if command is on cooldown
    cooldown = Parent.IsOnCooldown(ScriptName, CGSettings.Command)
    user_cool_down = Parent.IsOnUserCooldown(ScriptName, CGSettings.Command, data.User)
    caster = Parent.HasPermission(data.User, "Caster", "")

    if (cooldown or user_cool_down) and caster is False:

        if CGSettings.UseCD:
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, CGSettings.Command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, CGSettings.Command, data.User)

            if cooldownDuration > userCDD:
                m_CooldownRemaining = cooldownDuration

                message = CGSettings.OnCooldown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGSettings.Usage, message)

            else:
                m_CooldownRemaining = userCDD

                message = CGSettings.OnUserCooldown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGSettings.Usage, message)
        return True
    return False


def addcooldown(data):
    """Create Cooldowns Based on Castorr91's Gamble"""
    if Parent.HasPermission(data.User, "Caster", "") and CGSettings.CasterCD:
        Parent.AddCooldown(ScriptName, CGSettings.Command, CGSettings.Cooldown)
        return

    else:
        Parent.AddUserCooldown(ScriptName, CGSettings.Command, data.User, CGSettings.UserCoolDown)
        Parent.AddCooldown(ScriptName, CGSettings.Command, CGSettings.CoolDown)
