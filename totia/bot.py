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

    async def setupHttpServer(self):
        """Standard HTTP health check listener for Render's free tier."""
        app = web.Application()
        app.router.add_get("/", lambda r: web.Response(text="OK"))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", settings.PORT)
        await site.start()
        print(f"[HTTP] Health check server active on port {settings.PORT}")

    async def runKeepAlive(self):
        """Periodically pings the bot's own URL to prevent Render from spinning down."""
        if not settings.RENDER_URL:
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

    async def on_ready(self):
        print(f"Logged in as {self.user.name if self.user else 'iwbot'}")
        await self.load_extension("totia.cogs.general")
        
        # Start Render-specific tasks
        self.loop.create_task(self.setupHttpServer())
        self.loop.create_task(self.runKeepAlive())

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
        
        await self.process_commands(message)

        if message.content.startswith(self.command_prefix):
            return

        async with message.channel.typing():
            cleanedMessage = message.clean_content
            userId = str(message.author.id)
            
            recalledList = self.memory.recall(
                userId=userId, 
                query=cleanedMessage, 
                topK=settings.MEMORY_TOP_K, 
                minScore=settings.MEMORY_MIN_SCORE
            )
            
            memoriesText = "\n- ".join(recalledList) if recalledList else ""

            prompt = f"last 20 chats: {history.get_history()}\n" \
                     f"the new message: {message.author.name}: {cleanedMessage}"

            finalResponse = await client.chat(
                prompt=prompt, 
                bot=self, 
                channel=message.channel, 
                memories=memoriesText
            )

            history.remember(message.author.name, cleanedMessage)
            history.remember(self.user.name, finalResponse)
            
            self.memory.store(
                userId, 
                message.author.name, 
                f"User ({message.author.name}): {cleanedMessage}\nBot: {finalResponse}"
            )

        await message.reply(finalResponse)

    async def on_member_join(self, member):
        await member.send(f"Welcome to the server {member.name}")

    def runBot(self):
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        super().run(settings.DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)
