import discord
from discord.ext import tasks
from develyn.forums.discord.config import SERVER_IDS
class Outbound:
    def __init__(self):
        self.new_members = {}  # Dictionary to store new members per server
        self.server_channel_map ={SERVER_IDS: 'channel-name'}
    @staticmethod
    async def send_message_to_channel(guild, channel_name, message):
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel and isinstance(channel, discord.TextChannel):
            await channel.send(message)

    async def welcome_new_member(self, member):
        channel = discord.utils.get(member.guild.channels, name=self.server_channel_map.get(member.guild.id))
        if channel:
            if member.guild.id not in self.new_members:
                self.new_members[member.guild.id] = set()
            self.new_members[member.guild.id].add(member.id)
            print(f"Added {member.id} to new members list for guild {member.guild.id}")

    @tasks.loop(hours=12)
    async def send_periodic_welcome(self, bot):
        for guild in bot.guilds:
            if guild.id in self.new_members and self.new_members[guild.id]:
                channel = discord.utils.get(guild.channels, name=self.server_channel_map.get(guild.id))
                if channel:
                    mentions = ' '.join([f'<@{member_id}>' for member_id in self.new_members[guild.id]])
                    await channel.send(f"Welcome to all our new members! {mentions}")
                self.new_members[guild.id].clear()

    def start_welcome_loop(self, bot):
        self.send_periodic_welcome.start(bot)