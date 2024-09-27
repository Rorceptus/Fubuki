#LIBRARIES--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
import os
import json
import random
import asyncio
import requests
import nextcord
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image, ImageDraw
from nextcord.ext import commands

#IMPORTING BOT UTILITIES------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
from Utilities.Database import Database

#LOADING BOT TOKEN------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
env_path = os.path.join(os.path.dirname(__file__), "Config", ".env")                     # .env path.

load_dotenv(dotenv_path = env_path)
Token = os.getenv("BOT_TOKEN")

#LOADING CONFIG FILE----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
config_path = os.path.join(os.path.dirname(__file__), "Config", "Config.json")           # Config file path.

try:
    with open(config_path, 'r') as file:
        config_data = json.load(file)

    # Loading bot profile.
    try:
        Name = config_data['PROFILE']['Name']
        Prefix = config_data['PROFILE']['Prefix']

    except KeyError as e:
        raise KeyError(f"Missing key in Profile section: {e}")

    # Loading channels. Channel Id's must be in integer form all the time.
    try:
        Welcome_Channel = int(config_data['CHANNELS']['Welcome Channel'])

    except KeyError as e:
        raise KeyError(f"Missing key in Channel section: {e}")
    except ValueError:
        raise ValueError("Invalid value in Channel section; expected an integer.")

    # Loading roles. Role Id's must be in integer form all the time.
    try:
        Guest_Role = int(config_data['ROLES']['Guest Role'])

    except KeyError as e:
        raise KeyError(f"Missing key in Roles section: {e}")
    except ValueError:
        raise ValueError("Invalid value in Roles section; expected an integer.")

    # Loading database credentials.
    try:
        print('║' + '═'*100 + '✘')
        db = Database(
            host = config_data['DATABASE']['Host'],
            user = config_data['DATABASE']['User'],
            password = config_data['DATABASE']['Password'],
            database_name = config_data['DATABASE']['Name']
        )

    except KeyError as e:
        raise KeyError(f"Missing key in Database section: {e}")
    
except FileNotFoundError:
    print(f"Error: Config file not found at the path {config_path}. Please ensure it exists.")
except json.JSONDecodeError:
    print("Error: Config file is not a valid JSON file. Please check its contents.")
