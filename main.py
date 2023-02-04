import os
import nextcord

from os import environ as env

from nextcord import Intents, Interaction
from nextcord.ext.commands import Bot, errors, Context
from nextcord.ext.application_checks import errors as application_errors

import aiosqlite


class Client(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop.create_task(self.get_ready())

    async def get_ready(self):
        self.db = await aiosqlite.connect("farm.db")
        self.load_extensions()

    def load_extensions(self) -> None:
        print("---------[Loading]---------")
        loaded = []
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.load_extension(f"cogs.{filename[:-3]}")
                print(f"[System]: {filename[:-3]} cog loaded.")
                loaded.append(filename[:-3])
        print("---------------------------")
        return loaded

    def unload_extensions(self) -> None:
        print("--------[Unloading]--------")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.unload_extension(f"cogs.{filename[:-3]}")
                print(f"[System]: {filename[:-3]} cog unloaded.")
        print("---------------------------")

    async def on_ready(self):

        print(f"slave's ready, logged in as {client.user.name} ")


        cursor = await self.db.cursor()

        await cursor.execute(
            """CREATE TABLE IF NOT EXISTS warnings(
                id integer NOT NULL UNIQUE,
                memberid integer NOT NULL, 
                guild_id integer NOT NULL, 
                reason string,
                datetime timespan,
                PRIMARY KEY("id" AUTOINCREMENT)
                )
                """
        )

    async def on_application_command_error(
        self, interaction: Interaction, error: Exception
    ) -> None:
        
        if isinstance(error, application_errors.ApplicationMissingRole):
            role = interaction.guild.get_role(int(error.missing_role))
            await interaction.send(
                f"Le role {role.mention} est requis pour utiliser cette commande.",
                ephemeral=True,
            )
            return

        elif isinstance(error, application_errors.ApplicationMissingPermissions):
            permissions = error.missing_permissions
            await interaction.send(
                f"L{'es' if len(permissions) > 1 else 'a'} permission{'s' if len(permissions) > 1 else ''}: **{', '.join(permissions)}**. {'sont' if len(permissions) > 1 else 'est'} requise{'s' if len(permissions) > 1 else ''} pour utiliser cette commande.",
                ephemeral=True,
            )
            return
        
        elif isinstance(error, application_errors.ApplicationMissingAnyRole):
            roles = error.missing_roles
            await interaction.send(
                f"Le{'s' if len(roles) > 1 else ''} role{'s' if len(roles) > 1 else ''}: **{', '.join([interaction.guild.get_role(role).mention for role in roles])}**. {'sont' if len(roles) > 1 else 'est'} requis pour utiliser cette commande.",
                ephemeral=True,
            )
            return

    

client = Client(
    "=", intents=Intents(messages=True, guilds=True, members=True, message_content=True, invites=True)
)

if __name__ == "__main__":
    client.run(env["TOKEN"])
