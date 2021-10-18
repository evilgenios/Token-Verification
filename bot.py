import discord, asyncio, requests, os, sys
from random import choice
from discord.utils import _unique, get, find
from discord.ext import commands
from discord.ext.commands.core import command, has_any_role, has_permissions
import json
from threading import *
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)
bot.remove_command('help')



path = os.path.abspath('Tokens.json')
path2 = os.path.abspath('RegisteredUsers.json')


with open(path) as data:
    tokens = json.load(data)

if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config


tokenOpts = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890".lower()

def GenToken():
    t1 = ''.join((choice(tokenOpts)) for x in range(5))
    t2 = ''.join((choice(tokenOpts)) for x in range(3))
    t3 = ''.join((choice(tokenOpts)) for x in range(7))
    t4 = ''.join((choice(tokenOpts)) for x in range(5))
    return f"{t1}-{t2}-{t3}-{t4}"




@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=config.role_name)
    await member.add_roles(role)
    print(f"Assigned {role} to {member}!")


@bot.event
async def on_message(message): 
    message.content = message.content.lower()
    if "Direct Message" in str(message.channel): return

    if f"$createtoken" in (message.content).lower(): 
        await bot.process_commands(message)
        return
    elif f"$register" in (message.content).lower():
        await bot.process_commands(message)
        return

    with open(path2, "r") as l: tokenObj = json.load(l)
    for item in tokenObj:
        if message.author.id == item['ID']:
            if item['Banned']:
                chan = await bot.fetch_user(item['ID'])
                await chan.send(f"Your user is banned | Reason: Don't be gay :)")
                await message.guild.ban(chan, reason="Expired")
                break
            elif datetime.now() > datetime.strptime(item['Expiration'], "%Y-%m-%d %H:%M:%S.%f"): 
                chan = await bot.fetch_user(item['ID'])
                await message.guild.kick(chan, reason="Expired")
                break
            else:
                await bot.process_commands(message)
                break   
    l.close()

@bot.command()
async def createtoken(ctx, planDays=0):
    if ctx.message.author.id in config.OWNERS:
        tkn = []
        with open(path, "r") as data: tokens = json.load(data)
        with open(path, "w") as output:
            tok = GenToken()
            tkn.append(tok)
            tokens[0]['Unused'].append({"Days": planDays, "Level": "None", "Token": str(tok)})
            output.write(json.dumps(tokens, sort_keys=False, indent=4))
            o = '\n'.join(tkn)
            embed = discord.Embed(
                title="Verification",
                color= discord.Color.dark_theme()
            )
            embed.add_field(name="Token Status: Created <:white_check_mark:886940376127131689>", value=f"Token: `{o}`")
            embed.set_footer(text="Verification", icon_url="")
            await ctx.send(embed=embed)


def RemoveRegToken(tk, nick, auth):
    with open(path, 'r') as f: tokenObj = json.load(f)
    for token in tokenObj[0]['Unused']:
        if token['Token'] == tk:
            tokenObj[0]['Unused'].remove(token)
            token.update({'UsedBy': [{'Discord': str(auth), 'Nickname': str(nick)}]})
            tokenObj[0]['Used'].append(token)
    with open(path, "w") as output: output.write(json.dumps(tokenObj, sort_keys=True, indent=4))


invites = []


@bot.command()
async def register(ctx, Token=None, Nickname=None):
        embed = discord.Embed(title=f"Registered", color=discord.Color.dark_theme())
        reg = False
        if Token and Nickname != None: 
            with open(path, 'r') as f: tknObj = json.load(f)
            for item in tknObj[0]['Unused']:
                if Token == item['Token']:
                    with open(path2, 'r') as ff: gg = json.load(ff)
                    with open(path2, 'w') as output: 
                        gg.append({'Discord': str(ctx.author), 'Nickname': str(Nickname),'RegisterToken': item['Token'], 'Banned': False, 'BanReason': '', 'ID': ctx.author.id, 'Expiration': f"{datetime.now() + timedelta(item['Days'])}", 'Level': "None"})
                        output.write(json.dumps(gg, sort_keys=True, indent=4))
                    member = ctx.message.author
                    embed.add_field(name="Register Successful", value=f"Details:\nToken: `{Token}`\nExpiration: `{item['Days']}` days\nLevel: `None`", inline=False)
                    await ctx.send(embed=embed)
                    channel = bot.get_channel(config.channel_id)
                    invitelink = await channel.create_invite(max_uses=1, unique=True)
                    await ctx.message.author.send(invitelink)
                    guild = ctx.guild
                    member = ctx.author
                    #overwrites = {
                    #    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    #    member: discord.PermissionOverwrite(read_messages=True)
                    #}
                    #channel = await guild.create_text_channel(ctx.author.name, overwrites=overwrites)
                    reg = True
                    Thread(target=RemoveRegToken, args=(Token, Nickname, ctx.message.author)).start()
                    break  
            if reg == False:
                embed = discord.Embed(title=f"ERROR", color=discord.Color.dark_theme())
                embed.add_field(name="Register Fail", value=f"Invalid Token", inline=False)
                embed.set_footer(text="Verification", icon_url="")
                await ctx.send(embed=embed)  
                return
        else:
            embed.add_field(name="$Register <token> <nickname>", value=f"Invalid Token/missing nickname", inline=False)
            embed.set_footer(text="Verification", icon_url="")
            await ctx.send(embed=embed) 
            return


bot.run('Token Here')
