import discord
from discord.ext import commands
import logging

from .history import history
from .config import settings
from . import client


class TotiaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='+', intents=intents)
        self.gemini_chat = client.get_gemini_chat()

    async def on_ready(self):
        print(f"Logged in as {self.user.name if self.user else 'iwbot'}")
        await self.load_extension("totia.cogs.general")

    async def on_message(self, message):
        if(self.user == None): 
            return 

        selfMessage = message.author == self.user 
        notCorrectChannel = message.channel.id != settings.CHANNEL_ID
        messageIsFromBot = message.author.bot 
        repliedToOtherUser = message.reference and message.reference.resolved and message.reference.resolved.author.id != (self.user and self.user.id)
        repliedToOtherUser = (
            message.reference and 
            message.reference.resolved and 
            message.reference.resolved.author.id != self.user.id
        )
        isWebhook = message.webhook_id

        if(any((selfMessage,notCorrectChannel,messageIsFromBot,repliedToOtherUser, isWebhook))):
            return 
        
        await self.process_commands(message)

        if message.content.startswith(self.command_prefix):
            return

        async with message.channel.typing():
            cleanedMessage = message.clean_content
            prompt = f'''
                last 20 chats : {history.get_history()}
                the new message : { message.author.name } : {cleanedMessage}
            '''
            print(prompt)
            response = self.gemini_chat.send_message(prompt)
            history.remember(message.author.name , cleanedMessage)
            history.remember(self.user.name , response.text)

        await message.reply(response.text)

    async def on_member_join(self, member):
        await member.send(f"Welcome to the server {member.name}")

    def run_bot(self):
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        super().run(settings.DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)
