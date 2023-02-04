
import asyncio
from typing import Union
from nextcord import *
from nextcord.ext import *
from nextcord.ext import tasks
from nextcord.ext.commands import *
import aiosqlite
import time
import scrapetube

class Greetings(Cog):
    
    def __init__(self, client):
        self.client:Bot=client
        self.youtubeChannels = {
            "GothamChess": "https://www.youtube.com/@GothamChess",
            "You_ne5": "https://www.youtube.com/channel/UCMU3_AdA93SofARSIBBXuqg"
        }
        self.videoes = {}

    @Cog.listener()
    async def on_ready(self):
        self.check.start()


    @Cog.listener()
    async def on_member_join(self, member:Member):
        member_embed = Embed(
            title=f"Hello {member.name} !",
            description=f" **{member.name}** just joined the server!",
            colour=Colour.green(),
        )

        member_embed.set_thumbnail(url=member.avatar)
        member_embed.set_footer(text=f"Welcome")

        channel = utils.get(member.guild.channels, name="greetings")
        await channel.send(embed=member_embed)



    @Cog.listener()
    async def on_member_remove(self, member:Member):

        member_embed = Embed(
            title=f" {member.name} just left us :(",
            description=f"**why** {member.name} ",
            colour=Colour.red(),
        )

        member_embed.set_thumbnail(url=member.avatar)
        member_embed.set_footer(text=f"Traitor")

        channel = utils.get(member.guild.channels, name="greetings")
        await channel.send(embed=member_embed)
    
    @tasks.loop(seconds=10)
    async def check(self):
        channel = self.client.get_channel(1057071662836760706)

        for ychannel_name in self.youtubeChannels:
            videos = scrapetube.get_channel(channel_url = self.youtubeChannels[ychannel_name], limit=5)
            videoIds = [video['videoId'] for video in videos]
            

            if self.check.current_loop==0:
                self.videoes[ychannel_name]=videoIds
                continue

            for videoId in videoIds:
                if videoId not in self.videoes[ychannel_name]:
                    self.videoes[ychannel_name]=videoIds
                    vid_url = f"https://youtu.be/{videoId}"
                    await channel.send(f"{ychannel_name} has uploaded a new video!\n{vid_url}")







def setup(client: Bot):
    client.add_cog(Greetings(client))