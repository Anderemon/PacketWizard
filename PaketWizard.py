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
regex_ip = r"^((25[0-5]|2[0-4][0-default_port]|1[0-default_port][0-default_port]|[1-default_port]?[0-default_port])\.){3}(25[0-5]|2[0-4][0-default_port]|1[0-default_port][0-default_port]|[1-default_port]?[0-default_port])$"
regex_mac = r"^(?:[0-default_porta-fA-F]{12}|(?:[0-default_porta-fA-F]{2}[:-]){5}[0-default_porta-fA-F]{2})$"
base_dir = "./devices"
default_ip = "255.255.255.255"
default_port = "9"

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.tree.command(name="files", description="Lists all Devices")
async def files(interaction: discord.Interaction):
    files = os.listdir(base_dir)
    if not files:
        await interaction.response.send_message("no Device found")
        return
    files_message = "\n".join(files)
    await interaction.response.send_message(files_message)

@bot.tree.command(name="start", description="Send packet to selected file")
async def start(interaction: discord.Interaction, device: str):
      file_path = (base_dir + device)
      if os.path.isfile(file_path):
         variables = {}
         with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if "=" not in line:
                    continue
                name, value = line.split("=",1)
                variables[name.strip()] = value.strip()
         mac_addr = variables.get("mac_addr")
         if mac_addr is None or not mac_addr.strip():
              await interaction.response.send_message("No MAC address defined in device file.")
              return
         mac_addr = mac_addr.strip()
         ip_addr = variables.get("ip_addr",default_ip)
         port_addr = variables.get("port_addr",default_port)
         mac_validation = bool (re.fullmatch(regex_mac, mac_addr.lower()))
         if mac_validation == True:
            if(re.search(regex_ip, ip_addr)):
                try:
                    port = int(port_addr)
                    if not (1 <= port <= 65535):
                        raise ValueError
                except (TypeError, ValueError):
                    await interaction.response.send_message("Invalid Port")
                    return 
                send_magic_packet(mac_addr, ip_address=str(ip_addr), port=int(port))
                await interaction.response.send_message("Magic Packet was sent to " + device ) 
            else:
                await interaction.response.send_message("Invalid IP-Address")     
         else:
            await interaction.response.send_message("Invalid MAC-Address")                             
      else:
        await interaction.response.send_message("File does not exist")

@bot.tree.command(name="custom", description="Send packet to custom Device")
async def custom(interaction: discord.Interaction,
                 mac: str, ip: str | None = None, port: int | None = None):
         
         mac_addr = mac.strip()
         ip_addr = ip or default_ip
         port_addr = port or default_port
         mac_validation = bool (re.fullmatch(regex_mac, mac_addr.lower()))
         if mac_validation == True:
            if(re.search(regex_ip, ip_addr)):
                try:
                    port = int(port_addr)
                    if not (1 <= port <= 65535):
                        raise ValueError
                except (TypeError, ValueError):
                    await interaction.response.send_message("Invalid Port")
                    return
                send_magic_packet(mac_addr, ip_address=str(ip_addr), port=int(port))
                await interaction.response.send_message("Magic Packet was sent to device with mac: " + mac)
            else:
                await interaction.response.send_message("Invalid IP-Address")     
         else:
            await interaction.response.send_message("Invalid MAC-Address")                             

@bot.tree.command(name="create", description="Create device file")
async def create(interaction: discord.Interaction,
                 device_name: str, mac: str, ip: str | None = None, port: int | None = None):
        mac_addr = mac.strip()
        ip_addr = ip or default_ip
        port_addr = port or default_port
        mac_validation = bool (re.fullmatch(regex_mac, mac_addr.lower()))
        if mac_validation == True:
            if(re.search(regex_ip, ip_addr)):
                try:
                    port = int(port_addr)
                    if not (1 <= port <= 65535):
                        raise ValueError
                except (TypeError, ValueError):
                    await interaction.response.send_message("Invalid Port")
                    return
                file_path = os.path.join(base_dir, device_name)

                variables = {
                    "mac_addr": mac_addr,
                    "ip_addr": ip_addr,
                    "port_addr": port,
                }

                with open(file_path, "w", encoding="utf-8") as f:
                    for name, value in variables.items():
                        f.write(f"{name}={value}\n")

                await interaction.response.send_message("Device file was created")
            else:
                await interaction.response.send_message("Invalid IP-Address")     
        else:
            await interaction.response.send_message("Invalid MAC-Address") 
                                           
bot.run(TOKEN)

