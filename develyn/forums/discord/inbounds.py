
import discord
from discord.ext import commands
from tagger.tagging import add_tag
class Inbound:
    @staticmethod
    async def add_tag_command(ctx, tag_name, tag_description, *sub_tags):
        print("Adding tag with sub_tags: ", sub_tags, " tag_description: ", tag_description, " tag_name: ", tag_name)
        sub_tags_list = list(sub_tags)
        response = add_tag(sub_tags_list, tag_description, tag_name)
        await ctx.send(f"Tag '{tag_name}' added successfully!")