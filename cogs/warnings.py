import asyncio
from typing import Union
from nextcord import *
from nextcord.ext import *
from datetime import datetime
from nextcord.ext.commands import *
import aiosqlite
import time


now = datetime.now


class Warnings(Cog):
    def __init__(self, client):
        self.client = client
    
    @Cog.listener()
    async def on_ready(self):
        self.connect = await aiosqlite.connect("farm.db")
        self.cursor = await self.connect.cursor()

    @slash_command()
    @has_permissions(kick_members=True)
    async def warn(self, interaction:Interaction,member: Member=SlashOption(name="member", description="the member to warn", required=True), reason="No reason given",):
        

        #selecting the member warnings
        await self.cursor.execute(
            "SELECT * FROM warnings WHERE memberid = ? AND guild_id = ?",
            (
                member.id,
                interaction.guild.id,
            )
        )

        #getting the warning count
        warnings_fetchall = await self.cursor.fetchall()
        warning_count = len(warnings_fetchall)
        your_warning= "first" if warning_count+1==1 else "second" if warning_count+1==2 else "last" if warning_count+1==3 else "last"
    
        #creating the warn embed:
        warn_embed = Embed(
            title="Warning",
            description=f"""
            You have been warned in `{interaction.guild.name}` 
            reason: {reason}
            this is your **{your_warning}** warning
            
            """,
            color=0xD69533,
        )
        warn_embed.set_thumbnail(url=interaction.guild.icon)
        warn_embed.set_footer(icon_url=self.client.user.avatar, text=f' {now().date()} at {now().strftime("%H:%M")} ')
        if isinstance(interaction, Interaction):
            warn_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)


        #adding the new values to the database:
        await self.cursor.execute(
            "INSERT INTO warnings (memberid, guild_id, reason, datetime) VALUES(?,?,?,?)",
            (
                member.id,
                interaction.guild.id,
                reason,
                now(),
            ),
        )


        #sending the message
        await member.send(embed=warn_embed)

        #checking for the ban
        if warning_count >= 3:

            #deleting the data from the base after the member is banned:
            await self.cursor.execute(
                "DELETE FROM warnings WHERE memberid = ? AND guild_id = ?",
                (
                    member.id,
                    interaction.guild.id,
                )
            )

            #commiting
            await self.connect.commit()

            #calling the ban command:
            await self.client.get_cog("Moderation").ban(interaction, member=member, reason='multiple warnings')

        else:
            await self.connect.commit()


    @slash_command()
    @has_permissions(kick_members=True)
    async def warn_list(self, interaction:Interaction, member: Member=SlashOption(name="member", description="the member to get his list", required=True)):
        
        
        warnlist=Embed(
            title=f'Warning list',
            description=f"{member.mention}'s Warnings",
            colour=0x2e86a6
            )
    
        no_warn=Embed(
            title='this member has no warnings',
            description=f" **{member.mention}** has no warnings",
            color=Colour.red()
        )
        #editing the embeds
        warnlist.set_author(name=self.client.user.name, icon_url=self.client.user.avatar)
        warnlist.set_footer(text=f"requested by {interaction.user.name} ",icon_url=interaction.user.avatar)
        warnlist.set_thumbnail(url=member.avatar)
        #no warn
        no_warn.set_author(name=self.client.user.name, icon_url=self.client.user.avatar)
        no_warn.set_footer(text=f"requested by {interaction.user.name} ",icon_url=interaction.user.avatar)
        no_warn.set_thumbnail(url=f"https://i.imgur.com/ngl5Hdk.png")

        
        #getting the warnings
        await self.cursor.execute("SELECT * FROM warnings WHERE memberid=? AND guild_id=? ",(member.id, interaction.guild.id,))
        warnings = await self.cursor.fetchall()
        i=1

        #for every warning its going to output the informations
        for warning in warnings:
                id = warning[0]
                reason=warning[3]
                datetime=warning[4]
                warnlist.add_field(
                    name=f"warning: {i}",
                    value=f"""warned the {str(datetime.split()[0])} at {str(datetime.split()[1].split('.')[0])}
                    reason : {reason} 
                    id : {id}
                    """,
                    inline=False
                )
                i+=1

        #if the member has warnings it gives the warn list else the no warn embed
        if warnings:
            await interaction.send(embed=warnlist)
        else:
            await interaction.send(embed=no_warn)


    @slash_command()
    async def warn_remove(self, interaction: Interaction,member:Member=SlashOption(name="member", description="the member to get his list", required=True), warnid=SlashOption(name="warnid", description="the warn id", required=True)):

        #embed code

        await self.cursor.execute("""SELECT * From warnings WHERE guild_id=? AND id=?""",
                (
                    interaction.guild.id, 
                    warnid,
                ))

        fetchall=await self.cursor.fetchall()

        warndate=fetchall[0][4] if fetchall else None
        warned_member = utils.get(self.client.get_all_members(), id=fetchall[0][1]) if fetchall else None

    
        warn_remove=Embed(
            title="Warn removed!" if fetchall and member==warned_member else "Warn not found", 
            description=f"Warn removed successfully!" if fetchall and member==warned_member else "",
            color=Color.blue() if fetchall and member==warned_member else Color.red()
            )

        if fetchall and member==warned_member:
            warn_remove.set_author(name=interaction.user.name, icon_url=interaction.user.avatar) 
            warn_remove.set_footer(text=f"requested by {interaction.user.name} at {now().strftime('%H:%M')}") 
            warn_remove.add_field(name="member", value=member.mention, inline=False)
            warn_remove.add_field(name="warning date", value=str(warndate).split()[0], inline=True)
            warn_remove.add_field(name="warning time", value=str(warndate).split()[1].split(".")[0], inline=True)


        #database editing
        if member==warned_member:
            await self.cursor.execute(
                "Delete From warnings WHERE guild_id=? AND id=?",
                (interaction.guild.id,
                warnid,
                )
                )

        await interaction.send(embed=warn_remove)
        await self.connect.commit()
 


def setup(client: Bot):
    client.add_cog(Warnings(client))