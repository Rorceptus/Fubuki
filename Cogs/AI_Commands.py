#LIBRARIES--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
import re
import os
import json
import nextcord
from nextcord.ext import commands
from nextcord import Embed, slash_command, Interaction, SlashOption

#IMPORTING PLUGINS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
from Plugins.gemini_model import GeminiModel

#LOADING API FILE-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
api_path = os.path.join(os.path.dirname(__file__), "..", "Config", "API.json")           # API file path.

with open(api_path, 'r') as file:
    api_data = json.load(file)

# Loading google-gemini API.
Key = api_data['GEMINI']['Key']
gemini = GeminiModel(api_key = Key)

#FUNCTION TO CONVERT PLAIN URLs INTO MARKDOWN LINKS---------------------------------------------------------------------------------------------------------------------------------------------------|
def links(text):
    url_pattern = re.compile(r'(https?://[^\s]+)')
    return url_pattern.sub(r'<\1>', text)

#MAIN-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # (1) Gemini Command.
    @slash_command(
        name = 'gemini',
        description = 'Ask questions directly from google gemini.'
    )
    async def gemini(
        self,
        interaction: Interaction,
        question: str = SlashOption(
            name = "question",
            description = "How can I help you?",
            required = True
        )
    ):
        try:
            await interaction.response.defer()

            # Taking responses from Gemini AI.
            user_id = str(interaction.user.id)
            generated_content = gemini.generate_text(user_id, question)

            # Sending response.
            if generated_content:
                edited_content = links(generated_content)

                embed = Embed(
                    title = "__Gemini Response__",
                    description = edited_content,
                    color = nextcord.Color.dark_purple()
                )
                await interaction.followup.send(embed = embed)

            else:
                embed = Embed(
                    title = "__Error__",
                    description = "The AI could not generate a response. Try again later.",
                    color = nextcord.Color.red()
                )
                await interaction.followup.send(embed = embed, ephemeral = True)

        except Exception as e:
            print(f" ❌ Ask Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

#ADDING COG TO THE BOT--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
async def setup(bot):
    bot.add_cog(AICommands(bot))
