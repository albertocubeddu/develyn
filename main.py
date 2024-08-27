import discord
from discord.ext import commands


from develyn.graph import get_graph
from develyn.agent.base import AgentName
from develyn.agent.community_manager_agent.state import MessageRouterResponse
from develyn.agent.community_manager_agent.actions import Action
from develyn.agent.qa_agent.state import QAAgentResponseSchema
from develyn.agent.developer_agent.state import DeveloperAgentResponseSchema
from develyn.forums.discord.outbounds import Outbound
from langsmith import Client
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import ast
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('BOT_API_KEY')

import os
from firebase_admin import initialize_app, credentials, firestore
import random
import string
import pickle
import csv
from io import StringIO
from copy import deepcopy
import requests
import json
from cryptography.fernet import Fernet
import base64
from discord_onboard import setup as setup_onboarding

db = firestore.client()

#Langsmith client
client = Client()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True 
bot = commands.Bot(command_prefix='\\', intents=intents)

# Initialize Outbound
outbound = Outbound()

# Sever Channel Map
server_channel_map = {SERVER_NAME: 'channel-name'}


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    if len(bot.guilds) > 0:
        for guild in bot.guilds:
            print(f'- {guild.name} (id: {guild.id})')
    else:
        print('Bot is not in any guilds. Make sure you\'ve invited it to your server.')
    # Start the periodic welcome message loop
    outbound.start_welcome_loop(bot)
    # Call the setup function for onboarding
    await setup_onboarding(bot)

@bot.event
async def on_member_join(member):
    await outbound.welcome_new_member(member)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    server_id = message.guild.id if message.guild else None
    server_id = str(server_id)
    doc_refs =db.collection('server_config').document(str(server_id)).get()
    server_config = doc_refs.to_dict()
    tag_data = ""
    for each_tag in server_config['tag_data']:
        tag_data += f"Tag: {each_tag['tag_name']}\nDescription: {each_tag['tag_description']}\nSub-tags: {', '.join(each_tag['sub_tags'])}\n\n"
    print("Fetched server config: ", server_config)
    graph = get_graph()
    persisted_state = {
        "company_name": server_config.get("company_name", "Langchain"),
        "company_description": server_config.get("company_description", "Langchain is a platform for building and deploying language models"),
        "tag_data": tag_data,
        "docs_url": server_config.get("docs_urls", ["https://python.langchain.com/v0.2/docs/concepts/#langchain-expression-language-lcel"]),
        "project_name": server_config.get("project_name", "Langchain")
    }
    messages = [HumanMessage(content=message.content)]
    result = graph.invoke(
        input=(
            {
                "messages": messages,
                "persisted_state": persisted_state,
            }
        ),
        config = {"recursion_limit": 8})

    raw_result = result['messages'][-1].content
    replaced_raw_result = raw_result.replace("true", "True").replace("false", "False")
    result_data = ast.literal_eval(replaced_raw_result)
    result_agent = result['messages'][-1].name 
    if result_agent == AgentName.COMMUNITY_MANAGER_AGENT:
        response = MessageRouterResponse(**result_data)
        action = response.action
        msg = response.message
        detected_tags = response.tags
        detected_subtags = response.sub_tags
        msg = message.author.mention + msg + f"\n\nTags detected: {detected_tags}\nSub-tags detected: {detected_subtags}"
        if action == Action.IGNORE:
            msg = "Ignore message: " + msg

        await outbound.send_message_to_channel(message.guild, server_channel_map[server_id], msg)
    if result_agent == AgentName.QA_AGENT:
        response = QAAgentResponseSchema(**result_data)
        msg = message.author.mention + response.message_reponse
        thread = await message.create_thread(name=f"Thread for {message.content[:10]}")
        await thread.send(msg)
    if result_agent == AgentName.DEVELOPER_AGENT:
        response = DeveloperAgentResponseSchema(**result_data)
        if response.has_errors:
            apologize_for_errors_str = "Please make sure all libraries used are correctly installed.\n"
            msg = message.author.mention + apologize_for_errors_str
            msg += f"```python\n{response.code.strip()}\n```"
        else:
            working_code_str = "Sure, I have also tested the code and it will execute directly. Here is the code!\n"
            msg = message.author.mention + working_code_str
            msg += f"```python\n{response.code.strip()}\n```"
        thread = await message.create_thread(name=f"Thread for {message.content[:10]}")
        await thread.send(msg)
    await bot.process_commands(message)
# Run the bot
bot.run(DISCORD_BOT_TOKEN)
