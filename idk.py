
"""Helium bot src

developer m07/puncmadem07
Owners cwelium/wrix FUCK THEM I HATE THEM

"""

import discord
import random
import json
from discord.ext import commands, tasks
from datetime import datetime, timedelta

TOKEN = ''

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

def dataofkey():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=17))

def checkdataofkey(license_type):
    now = datetime.now()
    if license_type == "Lifetime":
        return now + timedelta(days=5000)
    elif license_type == "Monthly":
        return now + timedelta(days=30)
    elif license_type == "Weekly":
        return now + timedelta(days=7)
    elif license_type == "Daily":
        return now + timedelta(days=1)
    return now

def check_expired_keys():
    users = load_users()
    now = datetime.now()

    expired_users = []

    for user_id, user_data in users.items():
        expiry_date = datetime.strptime(user_data['expiry'], "%Y-%m-%d %H:%M:%S")
        if now >= expiry_date:
            expired_users.append(user_id)

    for user_id in expired_users:
        del users[user_id]
        print(f"License for {user_id} is Fucked Up")

    save_users(users)

@tasks.loop(hours=24)
async def check_expired_keys_loop():
    check_expired_keys()

async def send_confirmation(user, license_type, license_key):
    embed = discord.Embed(
        title="`✨` Thank you for your purchase!",
        description=f"Here is your {license_type} license key.",
        color=discord.Color.green()
    )
    embed.add_field(name="`🔐` License Key", value=license_key, inline=False)
    embed.add_field(name="`📅` License Type", value=license_type, inline=True)
    embed.set_thumbnail(url=user.avatar.url if user.avatar else "")
    embed.set_footer(text="Enjoy your new license! Main Developer @Puncmade m07")

    try:
        await user.send(embed=embed)
        print(f"License sent to {user.name}")
    except discord.Forbidden:
        print(f"Could not send DM to {user.name}")

@bot.tree.command(name="create-key", description="Helium Or m07 loves you")
async def create_key(interaction: discord.Interaction, license_type: str, target_user: discord.User):
    if license_type.lower() not in ["lifetime", "weekly", "daily", "monthly"]:
        await interaction.response.send_message("Please select a valid license type (lifetime, weekly, daily, or monthly).", ephemeral=True)
        return

    admin_role = discord.utils.get(interaction.user.roles, name="Admin")
    if admin_role is None:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    key = dataofkey()
    expiry_date = checkdataofkey(license_type.capitalize())

    pfp_url = target_user.avatar.url if target_user.avatar else None
    
    highest_role = target_user.top_role.name if target_user.top_role else "None"

    users = load_users()
    users[target_user.id] = {
        'username': str(target_user),
        'license': key,
        'type': license_type.capitalize(),
        'status': 'valid',
        'pfp': pfp_url,
        'expiry': expiry_date.strftime("%Y-%m-%d %H:%M:%S"),
        'highest_role': highest_role
    }
    save_users(users)

    await send_confirmation(target_user, license_type.capitalize(), key)

    await interaction.response.send_message(f"{license_type.capitalize()} license key generated for {target_user.name}.", ephemeral=True)


@bot.tree.command(name="status", description="Check your current license status")
async def status(interaction: discord.Interaction):
    users = load_users()
    user_id = str(interaction.user.id)

    if user_id not in users:
        await interaction.response.send_message("You do not have an active license. Please purchase one.", ephemeral=True)
        return

    user_data = users[user_id]
    license_key = user_data['license']
    license_type = user_data['type']
    expiry_date = user_data['expiry']
    highest_role = user_data.get('highest_role', 'None')

    embed = discord.Embed(
        title="`✨` Your License Status",
        description="Thank you For Buying Helium",
        color=discord.Color.blue()
    )
    embed.add_field(name="`🔐` License Key", value=license_key, inline=False)
    embed.add_field(name="`🔗` License Type", value=license_type, inline=True)
    embed.add_field(name="`📅` Expiry Date", value=expiry_date, inline=True)
    embed.add_field(name="`👑` Rank", value=highest_role, inline=True)
    embed.set_thumbnail(url=user_data['pfp'] if user_data['pfp'] else "")
    embed.set_footer(text="Main Developer Puncmade m07")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="remove-key", description="Mo7 loves niggers")
