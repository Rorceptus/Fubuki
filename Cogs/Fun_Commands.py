#LIBRARIES--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
import os
import re
import json
import random
import requests
import nextcord
import asyncpraw
from io import BytesIO
from nextcord.ext import commands
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
from nextcord import Embed, slash_command, Interaction, SlashOption

#LOADING API FILE-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
api_path = os.path.join(os.path.dirname(__file__), "..", "Config", "API.json")           # API file path.

with open(api_path, 'r') as file:
    api_data = json.load(file)

# Loading reddit API.
Client_ID = api_data['REDDIT']['Client Id']
Client_Secret = api_data['REDDIT']['Client Secret']
User_Agent = api_data['REDDIT']['User Agent']

# Loading joke API.
Joke_URL = api_data['Joke']

# Loading dog API.
Dog_URL = api_data['Dog']

# Loading cat API.
Cat_URL = api_data['Cat']

# Loading urban API.
Urban_URL = api_data['Urban']

# Loading wikipedia API.
Wiki_URL = api_data['Wikipedia']

#MAIN-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Reddit api instance.
        self.meme_cache = set()
        
        self.reddit = asyncpraw.Reddit(
            client_id = Client_ID,
            client_secret = Client_Secret,
            user_agent = User_Agent
        )

    # (1) Meme Command.
    @slash_command(
        name = 'meme',
        description = 'Tired? Have a meme.'
    )
    async def meme(
        self,
        interaction: Interaction,
        category: str = SlashOption(
            name = "category",
            description = "Choose your desired category.",
            choices = {
                "Hot": "hot",
                "New": "new",
                "Top": "top",
                "Rising": "rising"
            },
            required = False
        )
    ):
        try:
            await interaction.response.defer()

            # The subreddit from where to fetch memes.
            subreddit = await self.reddit.subreddit("memes")

            # Picking a random category if not mentioned.
            if not category:
                category = random.choice(["hot", "new", "top", "rising"])

            # Fetching memes if the category is mentioned.
            if category == "hot":
                memes = subreddit.hot(limit = 30)
            elif category == "new":
                memes = subreddit.new(limit = 30)
            elif category == "top":
                memes = subreddit.top(limit = 30)
            elif category == "rising":
                memes = subreddit.rising(limit = 30)

            # Clearing the meme cache if it reaches a certain amount of entries.
            if len(self.meme_cache) >= 500:
                self.meme_cache.clear()

            # Saving meme id to avoid showing it again and again.
            meme = None
            async for submission in memes:
                if submission.id not in self.meme_cache and not submission.stickied:
                    meme = submission
                    self.meme_cache.add(submission.id)
                    break
            
            # Sending meme.
            if meme is not None:
                embed = Embed(
                    title = meme.title,
                    url = f"https://www.reddit.com{meme.permalink}",
                    color = nextcord.Color.magenta()
                )
                embed.set_image(url = meme.url)
                embed.set_footer(text=f"Posted by u/{meme.author}")
                await interaction.followup.send(embed = embed)
            
            else:
                embed = Embed(
                    title = "__Command Error__",
                    description = "Couldn't find a new meme. Try again later.",
                    color = nextcord.Color.red()
                )
                await interaction.followup.send(embed = embed, ephemeral = True)

        except Exception as e:
            print(f" ❌ Meme Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)

    # (2) Avatar command.
    @slash_command(
        name = 'avatar',
        description = 'Display the avatar of a user.'
    )
    async def avatar(
        self,
        interaction: Interaction,
        user: nextcord.Member = SlashOption(
            name = "user",
            description = "The user whose avatar you want to see.",
            required = False
        )
    ):
        try:
            # If no user is mentioned, then show the command invoker's avatar.
            if not user:
                embed = Embed(
                title = f"__{interaction.user.name}'s Avatar__",
                color = nextcord.Color.magenta()
                )
                embed.set_image(url = interaction.user.avatar.url)
                await interaction.response.send_message(embed = embed)

            # If the user mentioned, then show avatar of the mentioned user.
            else:
                embed = Embed(
                    title = f"__{user.name}'s Avatar__",
                    color = nextcord.Color.magenta()
                )
                embed.set_image(url = user.avatar.url)
                await interaction.response.send_message(embed = embed)

        except Exception as e:
            print(f" ❌ Avatar Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

    # (3) Joke command.
    @slash_command(
        name = 'joke',
        description = 'Laugh with us. Have a joke.'
    )
    async def joke(
        self,
        interaction: Interaction,
        category: str = SlashOption(
            name = "category",
            description = "Choose your desired joke category.",
            choices = {
                "Programming": "programming",
                "Misc": "misc",
                "Dark": "dark",
                "Pun": "pun",
                "Spooky": "spooky",
                "Christmas": "christmas"
            },
            required = False
        )
    ):
        try:
            await interaction.response.defer()

            # Construct the URL for the API request.
            if category:
                url = f"{Joke_URL}{category}"

            else:
                url = f"{Joke_URL}Any"

            # Sending a GET request to the Joke API.
            response = requests.get(url)
            joke_data = response.json()

            # Check if the response contains a joke.
            if joke_data["error"]:
                embed = Embed(
                    title = "__Command Error__",
                    description = "Couldn't fetch a joke. Please try again later.",
                    color = nextcord.Color.red()
                )
                await interaction.followup.send(embed = embed, ephemeral = True)
                return

            # Send if it is a single or two-part joke.
            if joke_data["type"] == "single":
                joke = joke_data.get("joke")
                embed = Embed(
                    title = "__Here's a joke for you!__",
                    description = joke,
                    color = nextcord.Color.magenta()
                )
                embed.set_footer(text = "Note: This is just for fun. Don't take it seriously.")

            elif joke_data["type"] == "twopart":
                setup = joke_data.get("setup")
                delivery = joke_data.get("delivery")

                embed = Embed(
                    title = "__Here's a joke for you!__",
                    description = f"{setup}\n ||{delivery}||",
                    color = nextcord.Color.magenta()
                )
                embed.set_footer(text = "Note: This is just for fun. Don't take it seriously.")

            # Send the joke in an embed
            await interaction.followup.send(embed = embed)

        except Exception as e:
            print(f" ❌ Joke Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)

    # (4) Dog command.
    @slash_command(
        name = 'dog',
        description = 'Get a random dog picture.'
    )
    async def dog(self, interaction: Interaction):
        try:
            url = Dog_URL

            # Sending request to API.
            response = requests.get(url)
            dog_data = response.json()

            # Sending response.
            if dog_data["status"] == "success":
                embed = Embed(
                    title = "__Here's a dog picture for you!__",
                    color = nextcord.Color.magenta()
                )
                embed.set_image(url = dog_data["message"])
                await interaction.response.send_message(embed = embed)
                
            else:
                embed = Embed(
                    title = "__Command Error__",
                    description = "Couldn't fetch a dog picture. Please try again later.",
                    color = nextcord.Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)

        except Exception as e:
            print(f" ❌ Dog Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

    # (5) Cat command.
    @slash_command(
        name = 'cat',
        description = 'Get a random cat picture.'
    )
    async def cat(self, interaction: Interaction):
        try:
            url = Cat_URL

            # Sending request to API.
            response = requests.get(url)
            cat_data = response.json()

            # Sending response.
            if cat_data:
                embed = Embed(
                    title = "__Here's a cat picture for you!__",
                    color = nextcord.Color.magenta()
                )
                embed.set_image(url = cat_data[0]["url"])
                await interaction.response.send_message(embed = embed)
                
            else:
                embed = Embed(
                    title = "__Command Error__",
                    description = "Couldn't fetch a cat picture. Please try again later.",
                    color = nextcord.Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)

        except Exception as e:
            print(f" ❌ Cat Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

    # (6) Urban Command.
    @slash_command(
        name = 'urban',
        description = 'Get a definition from Urban Dictionary.'
    )
    async def urban(
        self,
        interaction: Interaction,
        term: str = SlashOption(
            name = "term",
            description = "The term you want to look up on Urban Dictionary.",
            required = True
        )
    ):
        try:
            await interaction.response.defer()

            # Constructing the URL for the API requests.
            url = f"{Urban_URL}{term}"

            # Sending request to API.
            response = requests.get(url)
            urban_data = response.json()

            # Checking if the response contains any definitions.
            if urban_data.get("list"):
                definition_data = urban_data["list"][0]
                word = definition_data.get("word")
                definition = definition_data.get("definition")
                example = definition_data.get("example")
                thumbs_up = definition_data.get("thumbs_up")
                thumbs_down = definition_data.get("thumbs_down")

                # Remove text within brackets using.
                cleaned_definition = re.sub(r'\[|\]', '', definition)
                cleaned_example = re.sub(r'\[|\]', '', example)

                # Sending response.
                embed = Embed(
                    title = f"__Definition of {word}__",
                    description = f'''
                    **Definition:** {cleaned_definition}

                    **Example:** {cleaned_example}
                    ''',
                    color = nextcord.Color.magenta()
                )
                embed.set_footer(text = f"👍 {thumbs_up} | 👎 {thumbs_down}")
                await interaction.followup.send(embed = embed)
            
            else:
                embed = Embed(
                    title = "__Command Error__",
                    description = f"Couldn't find a definition for '{term}'. Please try a different term.",
                    color = nextcord.Color.red()
                )
                await interaction.followup.send(embed = embed, ephemeral = True)

        except Exception as e:
            print(f" ❌ Urban Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)

    # (7) Wiki Command.
    @slash_command(
        name = 'wiki',
        description = 'Get more info from wikipedia on you favourite topic.'
    )
    async def wiki(
        self,
        interaction: Interaction,
        term: str = SlashOption(
            name = "term",
            description = "The term you want to look up on Wikipedia.",
            required = True
        )
    ):
        try:
            await interaction.response.defer()
            
            # Construct the URL for the API request.
            url = f"{api_data['Wikipedia']}{term}"

            # Sending request to API.
            response = requests.get(url)
            wiki_data = response.json()

            # Checking if the response contains any summary.
            if wiki_data.get("extract"):
                title = wiki_data.get("title")
                summary = wiki_data.get("extract")
                page_url = wiki_data.get("content_urls", {}).get("desktop", {}).get("page")

                if len(summary) > 300:
                    summary = summary[:300] + "..."

                # Sending response.
                embed = Embed(
                    title = f"__{title}__",
                    description = f"{summary}[Read more?]({page_url})",
                    url = page_url,
                    color = nextcord.Color.magenta()
                )
                await interaction.followup.send(embed = embed)

            else:
                embed = Embed(
                    title = "__Command Error__",
                    description = f"Couldn't find a Wikipedia page for '{term}'. Please try a different term.",
                    color = nextcord.Color.red()
                )
                await interaction.followup.send(embed = embed, ephemeral = True)

        except Exception as e:
            print(f" ❌ Wiki Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred. Please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)

    # (8) Flip Command.
    @slash_command(
        name = 'flip',
        description = 'Flip a coin to get head or tail.'
    )
    async def flip(self, interaction: Interaction):
        try:
            # Images path.
            images = os.path.join(os.path.dirname(__file__), "..", "Assets", "Commands", "Flip Command")

            # Selecting random image.
            options = ['Head.png', 'Tail.png']
            choice = random.choice(options)

            # Splitting the extension from the name.
            result, _ = os.path.splitext(choice)

            # Preparing to send the image in embed.
            image_path = os.path.join(images, choice)
            file = nextcord.File(image_path, filename = choice)

            # Sending result.
            embed = Embed(
                title = f'__You flipped: {result}!__',
                color = nextcord.Color.magenta()
            )
            embed.set_image(url = f'attachment://{choice}')
            await interaction.response.send_message(embed = embed, file = file)

        except Exception as e:
            print(f" ❌ Flip Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred. Please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)

    # (9) Dice Roll Command.
    @slash_command(
        name = 'roll',
        description = 'Roll a dice with a specified number of sides (default is 6).'
    )
    async def roll(
        self,
        interaction: Interaction,
        sides: int = SlashOption(
            name = "sides",
            description = "Number of sides you want on the dice.",
            default = 6,
            required = False
        )
    ):
        try:
            # Ensure the number of sides at least 1.
            if sides < 1:
                sides = 6

            # Roll the dice.
            result = random.randint(1, sides)

            # Sending the result.
            embed = Embed(
                title = "__🎲 Dice Rolled__",
                description = f'''
                **Sides:** {sides}
                **Result:** {result}
                ''',
                color = nextcord.Color.magenta()
            )
            await interaction.response.send_message(embed = embed)

        except Exception as e:
            print(f" ❌ Dice Roll Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred. Please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)

    # (10) Image Command.
    @slash_command(
        name = 'image',
        description = 'Apply different filters to profile photos.'
    )
    async def image(
        self,
        interaction: Interaction,
        user: nextcord.Member = SlashOption(
            name = "user",
            description = "Mention the user whose profile picture you want to apply a filter to.",
            required = True
        ),
        filter_type: str = SlashOption(
            name = "filter",
            description = "Choose the filter to apply.",
            choices = {
                "Blur": "BLUR",                                 # Blurs the image.
                "Brightness Down": "BRIGHTNESS_DOWN",           # Decreases the brightness.
                "Brightness Up": "BRIGHTNESS_UP",               # Increases the brightness.
                "Contour": "CONTOUR",                           # Highlights the edges with contours.
                "Detail": "DETAIL",                             # Enhances the detail of the image.
                "Edge Enhance": "EDGE_ENHANCE",                 # Enhances the edges in the image.
                "Edge Enhance More": "EDGE_ENHANCE_MORE",       # Applies a stronger edge enhancement.
                "Emboss": "EMBOSS",                             # Applies an embossing effect.
                "Find Edges": "FIND_EDGES",                     # Finds and highlights the edges in the image.
                "Grayscale": "GRAYSCALE",                       # Converts the image to grayscale.
                "Invert": "INVERT",                             # Inverts the colors of the image.
                "Max": "MAX_FILTER",                            # Replaces each pixel with the maximum value of the surrounding area.
                "Min": "MIN_FILTER",                            # Replaces each pixel with the minimum value of the surrounding area.
                "Mode": "MODE_FILTER",                          # Reduces noise by replacing each pixel with mode.
                "Rank": "RANK_FILTER",                          # Applies a rank filter to the image.
                "Sepia": "SEPIA",                               # Applies a sepia tone.
                "Sharpen": "SHARPEN",                           # Sharpens the image.
                "Smooth": "SMOOTH",                             # Smoothens the image.
                "Smooth More": "SMOOTH_MORE"                    # Applies a more intense smoothening effect.
            },
            required = True
        )
    ):
        try:
            await interaction.response.defer()

            # Dowloading user avatar
            avatar_url = user.avatar.url
            response = requests.get(avatar_url)
            img = Image.open(BytesIO(response.content))

            # Applying filter on the image.
            if filter_type == "BLUR":
                img = img.filter(ImageFilter.BLUR)

            elif filter_type == "CONTOUR":
                img = img.filter(ImageFilter.CONTOUR)

            elif filter_type == "DETAIL":
                img = img.filter(ImageFilter.DETAIL)

            elif filter_type == "EDGE_ENHANCE":
                img = img.filter(ImageFilter.EDGE_ENHANCE)

            elif filter_type == "EMBOSS":
                img = img.filter(ImageFilter.EMBOSS)

            elif filter_type == "FIND_EDGES":
                img = img.filter(ImageFilter.FIND_EDGES)

            elif filter_type == "GRAYSCALE":
                img = ImageOps.grayscale(img)

            elif filter_type == "SHARPEN":
                img = img.filter(ImageFilter.SHARPEN)

            elif filter_type == "SMOOTH":
                img = img.filter(ImageFilter.SMOOTH)

            elif filter_type == "SMOOTH_MORE":
                img = img.filter(ImageFilter.SMOOTH_MORE)

            elif filter_type == "EDGE_ENHANCE_MORE":
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

            elif filter_type == "MODE_FILTER":
                img = img.filter(ImageFilter.ModeFilter(size=3))

            elif filter_type == "MAX_FILTER":
                img = img.filter(ImageFilter.MaxFilter(size=3))

            elif filter_type == "MIN_FILTER":
                img = img.filter(ImageFilter.MinFilter(size=3))

            elif filter_type == "RANK_FILTER":
                img = img.filter(ImageFilter.RankFilter(size=3, rank=0))

            # Custom Filters.
            elif filter_type == "INVERT":
                img = ImageOps.invert(img.convert("RGB"))
                
            elif filter_type == "SEPIA":
                sepia_img = ImageOps.colorize(ImageOps.grayscale(img), "#704214", "#C0C090")
                img = sepia_img

            elif filter_type == "BRIGHTNESS_UP":
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.5)

            elif filter_type == "BRIGHTNESS_DOWN":
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(0.5)

            # Saving the image in Temp folder with a unique filename (user ID).
            image_folder = os.path.join(os.path.dirname(__file__), "..", "TempFiles", "Image")
            file_path = os.path.join(image_folder, f"{user.id}_avatar.png")
            img.save(file_path)

            # Sending edited image.
            embed = Embed(
                title = f"__Here's your image__",
                color = nextcord.Color.magenta()
            )
            embed.set_image(url = "attachment://avatar.png")
            await interaction.followup.send(embed = embed, file = nextcord.File(file_path, filename = "avatar.png"))

            # Deleting the image file after sending to save resources.
            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as e:
            print(f" ❌ Image Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred. Please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)

#ADDING COG TO THE BOT--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
async def setup(bot):
    bot.add_cog(FunCommands(bot))
