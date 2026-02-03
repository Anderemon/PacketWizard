#bot.py
import os
import os.path
import re
import discord
from wakeonlan import send_magic_packet
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN", "")

intents = discord.Intents.default()

class Bot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()

bot = Bot(command_prefix="!", case_insensitive=False, intents=intents)
regex_ip = r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
#regex_mac = r"'[\:\-]'.join(['([0-9a-f]{2})']*6)$"
regex_mac = r"^([0-9a-f]{2}[:-]){5}[0-9a-f]{2}$"


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.tree.command(name="files", description="Lists all Devices")
async def files(interaction: discord.Interaction):
    files = os.listdir("./devices/")
    if not files:
        await interaction.response.send_message("no Device found")
        return
    files_message = "\n".join(files)
    await interaction.response.send_message(files_message)



@bot.tree.command(name="start", description="Send packet to selected file")
async def start(interaction: discord.Interaction, device: str):
      file_path = ("./devices/" + device)
      if os.path.isfile(file_path):
         variables = {}
         with open(file_path, 'r') as f:
            for line in f:
                name, value = line.split("=")
                variables[name] = str(value)
         mac_addr = variables["mac_addr"].strip("\n")
         ip_addr = variables["ip_addr"].strip("\n")
         port_addr = variables["port_addr"].strip("\n")
         mac_validation = bool (re.fullmatch(regex_mac, mac_addr.lower()))
         #need mac failsafe if wrong
         if mac_validation == True:
            if(re.search(regex_ip, ip_addr)):
                #if ip wrong, default ip 255.255.255.255
                port_validation = int(port_addr) in range(0, 65536)
                #if empty, default to port 9
                if port_validation ==  True:  
                        send_magic_packet(mac_addr, ip_address=str(ip_addr), port=int(port_addr))
                        await interaction.response.send_message(str("Magic Packet was sent to " + device))
                else:
                    await interaction.response.send_message("Invalid Port")
            else:
                await interaction.response.send_message("Invalid IP-Address")     
         else:
            await interaction.response.send_message("Invalid MAC-Address")                             
      else:
        await interaction.response.send_message("File does not exist")

@bot.tree.command(name="custom", description="Send packet to custom Device")
async def custom(interaction: discord.Interaction, device: str):
    await interaction.response.send_message("OK", ephemeral=True)
   
#@bot.command()
#async def custom(ctx, custom_mac, custom_ip = "255.255.255.255", custom_port = "9"):
#        custom_mac_validation = bool(re.match('^' + '[\:\-]'.join(['([0-9a-f]{2})']*6) + '$', custom_mac.lower()))
#        if custom_mac_validation == True:
#            if(re.search(regex_ip, custom_ip)):
#                custom_port_validation = int(custom_port) in range(0, 65536)
#                if custom_port_validation ==  True:
#                    send_magic_packet(custom_mac, ip_address=str(custom_ip), port=int(custom_port))
#                    await ctx.send("Magic Packet was sent to MAC-Address " + custom_mac + " , IP-Address " + custom_ip + " and Port " + custom_port)
#                else: 
#                    await ctx.send("Invalid Port")
#            else: 
#                await ctx.send("Invalid IP-Address") 
#        else:
#            await ctx.send("Not a valid MAC-Address")  
                                       
bot.run(TOKEN)

