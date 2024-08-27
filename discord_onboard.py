import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
from dotenv import load_dotenv
import os
from firebase_admin import initialize_app, credentials, firestore

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('BOT_API_KEY')

# Path to the service account key JSON file
cred = credentials.Certificate("./firebase-config.json")

initialize_app(cred)

db = firestore.client()

class CompanyProjectInfoModal(discord.ui.Modal, title='Company and Project Information'):
    company_name = discord.ui.TextInput(label='Company Name')
    company_description = discord.ui.TextInput(label='Company Description', style=discord.TextStyle.paragraph)
    project_name = discord.ui.TextInput(label='Project Name')
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()

class DocsUrlModal(discord.ui.Modal, title='Documentation URLs'):
    docs_urls = discord.ui.TextInput(label='Documentation URLs (comma-separated)')
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()

class TagDataModal(discord.ui.Modal, title='Tag Data'):
    tag_name = discord.ui.TextInput(label='Tag Name')
    sub_tags = discord.ui.TextInput(label='Sub-tags (comma-separated)')
    tag_description = discord.ui.TextInput(label='Tag Description', style=discord.TextStyle.paragraph)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()

class ServerConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'server_config.json'

    @app_commands.command(name="configure", description="Set up server-wide configurations")
    @app_commands.checks.has_permissions(administrator=True)
    async def configure(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.start_configuration(interaction)

    async def start_configuration(self, interaction: discord.Interaction):
        try:
            # Step 1: Company and Project Information
            company_project_modal = CompanyProjectInfoModal()
            await interaction.followup.send("Let's start with company and project information. Click the button below to continue.", view=ModalView(company_project_modal), ephemeral=True)
            await company_project_modal.wait()
            
            # Step 2: Documentation URLs
            docs_modal = DocsUrlModal()
            await interaction.followup.send("Great! Now let's add documentation URLs. Click the button to continue.", view=ModalView(docs_modal), ephemeral=True)
            await docs_modal.wait()
            
            # Step 3: Tag Data (multiple tags)
            tag_data = []
            while True:
                tag_modal = TagDataModal()
                await interaction.followup.send("Now, let's add a tag. Click the button to add a tag.", view=ModalView(tag_modal), ephemeral=True)
                await tag_modal.wait()
                
                tag_data.append({
                    "tag_name": tag_modal.tag_name.value,
                    "sub_tags": [tag.strip() for tag in tag_modal.sub_tags.value.split(',')],
                    "tag_description": tag_modal.tag_description.value
                })
                
                # Ask if the admin wants to add another tag
                continue_adding = await self.ask_continue(interaction)
                if not continue_adding:
                    break
            
            # Collect all the data
            new_config = {
                "company_name": company_project_modal.company_name.value,
                "company_description": company_project_modal.company_description.value,
                "project_name": company_project_modal.project_name.value,
                "docs_urls": [url.strip() for url in docs_modal.docs_urls.value.split(',')],
                "tag_data": tag_data
            }
            
            # Update the configuration
            success = await self.update_config(interaction.guild_id, new_config)
            
            if success:
                await interaction.followup.send("Server configuration has been successfully updated!", ephemeral=True)
            else:
                await interaction.followup.send("Failed to update server configuration. Please try again.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

    @app_commands.command(name="add_url", description="Add new documentation URLs")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_url(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        docs_modal = DocsUrlModal()
        await interaction.followup.send("Add new documentation URLs. Click the button to continue.", view=ModalView(docs_modal), ephemeral=True)
        await docs_modal.wait()
        
        new_urls = [url.strip() for url in docs_modal.docs_urls.value.split(',')]
        success = await self.update_config(interaction.guild_id, {"docs_urls": new_urls}, append=True)
        
        if success:
            await interaction.followup.send("New documentation URLs have been added to the server configuration.", ephemeral=True)
        else:
            await interaction.followup.send("Failed to add new URLs. Please try again.", ephemeral=True)

    @app_commands.command(name="add_tag", description="Add a new tag")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_tag(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        tag_modal = TagDataModal()
        await interaction.followup.send("Add a new tag. Click the button to continue.", view=ModalView(tag_modal), ephemeral=True)
        await tag_modal.wait()
        
        new_tag = {
            "tag_name": tag_modal.tag_name.value,
            "sub_tags": [tag.strip() for tag in tag_modal.sub_tags.value.split(',')],
            "tag_description": tag_modal.tag_description.value
        }
        success = await self.update_config(interaction.guild_id, {"tag_data": [new_tag]}, append=True)
        
        if success:
            await interaction.followup.send("New tag has been added to the server configuration.", ephemeral=True)
        else:
            await interaction.followup.send("Failed to add the new tag. Please try again.", ephemeral=True)

    @app_commands.command(name="fetch_config", description="Fetch the current server configuration")
    @app_commands.checks.has_permissions(administrator=True)
    async def fetch_config(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        config = await self.get_config(interaction.guild_id)
        if config:
            await interaction.followup.send(f"Current server configuration:\n```json\n{json.dumps(config, indent=2)}```", ephemeral=True)
        else:
            await interaction.followup.send("No configuration found for this server.", ephemeral=True)

    async def update_config(self, guild_id, new_config, append=False):
        doc_ref = db.collection('server_config').document(str(guild_id))
        
        try:
            doc = doc_ref.get()
            if doc.exists:
                current_config = doc.to_dict()
                if append:
                    for key, value in new_config.items():
                        if key in current_config:
                            if isinstance(current_config[key], list):
                                current_config[key].extend(value if isinstance(value, list) else [value])
                            elif isinstance(current_config[key], dict):
                                current_config[key].update(value)
                            else:
                                current_config[key] = value
                        else:
                            current_config[key] = value
                else:
                    current_config.update(new_config)
                doc_ref.set(current_config)
            else:
                doc_ref.set(new_config)
            return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False

    async def get_config(self, guild_id):
        doc_ref = db.collection('server_config').document(str(guild_id))
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    @app_commands.command(name="reset", description="Reset the server configuration")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_config(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Create a confirmation view
        view = ConfirmView()
        await interaction.followup.send("Are you sure you want to reset the server configuration? This action cannot be undone.", view=view, ephemeral=True)
        
        # Wait for the user's response
        await view.wait()
        
        if view.value is None:
            await interaction.followup.send("Reset cancelled due to timeout.", ephemeral=True)
        elif view.value:
            success = await self.delete_config(interaction.guild_id)
            if success:
                await interaction.followup.send("Server configuration has been reset. You can now use /configure to set up a new configuration.", ephemeral=True)
            else:
                await interaction.followup.send("Failed to reset server configuration. Please try again.", ephemeral=True)
        else:
            await interaction.followup.send("Reset cancelled.", ephemeral=True)

    async def delete_config(self, guild_id):
        doc_ref = db.collection('server_config').document(str(guild_id))
        try:
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting config: {e}")
            return False
    
    async def ask_continue(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Add Another Tag", style=discord.ButtonStyle.primary, custom_id="continue"))
        view.add_item(discord.ui.Button(label="Finish", style=discord.ButtonStyle.secondary, custom_id="finish"))
        
        message = await interaction.followup.send("Do you want to add another tag?", view=view, ephemeral=True)
        
        try:
            interaction_response = await self.bot.wait_for(
                "interaction",
                check=lambda i: i.user.id == interaction.user.id and i.message.id == message.id,
                timeout=300.0
            )
            await interaction_response.response.defer()
            return interaction_response.data["custom_id"] == "continue"
        except asyncio.TimeoutError:
            await interaction.followup.send("Configuration timed out. Please start over if you wish to continue.", ephemeral=True)
            return False

class ModalView(discord.ui.View):
    def __init__(self, modal):
        super().__init__()
        self.modal = modal

    @discord.ui.button(label='Continue', style=discord.ButtonStyle.primary)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(self.modal)

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = True
        self.stop()

async def setup(bot):
    cog = ServerConfigCog(bot)
    await bot.add_cog(cog)
    await bot.tree.sync()  # Sync the command tree
    print("ServerConfigCog setup complete and commands synced")