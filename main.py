import discord
from discord.ext import commands
import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = 1404779830456133243 # Replace with your server ID
STAFF_ROLE_ID = 14047893693734524 # Replace with your staff role ID
CATEGORY_ID = 1410714293347024324 # Replace with your category ID (optional)

active_tickets = {}
ticket_history = {}

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="DMs | Made by Lev (@_yw2)"
        )
    )
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

@bot.tree.command(name="help", description="Learn how to use the ModMail bot")
async def help_command(interaction: discord.Interaction):
    help_embed = discord.Embed(
        title="ModMail Bot Help",
        description="A sophisticated ticket system that allows users to contact staff via DMs",
        color=discord.Color.blue()
    )
    
    help_embed.add_field(
        name="For Users",
        value="• Simply DM the bot to create a ticket\n• All your messages will be forwarded to staff\n• Staff responses will come to your DMs\n• Say 'I no longer need help' to close your ticket",
        inline=False
    )
    
    help_embed.add_field(
        name="For Staff",
        value="• Type in ticket channels to respond to users\n• Use `/close` to close tickets\n• All messages are logged for reference",
        inline=False
    )
    
    help_embed.add_field(
        name="Commands",
        value="• `/close [channel]` - Close a ticket (staff only)\n• `/help` - Show this help message",
        inline=False
    )
    
    help_embed.set_footer(text="Made by lev (@_yw2) | GitHub: https://github.com/levsimp")
    
    await interaction.response.send_message(embed=help_embed, ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        await handle_user_dm(message)
    
    elif (isinstance(message.channel, discord.TextChannel) and 
          message.channel.name.startswith("ticket-") and 
          not message.content.startswith("/")):
        await handle_staff_message(message)
    
    await bot.process_commands(message)

async def handle_user_dm(message):
    if message.author.id in active_tickets:
        channel_id = active_tickets[message.author.id]
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                description=message.content,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=f"User: {message.author}",
                icon_url=message.author.display_avatar.url
            )
            
            if message.attachments:
                attachment_urls = []
                for attachment in message.attachments:
                    attachment_urls.append(attachment.url)
                embed.add_field(
                    name="Attachments", 
                    value="\n".join(attachment_urls), 
                    inline=False
                )
            
            await channel.send(embed=embed)
            
            if channel.id not in ticket_history:
                ticket_history[channel.id] = []
            ticket_history[channel.id].append((message.author, message.content, datetime.now()))
            
            await message.add_reaction("✅")
        else:
            del active_tickets[message.author.id]
            await create_ticket_channel(message)
    else:
        await create_ticket_channel(message)

