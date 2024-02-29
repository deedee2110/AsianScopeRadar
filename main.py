import asyncio
from datetime import datetime
import json
import discord
import requests
from dateutil.parser import parse

intent = discord.Intents.default()
intent.message_content = True

# Load config.json
with open('config.json', 'r') as f:
    config = json.load(f)
    BOT_TOKEN = config['BOT_TOKEN']
    CALLSIGN = config['CALLSIGN']
    CONTROLLER_CHANNEL_ID = config['CONTROLLER_CHANNEL_ID']
    ATIS_CHANNEL_ID = config['ATIS_CHANNEL_ID']


client = discord.Client(intents=intent)
controllers = []
vt_controllers = []
new_controllers = []
vt_atis = []
atis = []
new_atis = []
offline_controllers = []
offline_atis = []


def get_data():
    response = requests.get('https://data.vatsim.net/v3/vatsim-data.json')
    data = response.json()
    return data


def get_facility_emoji(callsign):
    facility_emojis = {
        "DEL": "<:DEL:1212392580344582236>",
        "GND": "<:GND:1212392592604405760>",
        "TWR": "<:TWR:1212392595708186724>",
        "APP": "<:APP:1212392574740996096>",
        "DEP": "<:DEP:1212392589857390592>",
        "CTR": "<:CTR:1212392906716090430>"
    }
    facility = callsign.split("_")[-1]
    return facility_emojis.get(facility, "❓❓")


def get_regional_indicator(atis_code):
    regional_indicators = {
        "A": "🇦",
        "B": "🇧",
        "C": "🇨",
        "D": "🇩",
        "E": "🇪",
        "F": "🇫",
        "G": "🇬",
        "H": "🇭",
        "I": "🇮",
        "J": "🇯",
        "K": "🇰",
        "L": "🇱",
        "M": "🇲",
        "N": "🇳",
        "O": "🇴",
        "P": "🇵",
        "Q": "🇶",
        "R": "🇷",
        "S": "🇸",
        "T": "🇹",
        "U": "🇺",
        "V": "🇻",
        "W": "🇼",
        "X": "🇽",
        "Y": "🇾",
        "Z": "🇿"
    }
    return regional_indicators.get(atis_code, "❓")


def get_controller(data):
    controllers = data['controllers']
    vt_controllers = [controller for controller in controllers if controller['callsign'].startswith(CALLSIGN)]
    return vt_controllers


def get_atis(data):
    atis = data['atis']
    vt_atis = [atis for atis in atis if atis['callsign'].startswith(CALLSIGN)]
    return vt_atis


