from discord import app_commands
from discord.ext import commands
import discord

JOIN_TO_CREATE_NAME = "➕ Create VC"
TEMP_CATEGORY_NAME = "🎧 Voice Channels"


class RishikaSetup(commands.Cog):
    def init(self, bot: commands.Bot):
        self.bot = bot

    async def ensure_setup(self, guild: discord.Guild):
        category = discord.utils.get(guild.categories, name=TEMP_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(TEMP_CATEGORY_NAME)

        join_vc = discord.utils.get(guild.voice_channels, name=JOIN_TO_CREATE_NAME)
        if not join_vc:
            await guild.create_voice_channel(
                name=JOIN_TO_CREATE_NAME,
                category=category
            )

        me = guild.me or guild.get_member(self.bot.user.id)
        if me:
            await category.set_permissions(
                me,
                connect=True,
                speak=True,
                view_channel=True
            )

    #  REGISTER DIRECTLY ON THE TREE
    @app_commands.command(
        name="setup",
        description="Create or repair Temp Voice setup"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.ensure_setup(interaction.guild)
        await interaction.followup.send(
            " Temp Voice setup is complete.",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    #  THIS LINE IS THE KEY
    await bot.add_cog(RishikaSetup(bot))