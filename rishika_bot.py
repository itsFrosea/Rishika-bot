import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────
# INTENTS
# ─────────────────────────────
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.message_content = False  # not needed

# ─────────────────────────────
# BOT INSTANCE
# ─────────────────────────────
rishika = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ─────────────────────────────
# SETUP HOOK (MATCHES SHARAN)
# ─────────────────────────────
@rishika.event
async def setup_hook():
    """
    Runs BEFORE on_ready.
    Loads cogs and syncs slash commands.
    """
    print("🔧 Rishika setup_hook starting...")

    # Load all cogs from rishika/ folder
    for filename in os.listdir("./rishika"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await rishika.load_extension(f"rishika.{filename[:-3]}")
                print(f"📦 Loaded rishika/{filename}")
            except Exception as e:
                print(f"❌ Failed to load rishika/{filename}: {e}")

    # 🔑 THIS IS THE KEY (same as Sharan)
    try:
        await rishika.tree.sync()
        print("🔁 Rishika slash commands synced")
    except Exception as e:
        print("❌ Slash command sync failed:", e)

# ─────────────────────────────
# READY EVENT
# ─────────────────────────────
@rishika.event
async def on_ready():
    print(
        f"🎧 Rishika is online as {rishika.user} "
        f"(ID: {rishika.user.id})"
    )

# ─────────────────────────────
# ASYNC STARTER (USED BY app.py)
# ─────────────────────────────
async def start_discord_async():
    """
    Start the Discord bot WITHOUT blocking FastAPI.
    """
    token = os.getenv("RISHIKA_TOKEN")

    if not token:
        raise RuntimeError("RISHIKA_TOKEN is not set")

    await rishika.start(token)