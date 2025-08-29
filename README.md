# Discord ModMail Bot - Advanced Ticket System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Discord.py](https://img.shields.io/badge/discord.py-2.3.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🔥 Features

- **Automatic Ticket Creation**: When users DM the bot, it automatically creates a private staff-only channel
- **Two-Way Communication**: All messages are forwarded between users and staff seamlessly
- **DM-Based System**: Users communicate entirely through DMs - no need to join your server!
- **Secure Staff Channels**: Ticket channels are private and only accessible to staff members
- **Professional Closure Notifications**: Users receive embeds showing which staff member closed their ticket
- **Ticket History**: Complete message history tracking for every ticket
- **Easy Closure**: Simple `/close` command to resolve tickets
- **File Attachment Support**: Handles images and files in both directions
- **Professional Embeds**: Beautiful, organized message formatting

## 🚀 How It Works

1. **User DMs the bot** with their question or issue
2. **Bot automatically creates** a private ticket channel for staff
3. **Staff respond** in the ticket channel, and the bot forwards messages to the user via DM
4. **User responds** through DMs, and messages appear in the ticket channel
5. **Staff close tickets** with `/close` when resolved
6. **User receives professional notification** showing which staff member closed their ticket

## 📋 Commands

- `/close [channel]` - Close a ticket (staff only)
- `/help` - Show help information about the bot

## 🛠️ Setup

### 1. Create a Discord Application
- Go to [Discord Developer Portal](https://discord.com/developers/applications)
- Create a New Application
- Navigate to the "Bot" section
- Create a bot and copy the token

### 2. Configure the Bot
```python
# Get these values from your Discord server
GUILD_ID = 123456789  # Your server ID
STAFF_ROLE_ID = 123456789  # Staff role ID
CATEGORY_ID = 123456789  # (Optional) Ticket category ID