def get_controller_embed(controller):
    if controller:
        embed = discord.Embed(
            title="🇹🇭 VATSIM Thailand Online Controller Status !",
            description=f"🟢  There are currently {len(controller)} controllers online at the moment !",
            color=discord.Color.dark_green()
        )

        for controller in controller:
            logon_time = parse(controller['logon_time'])
            logon_time = logon_time.strftime("%H:%M:%S")
            text_atis = controller['text_atis'][0] if controller['text_atis'] else "UNKNOWN"
            embed.add_field(
                name=f"{get_facility_emoji(controller['callsign'])}  {controller['callsign']} - {controller['name']}",
                value=f"{text_atis} ● 📻 {controller['frequency']} ● Online Since {logon_time} UTC",
                inline=False)
        embed.set_footer(text=f"Last Updated")
        embed.timestamp = datetime.now()
        return embed
    else:
        embed = discord.Embed(
            title="🇹🇭 VATSIM Thailand Online Controller Status !",
            description="🔴 There is no active VATSIM Thailand Controller at the moment.TT",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Last Updated")
        embed.timestamp = datetime.now()
        return embed

def get_atis_embed(atis):
    if atis:
        embed = discord.Embed(
            title="🇹🇭  VATSIM Thailand Real-Time ATIS Status !",
            description=f"🟢  There are currently {len(atis)} ATIS online at the moment !",
            color=discord.Color.brand_green()
        )
        for atis in atis:
            embed.add_field(name=f"{get_regional_indicator(atis['atis_code'])} {atis['callsign']} - {atis['name']}",
                            value=f"{atis['text_atis']}",
                            inline=False)
    else:
        embed = discord.Embed(
            title="🇹🇭  VATSIM Thailand Real-Time ATIS Status !",
            description="🔴  There is no active VATSIM Thailand ATIS at the moment.",
            color=discord.Color.red()
        )
    embed.set_footer(text=f"Last Updated")
    embed.timestamp = datetime.now()
    return embed


async def send_hi_message(controller, channel):
    await channel.send(
        f"Hi ! {controller['name']} are online on {controller['callsign']} at {controller['frequency']} !!!")
    await asyncio.sleep(5)
    await channel.purge(limit=1)


async def send_offline_message(controller, channel):
    await channel.send(f"Bye ! {controller['callsign']} - {controller['name']} went offline")
    await asyncio.sleep(5)
    await channel.purge(limit=1)


@client.event
async def on_ready():
    global controllers, atis, new_controllers, new_atis, offline_controllers, offline_atis
    print(f"We have logged in as {client.user}")
    initial = True
    con_channel = client.get_channel(CONTROLLER_CHANNEL_ID)
    print(con_channel)
    atis_channel = client.get_channel(ATIS_CHANNEL_ID)
    print(atis_channel)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="VATSIM Data API 📡📡"))
    while True:
        data = get_data()
        vt_controllers = get_controller(data)
        vt_atis = get_atis(data)

        for controller in vt_controllers:
            if controller['callsign'] not in [c['callsign'] for c in controllers]:
                print(f"{controller['callsign']} is online")
                new_controllers.append(controller)

        for atis_info in vt_atis:
            if atis_info['callsign'] not in [a['callsign'] for a in atis]:
                print(f"{atis_info['callsign']} has ATIS")
                new_atis.append(atis_info)

        for controller in controllers:
            if controller['callsign'] not in [vc['callsign'] for vc in vt_controllers]:
                print(f"{controller['callsign']} is offline")
                offline_controllers.append(controller)

        for atis_info in atis:
            if atis_info['callsign'] not in [va['callsign'] for va in vt_atis]:
                print(f"{atis_info['callsign']} has no ATIS")
                offline_atis.append(atis_info)

        print("✔️✔️✔️")
        atis_updated = False
        for prev, curr in zip(atis, vt_atis):
            if prev['atis_code'] != curr['atis_code']:
                atis_updated = True
                break
        controller_updated = False
        for prev, curr in zip(controllers, vt_controllers):
            if prev['frequency'] != curr['frequency']:
                controller_updated = True
                break
            elif prev['text_atis'] != curr['text_atis']:
                controller_updated = True
                break
        controllers = vt_controllers
        atis = vt_atis
        # If NewControllers or Controller Offline
        if new_controllers or offline_controllers or initial or controller_updated :
            # Delete Previous Embed
            await con_channel.purge(limit=1)
            embed = get_controller_embed(controllers)
            await con_channel.send(embed=embed)
            # Send Hi ! -Name- are online on -Callsign- at -Frequency- !!! and Bye ! -Callsign- -Name- went offline
            tasks = ([send_hi_message(controller, con_channel) for controller in new_controllers] +
                     [send_offline_message(controller, con_channel) for controller in offline_controllers])
            await asyncio.gather(*tasks)
            offline_controllers = []
            new_controllers = []
        if new_atis or offline_atis or initial or atis_updated:
            initial = False
            # Delete Previous Embed
            await atis_channel.purge(limit=1)
            embed = get_atis_embed(atis)
            await atis_channel.send(embed=embed)
            offline_atis = []
            new_atis = []

        await asyncio.sleep(20)



client.run(BOT_TOKEN)
