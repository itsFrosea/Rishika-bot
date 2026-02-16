# Rishika Discord Bot

Rishika is a **voice-channel management Discord bot** focused on creating and controlling temporary voice channels with an interactive control panel.

It is designed to be lightweight, user-friendly, and safe for public Discord servers.

---

## ✨ Features

- Join-to-create voice channels
- Automatic temporary VC creation
- Interactive VC control panel (buttons + modals)
- Rename voice channels via popup modal
- Lock / unlock voice channels
- Change user limits dynamically
- Claim ownership of a VC
- Auto-delete empty voice channels
- Persistent control UI (no slash spam)

---

## 🎛 Voice Control Panel

Each temporary VC gets a control panel that allows the **owner** to:

- 🔒 Lock / 🔓 Unlock the VC  
- 👥 Increase or set user limits  
- ✏️ Rename the VC (modal input)  
- 👑 Claim ownership  
- 🗑️ Delete the VC  

Only the VC owner can use these controls.

---

## ⚙️ Configuration

Inside the cog:

```python
JOIN_TO_CREATE_NAME = "➕ Create VC"
TEMP_CATEGORY_NAME = "🎧 Voice Channels"
DEFAULT_USER_LIMIT = 0  # 0 = unlimited
```

- Users join the **Join to Create** channel
- Bot creates a personal VC under the temp category
- VC is deleted automatically when empty

---

## 🔐 Permissions Required

The bot requires the following permissions:

- View Channels
- Manage Channels
- Move Members
- Connect
- Speak
- Send Messages
- Embed Links
- Use External Emojis

❗ **Administrator permission is NOT required**

---

## 🛡 Security & Privacy

- No user messages are read or stored
- No personal data is logged
- No external APIs are used
- No credentials are collected
- Runs using Discord’s official API only

---

## 🧩 Tech Stack

- Python 3.11+
- discord.py
- Discord UI (Buttons & Modals)
- Cog-based architecture

---

## 🚀 Deployment

1. Clone the repository
2. Install dependencies
3. Add bot token to `.env`
4. Run the bot

---

## 📄 License

MIT License
