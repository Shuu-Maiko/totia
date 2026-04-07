import discord
from discord.ext import commands
import asyncio
import aiohttp
from aiohttp import web
import logging

from .history import history
from .config import settings
from . import client
from .memory import MemoryStore

class TotiaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='+', intents=intents)
        
        self.memory = MemoryStore(
            persistDirectory=settings.MEMORY_DIR,
            collectionName="discord_memories", 
        )


    async def runKeepAlive(self):
        """Periodically pings the bot's own URL to prevent Render from spinning down."""
        placeholder = "https://your-bot-name.onrender.com"
        if not settings.RENDER_URL or settings.RENDER_URL == placeholder:
            return
        
        # Wait for bot setup to stabilize
        await asyncio.sleep(60)
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(settings.RENDER_URL) as r:
                        if r.status == 200:
                            print(f"[KEEP-ALIVE] Ping to {settings.RENDER_URL} successful.")
                        else:
                            print(f"[KEEP-ALIVE] Warning: unexpected status {r.status} for {settings.RENDER_URL}")
                except Exception as e:
                    print(f"[KEEP-ALIVE] Error: {e}")
                
                # Ping every 10 minutes (safety margin for Render's 15-min limit)
                await asyncio.sleep(600)

    async def setup_hook(self):
        """Called before the bot logs in, perfect for starting background tasks instantly."""
        self.loop.create_task(self.runKeepAlive())
        await self.load_extension("totia.cogs.general")

    async def on_ready(self):
        print(f"Logged in as {self.user.name if self.user else 'iwbot'}")

    async def on_message(self, message: discord.Message):
        if not self.user or message.author == self.user: 
            return 

        isCorrectChannel = message.channel.id == settings.CHANNEL_ID
        isBot = message.author.bot 
        isWebhook = message.webhook_id
        isReplyToOthers = (
            message.reference and 
            message.reference.resolved and 
            isinstance(message.reference.resolved, discord.Message) and
            message.reference.resolved.author.id != self.user.id
        )

        if not isCorrectChannel or isBot or isWebhook or isReplyToOthers:
            return 
        
        print(f"[BOT] Message received from {message.author.display_name}: {message.clean_content}")
        await self.process_commands(message)

        if message.content.startswith(self.command_prefix):
            return

        try:
            async with message.channel.typing():
                cleanedMessage = message.clean_content
                userId = str(message.author.id)
                
                recalledList = []
                try:
                    print(f"[BOT] Recalling memory for {userId}...")
                    recalledList = await self.memory.arecall(
                        userId=userId, 
                        query=cleanedMessage, 
                        topK=settings.MEMORY_TOP_K, 
                        minScore=settings.MEMORY_MIN_SCORE
                    )
                    print(f"[BOT] Found {len(recalledList)} memories.")
                except Exception as memErr:
                    print(f"[BOT] [MEMORY ERROR] Proceeding without historical context: {type(memErr).__name__} - {memErr}")
                
                memoriesText = "\n- ".join(recalledList) if recalledList else ""

                import datetime
                now_time = datetime.datetime.now().strftime("%h %d, %I:%M %p")
                prompt = f"Current Time: {now_time}\n" \
                         f"last 20 chats: {history.getHistory()}\n" \
                         f"the new message: {message.author.display_name}: {cleanedMessage}"

                finalResponse = await client.chat(
                    prompt=prompt, 
                    bot=self, 
                    channel=message.channel, 
                    memories=memoriesText
                )

                history.remember(message.author.display_name, cleanedMessage)
                bot_name = message.guild.me.display_name if message.guild else self.user.name
                history.remember(bot_name, finalResponse)
                
                try:
                    await self.memory.astore(
                        userId, 
                        message.author.display_name, 
                        f"User ({message.author.display_name}): {cleanedMessage}\nBot: {finalResponse}"
                    )
                except Exception as memSaveErr:
                    print(f"[BOT] [MEMORY ERROR] Failed to save interaction: {type(memSaveErr).__name__} - {memSaveErr}")

            await message.reply(finalResponse)
        except Exception as msgError:
            print(f"\n[CRITICAL BOT ERROR] Pipeline crashed on message '{cleanedMessage}': {type(msgError).__name__} - {msgError}\n")


    async def on_member_join(self, member):
        await member.send(f"Welcome to the server {member.name}")

    def runBot(self):
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        super().run(settings.DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)