async def handle_staff_message(message):
    channel_is_ticket = False
    for cid in active_tickets.values():
        if cid == message.channel.id:
            channel_is_ticket = True
            break
    
    if not channel_is_ticket:
        return
    
    user_id = None
    for uid, cid in active_tickets.items():
        if cid == message.channel.id:
            user_id = uid
            break
    
    if not user_id:
        return
    
    user = await bot.fetch_user(user_id)
    if not user:
        return
    
    if message.channel.id not in ticket_history:
        ticket_history[message.channel.id] = []
    ticket_history[message.channel.id].append((message.author, message.content, datetime.now()))
    
    try:
        embed = discord.Embed(
            title="Staff Response",
            description=message.content,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_author(
            name=f"Staff: {message.author}",
            icon_url=message.author.display_avatar.url
        )
        embed.set_footer(text="Reply to this message to continue the conversation")
        
        if message.attachments:
            attachment_urls = []
            for attachment in message.attachments:
                attachment_urls.append(attachment.url)
            embed.add_field(
                name="Attachments", 
                value="\n".join(attachment_urls), 
                inline=False
            )
        
        await user.send(embed=embed)
        await message.add_reaction("✅")  
    except discord.Forbidden:
        error_embed = discord.Embed(
            title="Error",
            description="Could not send message to user. They may have DMs disabled.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=error_embed)
    except Exception as e:
        logger.error(f"Error sending DM to user: {e}")
        error_embed = discord.Embed(
            title="Error",
            description=f"An error occurred while sending the message: {e}",
            color=discord.Color.red()
        )
        await message.channel.send(embed=error_embed)

async def create_ticket_channel(message):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        logger.error("Guild not found")
        return
    
    category = None
    if CATEGORY_ID:
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
    
    safe_name = ''.join(c for c in message.author.name if c.isalnum() or c in ['-', '_']).lower()
    channel_name = f"ticket-{safe_name}-{message.author.discriminator}"
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
    }
    
    if STAFF_ROLE_ID:
        staff_role = guild.get_role(STAFF_ROLE_ID)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    try:
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Ticket created by {message.author}"
        )
        
        active_tickets[message.author.id] = channel.id
        ticket_history[channel.id] = []
        
        welcome_user_embed = discord.Embed(
            title="Thank you for contacting us!",
            description="Our staff team has been notified and will respond as soon as possible. Please be patient and don't spam. Say 'I no longer need help' to close your ticket.",
            color=discord.Color.green()
        )
        welcome_user_embed.set_footer(text="You can continue to message here to add to your ticket")
        await message.author.send(embed=welcome_user_embed)
        
        welcome_channel_embed = discord.Embed(
            title=f"New ticket from {message.author}",
            description=f"User ID: {message.author.id}\nCreated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            color=discord.Color.blue()
        )
        welcome_channel_embed.set_author(
            name=str(message.author),
            icon_url=message.author.display_avatar.url
        )
        await channel.send(embed=welcome_channel_embed)
        
        if message.content:
            embed = discord.Embed(
                description=message.content,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_author(
                name=f"User: {message.author}",
                icon_url=message.author.display_avatar.url
            )
            
            if message.attachments:
                attachment_urls = []
                for attachment in message.attachments:
                    attachment_urls.append(attachment.url)
                embed.add_field(
                    name="Attachments", 
                    value="\n".join(attachment_urls), 
                    inline=False
                )
            
            await channel.send(embed=embed)
            ticket_history[channel.id].append((message.author, message.content, datetime.now()))
        
        instructions_embed = discord.Embed(
            title="Ticket Instructions",
            description="Just type in this channel to respond to the user. The user will receive your messages via DM.\nUse `/close` to close this ticket.",
            color=discord.Color.gold()
        )
        await channel.send(embed=instructions_embed)
        
    except Exception as e:
        logger.error(f"Error creating ticket channel: {e}")
        error_embed = discord.Embed(
            title="Error",
            description="Sorry, there was an error creating your ticket. Please try again later.",
            color=discord.Color.red()
        )
        await message.author.send(embed=error_embed)

@bot.tree.command(name="close", description="Close a ticket")
async def close_ticket(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not channel:
        channel = interaction.channel
    
    if not channel.name.startswith("ticket-"):
        await interaction.response.send_message("This is not a ticket channel!", ephemeral=True)
        return
    
    if STAFF_ROLE_ID:
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role and staff_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to close tickets!", ephemeral=True)
            return
    
    user_id = None
    for uid, cid in active_tickets.items():
        if cid == channel.id:
            user_id = uid
            break
    
    closing_embed = discord.Embed(
        title="Ticket Closed",
        description=f"This ticket has been closed by {interaction.user.mention}.",
        color=discord.Color.orange()
    )
    await channel.send(embed=closing_embed)
    
    if user_id:
        user = bot.get_user(user_id)
        if user:
            try:
                # Updated notification embed showing who closed the ticket
                notify_embed = discord.Embed(
                    title="Ticket Closed",
                    description=f"Your ticket has been closed by {interaction.user.name}.",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                notify_embed.set_author(
                    name=f"Staff: {interaction.user}",
                    icon_url=interaction.user.display_avatar.url
                )
                notify_embed.set_footer(text="Thank you for contacting us!")
                await user.send(embed=notify_embed)
            except discord.Forbidden:
                logger.warning(f"Could not DM user {user.id}")
        
        del active_tickets[user_id]
    
    await interaction.response.send_message("Closing ticket...", ephemeral=True)
    await asyncio.sleep(3)
    await channel.delete(reason=f"Ticket closed by {interaction.user}")
    
    if channel.id in ticket_history:
        del ticket_history[channel.id]

@close_ticket.error
async def close_ticket_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.BadArgument):
        await interaction.response.send_message("Channel not found!", ephemeral=True)
    else:
        logger.error(f"Error in close command: {e}")
        await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    logger.error(f"Command error: {error}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set!")
        exit(1)
    bot.run(BOT_TOKEN)
