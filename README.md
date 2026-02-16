# 🤖 Rishika Bot

Rishika is a multipurpose Discord bot focused on **Twitch stream notifications**, **voice channel management**, and **community automation**.

Built and maintained by **Froséa**, Rishika is designed to be lightweight, reliable, and easy to configure for any Discord server.

---

## ✨ Features

### 🎮 Twitch Notifications
- Live stream alerts with rich embeds
- Game name, stream title, and live preview image
- Role pings (optional)
- Automatic **LIVE / OFFLINE** announcement channel renaming
- Discord status updates (e.g. *Streaming Valorant*)

### 🧠 Smart State Handling
- No repeated notifications
- Persistent live/offline tracking
- SQLite-based storage (server-safe)

### 🎧 Voice Channel System
- Join-to-create voice channels
- Owner-based VC control panel
- Lock / unlock / rename / limit users
- Automatic cleanup

---

## ⚙️ Commands

### 🔹 Twitch
```
/twitch add
/twitch list
```

**/twitch add**
- Twitch username
- Optional role to ping
- Announcement channel (LIVE / OFFLINE status)

**/twitch list**
- View all Twitch alerts configured in your server

> Requires **Manage Server** permission.

---

## 🔐 Permissions Required

- Manage Channels (for status channel renaming)
- Send Messages
- Embed Links
- Use Slash Commands
- Read Message History

---

## 🗄️ Data Usage

Rishika stores only what is necessary:
- Server ID
- Channel IDs
- Role IDs
- Twitch usernames & user IDs
- Stream state (live/offline)

❌ No messages, DMs, or personal user content are stored.

---

## 📜 Policies

- [Terms of Service](TERMS.md)
- [Privacy Policy](PRIVACY.md)

Rishika is **not affiliated with Discord or Twitch**.

---

## 🚀 Setup (Self-Hosting)

1. Clone the repository
2. Install dependencies
3. Configure environment variables
4. Run the bot

Required environment variables:
```
DISCORD_TOKEN
TWITCH_CLIENT_ID
TWITCH_CLIENT_SECRET
```

---

## 💬 Support

- Developer: **Froséa**
- Discord: *(add your support server link here)*
- GitHub: *(add repository link here)*

---

## ❤️ Credits

Built with:
- discord.py
- Twitch Helix API
- SQLite

Made with 💜 by Froséa