async def remove_key(interaction: discord.Interaction, license_key: str):
    niggero = discord.utils.get(interaction.user.roles, name="Admin")
    if niggero is None:
        await interaction.response.send_message("Nigga m07 told me that he will kiss you", ephemeral=True)
        return
    
    users = load_users()

    user_id_to_remove = None
    for user_id, user_data in users.items():
        if user_data['license'] == license_key:
            user_id_to_remove = user_id
            break

    if user_id_to_remove is None:
        await interaction.response.send_message("Nigga wrong key", ephemeral=True)

    del users[user_id_to_remove]
    save_users(users)

    await interaction.response.send_message(f"{license_key} has been removed.", ephemeral=True)
    print(f"Removed user {user_id_to_remove} with license key {license_key}")

@bot.tree.command(name="info", description="Get User Data From api")
async def info(interaction: discord.Interaction, target_user: discord.User):
        admin_role = discord.utils.get(interaction.user.roles, name="Admin")
        if admin_role is None:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        users = load_users()
        user_id = str(target_user.id)

        if user_id not in users:
            await interaction.response.send_message(f"{target_user} Deosnt have any key BOSS!", ephemeral=True)
            return
        
        user_data = users[user_id]
        license_key = user_data['license']
        license_type = user_data['type']
        expiry_date = user_data['expiry']
        highest_role = user_data.get('highest_role', 'None')
        pfp_url = user_data['pfp'] if user_data['pfp'] else "https://images-ext-1.discordapp.net/external/Nr4X4kyBBVFLiEeJtkEfBa3I2Pc2sQMua2BezLbvmrk/%3Fsize%3D4096/https/cdn.discordapp.com/embed/avatars/0.png?format=webp&quality=lossless"

        embed = discord.Embed(
            title=f"`💾` Got Info for {target_user}",
            color=discord.Color.blue()
        )
        embed.add_field(name="`🔐` License Key", value=license_key, inline=False)
        embed.add_field(name="`🔗` License Type", value=license_type, inline=True)
        embed.add_field(name="`📅` Expiry Date", value=expiry_date, inline=True)
        embed.add_field(name="`👑` Rank", value=highest_role, inline=True)
        embed.set_thumbnail(url=pfp_url)
        embed.set_footer(text="Main Developer Puncmade m07")

        await interaction.response.send_message(content=f"Successfully got info for {target_user.mention}", embed=embed, ephemeral=True)

def get_database(sreach1):
    try:
        with open('nusi.pl.txt', 'r', encoding='utf-8') as nigger:
            for line in nigger:
                if sreach1 in line:
                    return line.strip()
        return None
    except FileNotFoundError:
        return None
    
@bot.tree.command(name="check", description="Check Database Minecraft Database")
async def check(interaction: discord.Interaction, sreach1: str):
    Customer = discord.utils.get(interaction.user.roles, name="Customers")
    if Customer is None:
        await interaction.response.send_message("You're Not A Customer Please Buy Our Paid Version", ephemeral=True)
        return
    
    data = get_database(sreach1)

    if data is None:
        await interaction.response.send_message(f"NO DATA FOUND FOR `{sreach1}`", ephemeral=True)
        return
    
    try:
        name, ip = data.split(":")
    except ValueError:
        await interaction.response.send_message(f"Database Can't Find!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"`📄` Data for {name}",
        description=f"Here is the information Got From Database `{name}`",
        color=discord.Color.green()
    )
    embed.add_field(name="`📝` Name", value=name, inline=False)
    embed.add_field(name="`💬` Data", value="Successfully", inline=True)
    embed.add_field(name="`🌍` IP", value=ip, inline=True)
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/ykS9YS_6Lk1VRra8OIBrWWoWIfuNBu2lJdijPj4CT0M/%3Fsize%3D512/https/cdn.discordapp.com/avatars/1244373951015157912/90decb5345a6ee839853214df72455ee.png?format=webp&quality=lossless")
    embed.set_footer(text="Main Developer Puncmade m07")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Slash commands synced!")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands!")
    except Exception as fuck:
        print(f"{fuck}")

    check_expired_keys_loop.start()

bot.run(TOKEN)
