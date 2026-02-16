import discord
from discord.ext import commands

# ───────────────── CONFIG ─────────────────

JOIN_TO_CREATE_NAME = "➕ Create VC"
TEMP_CATEGORY_NAME = "🎧 Voice Channels"

DEFAULT_USER_LIMIT = 0   # 0 = unlimited
SEND_INTERFACE_MESSAGE = True

# ───────────────── STATE ─────────────────
# vc_id -> {"owner": user_id, "message": message_id}
TEMP_VC = {}


# ───────────────── EMBED ─────────────────

def voice_embed(vc: discord.VoiceChannel, owner: discord.Member):
    locked = not vc.permissions_for(vc.guild.default_role).connect

    embed = discord.Embed(
        title="🎧 Voice Channel Control",
        description="Manage **your personal voice channel**",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="👑 Owner",
        value=owner.mention,
        inline=True
    )

    embed.add_field(
        name="👥 Members",
        value=f"{len(vc.members)} / {vc.user_limit or '∞'}",
        inline=True
    )

    embed.add_field(
        name="🔒 Status",
        value="Locked" if locked else "Unlocked",
        inline=True
    )

    embed.set_footer(text="Only the VC owner can use this panel")

    return embed


# ───────────────── UI VIEW ─────────────────

class VoiceControl(discord.ui.View):
    def __init__(self, vc_id: int):
        super().__init__(timeout=None)
        self.vc_id = vc_id

    async def interaction_check(self, interaction: discord.Interaction):
        data = TEMP_VC.get(self.vc_id)
        if not data or interaction.user.id != data["owner"]:
            await interaction.response.send_message(
                "❌ This control panel is not yours.",
                ephemeral=True
            )
            return False
        return True

    async def refresh(self, interaction: discord.Interaction):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            return

        owner = interaction.guild.get_member(TEMP_VC[self.vc_id]["owner"])
        message_id = TEMP_VC[self.vc_id]["message"]
        message = await interaction.channel.fetch_message(message_id)

        await message.edit(
            embed=voice_embed(vc, owner),
            view=VoiceControl(self.vc_id)
        )

    # ───── ACCESS ─────

    @discord.ui.button(label="Lock", emoji="🔒", style=discord.ButtonStyle.secondary, row=0)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        await vc.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("🔒 VC locked", ephemeral=True)
        await self.refresh(interaction)

    @discord.ui.button(label="Unlock", emoji="🔓", style=discord.ButtonStyle.success, row=0)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        await vc.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("🔓 VC unlocked", ephemeral=True)
        await self.refresh(interaction)

    # ───── LIMIT ─────

    @discord.ui.button(label="Limit +1", emoji="👥", style=discord.ButtonStyle.primary, row=1)
    async def limit_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        new_limit = (vc.user_limit or len(vc.members)) + 1
        await vc.edit(user_limit=new_limit)
        await interaction.response.send_message("👥 User limit increased", ephemeral=True)
        await self.refresh(interaction)

    # ───── OWNERSHIP ─────

    @discord.ui.button(label="Claim", emoji="👑", style=discord.ButtonStyle.secondary, row=1)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        TEMP_VC[self.vc_id]["owner"] = interaction.user.id
        await interaction.response.send_message("👑 You are now the owner", ephemeral=True)
        await self.refresh(interaction)

    # ───── DELETE ─────

    @discord.ui.button(label="Delete", emoji="🗑️", style=discord.ButtonStyle.danger, row=2)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        await vc.delete()
        TEMP_VC.pop(self.vc_id, None)


# ───────────────── COG ─────────────────

class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild

        # ───── JOIN TO CREATE ─────
        if after.channel and after.channel.name == JOIN_TO_CREATE_NAME:
            category = discord.utils.get(guild.categories, name=TEMP_CATEGORY_NAME)
            if not category:
                category = await guild.create_category(TEMP_CATEGORY_NAME)

            # ── USER'S VC NAME ──
            display = member.display_name
            if display.lower().endswith("s"):
                base_name = f"🔊 {display}' VC"
            else:
                base_name = f"🔊 {display}'s VC"

            channel_name = base_name
            existing = [vc.name for vc in category.voice_channels]
            count = 1
            while channel_name in existing:
                count += 1
                channel_name = f"{base_name} #{count}"

            vc = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                user_limit=DEFAULT_USER_LIMIT
            )

            await member.move_to(vc)

            TEMP_VC[vc.id] = {"owner": member.id, "message": None}

            if SEND_INTERFACE_MESSAGE:
                msg = await vc.send(
                    embed=voice_embed(vc, member),
                    view=VoiceControl(vc.id)
                )
                TEMP_VC[vc.id]["message"] = msg.id

        # ───── OWNER LEFT / CLEANUP ─────
        if before.channel and before.channel.id in TEMP_VC:
            data = TEMP_VC[before.channel.id]

            if member.id == data["owner"]:
                if before.channel.members:
                    data["owner"] = before.channel.members[0].id
                else:
                    await before.channel.delete()
                    TEMP_VC.pop(before.channel.id, None)


async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))
