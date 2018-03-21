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
Version = "1.1.0"

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
            self.MinCoolDown = 30
            self.MaxCoolDown = 60
            self.Permission = 'Everyone'
            self.PermissionInfo = ''
            self.PermissionResp = '{0} -> only {1} and higher can use this command'
            self.GiphyCreatedMsg = 'Giphy was created. It will show shortly.'
            self.GiphyErrorMsg = 'There was an issue with creating the giphy'
            self.GiphyCost = 5
            self.OnCoolDown = "{0} the command is still on cool down for {1} seconds!"
            self.UserCoolDown = 45
            self.OnUserCoolDown = "{0} the command is still on user cooldown for {1} seconds!"
            self.InfoResponse = 'To create a giphy use !giphy keyword. At this time the giphy command only accepts' \
                                'two keyword. Future versions will allow a full string of keywords.'

    def ReloadSettings(self, data):
        """ Reload settings file. """
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    def SaveSettings(self, settingsFile):
        """ Saves settings File """
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
        return


def ReloadSettings(jsonData):
    """ Reload Settings on Save """
    global CGSettings
    CGSettings.ReloadSettings(jsonData)
    return


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

        # set permission of the permision
        has_perm = Parent.HasPermission(data.User, CGSettings.Permission, CGSettings.PermissionInfo)
        with open('permission.txt', 'w') as outfile:
            outfile.write(str(has_perm))
        if not CGSettings.OnlyLive or Parent.IsLive() and has_perm:

            # check if command is on cooldown
            cooldown = Parent.IsOnCooldown(ScriptName, CGSettings.Command)
            user_cool_down = Parent.IsOnUserCooldown(ScriptName, CGSettings.Command, data.User)
            caster = Parent.HasPermission(data.User, "Caster", "")

            if (cooldown or user_cool_down) and caster is False:
                # send cooldown message
                cooldown_duration = Parent.GetCooldownDuration(ScriptName, CGSettings.Command)
                user_cooldown_duration = Parent.GetUserCooldownDuration(ScriptName, CGSettings.Command, data.User)

                if cooldown_duration > user_cooldown_duration:
                    # set remaining cooldown
                    m_cooldown_remaining = cooldown_duration

                    # send cooldown message
                    message = CGSettings.OnCoolDown.format(data.User, m_cooldown_remaining)
                    SendResp(data, CGSettings.Usage, message)
                    with open('cooldown.txt', 'w') as outfile:
                        outfile.write("On Global Cooldown.")
                else:
                    m_cooldown_remaining = user_cooldown_duration

                    # send usercooldown message
                    message = CGSettings.OnUserCoolDown.format(data.User, m_cooldown_remaining)
                    SendResp(data, CGSettings.Usage, message)
                    with open('cooldown.txt', 'w') as outfile:
                        outfile.write("On User CoolDown. Cooldown.")

                return
            # if not on cooldown start creating a giphy
            else:
                # get the parameter
                if data.GetParamCount() > 3:
                    # to many params send response
                    SendResp(data, CGSettings.Usage, CGSettings.InfoResponse)
                    return

                # Remove currency before executing the command.

                if Parent.GetPoints(data.User) >= CGSettings.GiphyCost:
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
                    if jsondata['status'] == '403':
                        SendResp(data, CGSettings.Usage, CGSettings.GiphyErrorMsg)
                        return

                    with open('data.txt', 'w') as outfile:
                        json.dump(jsondata["response"]['data'][0]['images']['downsized_large']['url'], outfile)

                    gifydata = jsondata["response"]['data'][0]['images']['downsized_large']['url']

                    # Send confirmation that gify was created.
                    SendResp(data, CGSettings.Usage, CGSettings.GiphyCreatedMsg)
                    # Lets remove currecny from the user.

                    # send it to web socket
                    Parent.BroadcastWsEvent('EVENT_GIFYCREATED', gifydata)
                    return
                else:
                    SendResp(data, CGSettings.Usage, "{0}, you do not have enough currency to use this command.".format(data.User))
        else:
            message = CGSettings.PermissionResp.format(data.User, CGSettings.Permission, CGSettings.PermissionInfo)
            SendResp(data, CGSettings.Usage, message)
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


def OpenReadMe():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return
