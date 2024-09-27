#LIBRARIES--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
import os
import json
import nextcord
from datetime import datetime
from nextcord.ext import commands
from nextcord import Embed, slash_command, Interaction, SlashOption

#MAIN-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # (1) Ping-Pong Command.
    @slash_command(
        name = 'ping',
        description = 'Check bot latency and round trip.'
    )
    async def ping(self, interaction: Interaction):
        try:
            start = datetime.now()
            await interaction.response.defer()
            end = datetime.now()

            latency = round(self.bot.latency * 1000)                               # In milliseconds.
            round_trip = round((end - start).total_seconds() * 1000)               # In milliseconds.

            embed = Embed(
                title = "__🏓 Pong!__",
                description = f'''
                **Latency:** {latency} ms
                **Round-Trip:** {round_trip} ms
                ''',
                color = nextcord.Color.dark_magenta()
            )
            await interaction.edit_original_message(embed = embed)

        except Exception as e:
            print(f" ❌ Ping Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

    # (2) About command.
    @slash_command(
        name = 'about',
        description = 'Know more about me and my creator.'
    )
    async def about(self, interaction: Interaction):
        try:
            # Embed image path.
            path = os.path.join(os.path.dirname(__file__), '..', 'Assets', 'Bot Profile', 'Banner.png')

            # About message content.
            about_message = f'''
            **Hello there!** 🌟

            I'm **Fubuki**, your friendly neighborhood bot designed to enhance your server experience. Here's a bit about me:

            ◉ **Main Role**: *I assist our awesome moderators to ensure smooth and efficient server management.*
            ◉ **Fun Commands**: *I come with a variety of commands to keep our server lively and engaging.*
            ◉ **Extra Features**: *Whether you're looking for a laugh, a cute cat picture, or just want to spice up the chat, I've got you covered!*

            **Created with care by Rorceptus** 🌟
        
            Feel free to reach out to my creator with any questions, suggestions, or just to say hi through the following links:

            ◉ **Discord**: [rorceptus](https://discord.com/users/1274596333298122755)
            ◉ **GitHub**: [Rorceptus](https://github.com/Rorceptus)
            '''

            embed = Embed(
                title = "__About Me__",
                description = about_message,
                color = nextcord.Color.dark_magenta()
            )
            embed.set_thumbnail(url = self.bot.user.avatar.url)
            embed.set_image(url = "attachment://Banner.png")

            with open(path, 'rb') as file:
                await interaction.response.send_message(embed = embed, file = nextcord.File(file, 'Banner.png'))

        except Exception as e:
            print(f" ❌ About Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

    # (3) Help command.
    @slash_command(
        name = 'help',
        description = 'Get information on all the available commands.'
    )
    async def help(
        self,
        interaction: Interaction,
        cmd: str = SlashOption(
            name = "cmd",
            description = "Pick the command you want to know about.",
            choices = {
                "About Command": "About",
                "Avatar Command": "Avatar",
                "Cat Command": "Cat",
                "Clear Command": "Clear",
                "Dice Roll Command": "Roll",
                "Dog Command": "Dog",
                "Flip Command": "Flip",
                "Gemini Command": "Gemini",
                "Help Command": "Help",
                "Image Command": "Image",
                "Joke Command": "Joke",
                "Meme Command": "Meme",
                "Ping Command": "Ping",
                "Roll Command": "Roll",
                "Urban Command": "Urban",
                "Warn Command": "Warn",
                "Wiki Command": "Wiki"
            },
            required = True
        )
    ):
        try:
            # Path for Commands_Info File.
            cmd_info_path = os.path.join(os.path.dirname(__file__), '..', 'Assets', 'Commands', 'Commands Info', 'Commands_Info.json')

            # Reading data from json file.
            with open(cmd_info_path, 'r') as file:
                commands_info = json.load(file)

            # Getting and sending info from json file.
            if cmd in commands_info:
                cmd_info = commands_info[cmd]
                
                embed = Embed(
                    title = "__Commands Help__",
                    description = f'''
                    **- Name:** ⠀⠀⠀⠀➥ {cmd_info['name']}
                    **- Usage:** ⠀⠀⠀⠀➥ {cmd_info['usage']}
                    **- Restrictions:** ⠀⠀⠀⠀➥ {cmd_info['restrictions']}
                    **- Description:** ⠀⠀⠀⠀➥ {cmd_info['description']}
                    ''',
                    color = nextcord.Color.dark_magenta()
                )
                await interaction.response.send_message(embed = embed)

            else:
                embed = Embed(
                    title = "__Command Error__",
                    description = f"{cmd} command doesn't exists. Make sure the command name is correct.",
                    color = nextcord.Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)

        except Exception as e:
            print(f" ❌ Help Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

#ADDING COG TO THE BOT--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
async def setup(bot):
    bot.add_cog(BasicCommands(bot))
