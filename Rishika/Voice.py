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

    embed.add_field(name="👑 Owner", value=owner.mention, inline=True)
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

# ───────────────── MODALS ─────────────────

class RenameVCModal(discord.ui.Modal, title="Rename Voice Channel"):
    new_name = discord.ui.TextInput(
        label="New channel name",
        placeholder="e.g. 🔊 Gaming VC",
        max_length=100
    )

    def __init__(self, vc_id: int):
        super().__init__()
        self.vc_id = vc_id

    async def on_submit(self, interaction: discord.Interaction):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            return await interaction.response.send_message(
                "❌ Voice channel not found", ephemeral=True
            )

        await vc.edit(name=self.new_name.value)
        await interaction.response.send_message(
            f"✏️ VC renamed to **{self.new_name.value}**", ephemeral=True
        )

class LimitVCModal(discord.ui.Modal, title="Set User Limit"):
    limit = discord.ui.TextInput(
        label="User limit (0 = unlimited)",
        placeholder="0",
        max_length=2
    )

    def __init__(self, vc_id: int):
        super().__init__()
        self.vc_id = vc_id

    async def on_submit(self, interaction: discord.Interaction):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            return await interaction.response.send_message(
                "❌ Voice channel not found", ephemeral=True
            )

        try:
            value = int(self.limit.value)
            if value < 0:
                raise ValueError
        except ValueError:
            return await interaction.response.send_message(
                "❌ Enter a valid number", ephemeral=True
            )

        await vc.edit(user_limit=value)
        await interaction.response.send_message(
            f"👥 User limit set to **{value or '∞'}**", ephemeral=True
        )

# ───────────────── VIEW ─────────────────

class VoiceControl(discord.ui.View):
    def __init__(self, vc_id: int):
        super().__init__(timeout=None)
        self.vc_id = vc_id

    async def interaction_check(self, interaction: discord.Interaction):
        data = TEMP_VC.get(self.vc_id)
        if not data or interaction.user.id != data["owner"]:
            await interaction.response.send_message(
                "❌ This control panel is not yours.", ephemeral=True
            )
            return False
        return True

    async def refresh(self, interaction: discord.Interaction):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            return

        owner = interaction.guild.get_member(TEMP_VC[self.vc_id]["owner"])
        msg_id = TEMP_VC[self.vc_id]["message"]
        msg = await interaction.channel.fetch_message(msg_id)

        await msg.edit(
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

    # ───── MODAL ACTIONS ─────

    @discord.ui.button(label="Rename", emoji="✏️", style=discord.ButtonStyle.primary, row=1)
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RenameVCModal(self.vc_id))

    @discord.ui.button(label="Set Limit", emoji="👥", style=discord.ButtonStyle.primary, row=1)
    async def set_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LimitVCModal(self.vc_id))

    # ───── OWNERSHIP ─────

    @discord.ui.button(label="Claim", emoji="👑", style=discord.ButtonStyle.secondary, row=2)
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

        if after.channel and after.channel.name == JOIN_TO_CREATE_NAME:
            category = discord.utils.get(guild.categories, name=TEMP_CATEGORY_NAME)
            if not category:
                category = await guild.create_category(TEMP_CATEGORY_NAME)

            base = f"🔊 {member.display_name}'s VC"
            vc = await guild.create_voice_channel(
                name=base,
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