except KeyError as e:
    print(f"Error: {e}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


#DEFINING INTENTS-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
intents = nextcord.Intents.default()

intents.members = True
intents.presences = True
intents.message_content = True

client = commands.Bot(command_prefix = Prefix, intents = intents, help_command = None)

#LOADING COG FILES------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
cog_path = os.path.join(os.path.dirname(__file__), "Cogs")                     # Path to the cogs folder.

def load_cog():
    for filename in os.listdir(cog_path):
        if filename.endswith('.py'):
            try:
                client.load_extension(f'Cogs.{filename[:-3]}')
                print(f" ✅ Loaded Cog: {filename[:-3]}")

            except Exception as e:
                print(f" ❌ Failed To Load Cog: {filename[:-3]}. Error: {e}")

#MAIN-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
# (1) Application Info.
@client.event
async def on_ready():
    # Changing bot's presence.
    await client.change_presence(activity = nextcord.Game(name = "Watching Over You👀"))

    # Bot's Info.
    print('║' + '═'*100 + '✘')
    print(' The bot has successfully joined the server.')
    print(' ' + '-'*50)
    print(f' Name: {Name}')
    print(f' Prefix: {Prefix}')
    print(f' Bot ID: {client.user.id}')
    print(' ' + '-'*50)

    # Fetching guild info.
    for guild in client.guilds:
        print(f' Guild Name: {guild.name}')
        print(f' Guild ID: {guild.id}')

    print('║' + '═'*100 + '✘')


# (2) Welcome Messages.
def generate_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

@client.event
async def on_member_join(member):
    temp_path = os.path.join(os.path.dirname(__file__), "TempFiles", "Welcome")
    temp_image_path = os.path.join(temp_path, f"temp_welcome_image_{member.id}.png")
    
    try:
        # Assigning guest role.
        role = member.guild.get_role(Guest_Role)

        if role:
            await member.add_roles(role)
        
        else:
            raise ValueError(f" ❌ Role ID {Guest_Role} not found.")
        
        # Welcome message content.
        welcome_message = f'''
        Welcome to the server, {member.mention}! 🎉
        We're so happy to have you here! To get started, please take a moment to complete a few quick steps:

        ➤ Head over to the **#verification** channel to verify yourself.\n
        ➤ Once verified, please read through the **#rules** channel to ensure a smooth and enjoyable experience for everyone.\n
        ➤ After that, feel free to say hi and introduce yourself in the **#introduction** channel. We're excited to meet you!\n

        *If you have any question or need help, don't hesitate to ask. Enjoy your stay!* 🌟
        '''
        
        # Fetching the welcome channel.
        channel = client.get_channel(Welcome_Channel)

        if channel is None:
            raise ValueError(f" ❌ Channel ID {Welcome_Channel} not found.")
        
        # Loading all image files from the "Welcome" directory.
        img_path = os.path.join(os.path.dirname(__file__), "Assets", "Welcome")
        img_files = [f for f in os.listdir(img_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

        if not img_files:
            raise FileNotFoundError(" ❌ No images found in the 'Welcome' folder.")
        
        selected_image = random.choice(img_files)
        welcome_image_path = os.path.join(img_path, selected_image)

        # Fetch and process user's profile photo.
        response = requests.get(member.avatar.url)
        user_avatar = Image.open(BytesIO(response.content)).convert("RGBA")

        # Crop the avatar to a circle
        avatar_size = 700
        mask = Image.new('L', (avatar_size, avatar_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, avatar_size, avatar_size), fill = 255)

        user_avatar = user_avatar.resize((avatar_size, avatar_size))
        user_avatar.putalpha(mask)

        # Generate a random solid color.
        frame_color = generate_random_color()
        
        # Create a solid color circle slightly larger than the profile photo.
        frame_size = (avatar_size + 40, avatar_size + 40)
        frame_circle = Image.new('RGBA', frame_size, frame_color)
        
        # Create a circular mask for the frame circle.
        mask = Image.new('L', frame_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, frame_size[0], frame_size[1]), fill = 255)
        frame_circle.putalpha(mask)

        # Position to center the profile picture on the frame circle.
        frame_position = (0, 0)
        user_avatar_position = (20, 20)

        # Create a final image with the frame circle and profile photo.
        final_image = Image.new('RGBA', frame_size, (0, 0, 0, 0))
        final_image.paste(frame_circle, frame_position, frame_circle)
        final_image.paste(user_avatar, user_avatar_position, user_avatar)

        # Open and modify the welcome image.
        welcome_image = Image.open(welcome_image_path)

        # Calculate position to center the final image on the welcome image.
        x = (welcome_image.width - final_image.width) // 2
        y = (welcome_image.height - final_image.height) // 2

        # Paste the final image onto the welcome image.
        welcome_image.paste(final_image, (x, y), final_image)

        # Ensure temp_path directory exists.
        os.makedirs(temp_path, exist_ok = True)

        # Save and send the new image.
        welcome_image.save(temp_image_path)
        
        files = nextcord.File(temp_image_path, filename = "welcome_image.png")

        embed = nextcord.Embed(
            title = "🎉 Welcome! 🎉",
            description = welcome_message,
            color = nextcord.Color.dark_theme()
        )
        embed.set_image(url = "attachment://welcome_image.png")
        await channel.send(embed = embed, file = files)

        # Insert member data into the database.
        join_time = member.joined_at.strftime("%H:%M:%S")
        join_date = member.joined_at.strftime("%Y-%m-%d")
        db.insert_member(member.name, str(member.id), join_time, join_date)

    except Exception as e:
        print(f" ❌ An error occurred: {e}")

    finally:
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

#RUNNING THE BOT--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
async def main():
    print('║' + '═'*100 + '✘')
    load_cog()                                             # Loading cog files.
    await client.start(Token)                              # Starting the bot with secret token.

if __name__ == "__main__":
    asyncio.run(main())                                    # Entry point to start the bot using an asynchronous event loop.
