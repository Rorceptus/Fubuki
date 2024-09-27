#LIBRARIES--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
import nextcord
from datetime import datetime
from nextcord.ext import commands
from nextcord import Embed, slash_command, Interaction, SlashOption

#MAIN-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # (1) Clear Command.
    @slash_command(
        name = 'clear',
        description = 'Clears a specified number of messages from the channel. (Max 99)'
    )
    async def clear(
        self,
        interaction: Interaction,
        amount: int = SlashOption(
            name = "amount",
            description = "Number of messages to clear (max 99)",
            required = True
        )
    ):
        try:
            # Permission check.
            if not interaction.user.guild_permissions.manage_messages:
                embed = Embed(
                    title = "__Permission Denied__",
                    description = "You don't have permission to use this command.",
                    color = nextcord.Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            
            # Limiting the amount of messages to delete to 99.
            if amount > 99:
                embed = Embed(
                    title = "__Invalid Amount__",
                    description = "You can only delete up to 99 messages at a time.",
                    color = nextcord.Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            
            # Deleting the messages.
            delete = await interaction.channel.purge(limit = amount + 1)
            embed = Embed(
                title = "__Messages Deleted__",
                description = f'''
                Successfully deleted {len(delete) - 1} messages.
                **➧ Amount:** {len(delete) - 1}
                **➧ By:** {interaction.user.mention}
                ''',
                color = nextcord.Color.orange()
            )
            await interaction.response.send_message(embed = embed)

        except Exception as e:
            print(f" ❌ Clear Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

    # (2) Warn Command.
    @slash_command(
        name = 'warn',
        description = 'Warns a specified user.'
    )
    async def warn(
        self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name = "member",
            description = "Mention the user to warn",
            required = "True"
        ),
        reason: str = SlashOption(
            name = "reason",
            description = "The reason for the warning.",
            required = True
        )
    ):
        try:
            # Permission check.
            if not interaction.user.guild_permissions.manage_messages:
                embed = Embed(
                    title = "__Permission Denied__",
                    description = "You don't have permission to use this command.",
                    color = nextcord.Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return

            # DM message to the warned user.
            dm_msg = Embed(
                title = "__You Have Been Warned__",
                description = f'''
                **➧ Server: ** {interaction.guild.name}

                **➧ Reason:** {reason}

                **➧ Warned By:** {interaction.user.mention}

                *Note: You might get muted or even banned from the server. If you repeat what you did.*
                ''',
                color = nextcord.Color.red()
            )
            try:
                await member.send(embed = dm_msg)

                # Confirmation message.
                conf_msg = Embed(
                    title = "__Warning Sent__",
                    description = f"{member.mention} has been warned and notified via DM.",
                    color = nextcord.Color.green()
                )
                await interaction.response.send_message(embed = conf_msg, ephemeral = True)

            except nextcord.Forbidden:
                embed = Embed(
                    title = "__Dm Error__",
                    description = f"Could not send a DM to {member.mention}.",
                    color = nextcord.Color.red()
                )
                await interaction.followup.send(embed = embed, ephemeral = True)

        except Exception as e:
            print(f"❌ Warn Command Error: {e}")

            embed = Embed(
                title = "__Command Error__",
                description = "Oops. An error occurred, please try again later.",
                color = nextcord.Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

#ADDING COG TO THE BOT--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
async def setup(bot):
    bot.add_cog(AdminCommands(bot))
