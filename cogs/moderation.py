import asyncio
from typing import Union
from nextcord import *
from nextcord.ext import *
from datetime import datetime
from nextcord.ext.commands import *
import aiosqlite
import time


authorised_channels = ["tests"]
now = datetime.now


class Moderation(Cog):
    def __init__(self, client:Bot):
        self.client = client
    
    @Cog.listener()
    async def on_ready(self):
        self.connect = await aiosqlite.connect("farm.db")
        self.cursor = await self.connect.cursor()


    
    @slash_command(name="kick")
    @has_permissions(kick_members=True)
    async def kick(self, interaction:Interaction, member: Member, *, reason="no reason given"):

        #embed code
        kick_embed = Embed(
            title=f"you have been kicked from {interaction.guild.name} ",
            description=f"reason : {reason}",
            colour=Colour.yellow(),
        )
        kick_embed.set_thumbnail(url=member.guild.icon)
        kick_embed.set_footer(
            text=f"kicked the{now().date()} at {now().strftime('%H:%M')}", 
            icon_url=self.client.user.avatar
        )
        if isinstance(interaction, Interaction):
            kick_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)

        #main code
        if interaction.channel.name in authorised_channels:

            await member.send(embed=kick_embed)
            await member.kick(reason=reason)
            await interaction.send(
                f" {member.name} has been kicked from the server by `{interaction.user.name}`"
            )


    @slash_command(name="ban")
    @has_permissions(ban_members=True)
    async def ban(self, interaction: Interaction, member: Member = SlashOption(name="member", description="the member to ban", required=True),*,reason="no reason given",):

        # embed code
        ban_embed = Embed(
            title=f"you have been banned from {interaction.guild.name} ",
            description=f"reason : {reason}",
            colour=0xCC3D3D,
        )

        ban_embed.set_thumbnail(url=member.guild.icon)

        ban_embed.set_footer(
            text=f"banned the {now().date()} at {now().strftime('%H:%M')}", 
            icon_url=self.client.user.avatar
        )

        if isinstance(interaction, Interaction):
            ban_embed.set_author(name=interaction.user.name, url=interaction.user.avatar)

        # ban code
        if interaction.channel.name in authorised_channels or reason=="multiple warnings":

            await member.send(embed=ban_embed)
            await member.ban(reason=reason)
            if isinstance(interaction, Interaction):
                await interaction.channel.send(
                    f" **{member.name}** has been banned from the server by **{interaction.user.name}**"
                )
            else:
                await interaction.channel.send(
                    f" **{member.name}** has been banned from the server by **{interaction.user.name}**"
                )

    
    @slash_command(name='unban', description='unbanning a user')
    async def unban(self, interaction:Interaction, *, member):
        
        #embed code
        unban_embed = Embed(
            title=f"Unbanned",
            description=f" {str(member).split('#')[0]} have been unbanned from **{interaction.guild.name}**",
            colour=Color.green(),
        )

        unban_embed.set_thumbnail(url=self.client.user.avatar)
        unban_embed.set_footer(
            text=f"unbanned by {self.client.user.name} {now().date()} at {now().strftime('%H:%M')} ",
            icon_url=self.client.user.avatar,
        )
        if isinstance(interaction, Interaction):
            unban_embed.set_author(name=interaction.user.name, url=interaction.user.avatar)

        #if youre able to send commands in this channel
        if interaction.channel.name in authorised_channels:

            #getting the banned users list to find the member
            banned_users = [entry async for entry in interaction.guild.bans()]
            member_name, member_discriminator = member.split("#")


            #searching for the member
            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name,member_discriminator,):
                    await interaction.guild.unban(user)
                    print(f"{member} unbanned")
                    await interaction.send(embed=unban_embed)
                    await user.send(embed=unban_embed)
                    return



    @slash_command(name="clear")
    async def clear(self, interaction:Interaction, channel: abc.GuildChannel = None, amount : int = None):
        to_clear = channel if channel else interaction.channel

        loading_clear=Embed(
            title=f"Clearing {to_clear.name}",
            colour=Color.yellow(),
            )
        loading_clear.set_author(name=self.client.user.name, url=self.client.user.avatar)

        cleared=Embed(
            title="Cleared!", 
            description=f" {to_clear.name} has been cleared!",
            colour=Color.green()
        )
        cleared.set_author(name=self.client.user.name, url=self.client.user.avatar)

        messages = []

        for chnl in ([channel, interaction.channel] if channel else [interaction.channel]):
            msg = await chnl.send(embed=loading_clear)
            if channel and chnl != channel: messages.append(msg)

        await to_clear.purge(limit=amount)


        for message in messages:
            await message.delete()

        messages = []

        for chnl in ([channel, interaction.channel] if channel else [interaction.channel]):
            messages.append(await chnl.send(embed=cleared))

        await asyncio.sleep(3)


        for message in messages:
            await message.delete()


    #--> on message command:
    @Cog.listener()
    async def on_message(self, message: Message):

        
        if not isinstance(message.channel,abc.GuildChannel):
            return

        #getting the channel name
        channel = message.channel.name
        #curse code
        if message.content == "curse":
            await message.delete()
            await self.warn(
                message,
                member=message.author,
                reason=f"cursing",
            )

        #commands code
        if message.content.startswith("!"):
            if channel not in authorised_channels:
                await message.delete()
                await message.channel.send("you cannot send messages on this channel")



def setup(client: Bot):
    client.add_cog(Moderation(client))
