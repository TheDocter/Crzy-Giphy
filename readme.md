# About
------
Crzy Gify is a way to have gif images to show up on the stream. This was a huge request from Goltrix2580, a twitch streamer
who switched to stream labs. As I wanted gif images to show up as well on my own stream I sat down and finally got it to work.
As of right now it only takes only 1 keyword. Further updates will allow more. The request does show up to 3 keywords, though
for the time being it only uses 1 keyword.

The gif image will fade out after 5 seconds. This is hard coded and will never have an option. So if you are sure about
editing files you are more than welcome to edit the client.js file.

# Setup
-------
1. Install Script via Stram Labs Chat bot.
2. Right click on the script name and click Insert API Keys in the menu that pops up. THIS IS REQUIRED!!!
3. Go to https://developers.giphy.com and create an app. You may need to register. ONce the app is created copy the api key
to the settings of the script. It is located under the Giphy Heading. Save the settings.
3. Add a new browser source. Set it to local file and browse to the Crzy Gif script file. Inside overlay is a index.html file.
Choose that file and save.
4. use the !giphy command like so. !giphy keywordhere keywordhere
5. Within a few seconds a message saying the giphy was created and it will show on your scene.


# WARNINGS
----------
As of right now there is a hard coded filter that limits it to only be pg rated.

# Support
----------
As I only use the Stream Labs Chat bot discord once in a while, usually when I go live or I have a question, The best place
to reach me is my personal discord server.

iblamedoc Discord Server: https://discord.gg/76QM7Zh

You can reach me there pretty much all day as I work from home. If you do run into issues with the script please feel free to
reach out to me and I'll update/fix what ever the issue was. If its just a feature request, I will most likely ignore these
inquires as this was specifically built and for Goltrix2580 needs with the knowledge it was going to be released to the public, as we
both could not find a gif script.

[Donations are always welcome. But not required](https://paypal.me/thecrzydoctor)

# Change Log
------------
Version 1.0.0
- Initial Release

Version 1.1.0
- Hard coded gif size to 500x500
- Centered gif in html page.
- Updated Rating to be PG
- Added in !giphy cost to remove points and also help limit the spamming of the command if cooldown is lower than default.