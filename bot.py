
import os
import requests
from telethon import TelegramClient, events, sync
from telethon.tl.functions.channels import InviteToChannelRequest

# Define constants
API_ID = '21634981'
API_HASH = 'c4b3f95a23f0435168c955a22c800a90'
BOT_TOKEN = '7322123835:AAGbn8Lrfl4f-mrU1gfqCc3fRrXNSvqS-Ac'
GROUP_ID = '-1002222790187'  # Change to group ID
GITHUB_REPO_URL = 'https://raw.githubusercontent.com/ShashwatMishra0099/Members.run/main/members.txt'

# Initialize Telegram client for bot
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Function to fetch members from GitHub
def fetch_members_from_github():
    response = requests.get(GITHUB_REPO_URL)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        raise Exception("Failed to fetch members.txt from GitHub")

# Function to add members to the group
async def add_members_to_group(client, members, group_id):
    for member in members:
        try:
            await client(InviteToChannelRequest(group_id, [member]))
            print(f"Added {member} to the group {group_id}")
        except Exception as e:
            print(f"Failed to add {member}: {e}")

# Handle bot events for login
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Please provide your phone number for login.")
    bot.add_event_handler(handle_phone_number)

@bot.on(events.NewMessage)
async def handle_phone_number(event):
    phone_number = event.message.text
    await event.respond("Please provide the OTP sent to your phone.")
    bot.add_event_handler(lambda e: handle_otp(e, phone_number))

async def handle_otp(event, phone_number):
    otp = event.message.text
    client = TelegramClient(phone_number, API_ID, API_HASH)
    await client.connect()
    try:
        await client.sign_in(phone_number, otp)
        await event.respond("Login successful. Adding members to the group...")
        
        # Fetch members from GitHub
        members = fetch_members_from_github()

        # Add members to the group
        await add_members_to_group(client, members, GROUP_ID)

        await event.respond("All members have been added.")
    except Exception as e:
        await event.respond(f"Login failed: {e}")
    finally:
        await client.disconnect()

bot.start()
bot.run_until_disconnected()
