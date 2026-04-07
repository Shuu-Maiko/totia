import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from langchain_core.tools import tool
import discord
from discord.ext import commands
from duckduckgo_search import DDGS

async def getTools(bot: commands.Bot, contextChannel: Optional[discord.abc.Messageable] = None):
    @tool
    async def getCurrentTime() -> str:
        """Get the current date and time."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @tool
    async def searchWeb(query: str) -> str:
        """Search the web for information using DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(None, lambda: list(ddgs.text(query, max_results=3)))
                if not results:
                    return "No results."
                
                output = []
                for r in results:
                    output.append(f"Title: {r['title']}\nSnippet: {r['body']}")
                return "\n\n".join(output)
        except Exception as e:
            return f"Search error: {str(e)}"

    @tool
    async def getUserInfo(userId: str) -> str:
        """Fetch Discord user details (name, join date, ID). Provide user ID to look up."""
        try:
            if not userId:
                return "Please provide a valid numeric userId."
            user = bot.get_user(int(userId)) or await bot.fetch_user(int(userId))
            if not user: return "Not found."
            return f"User: {user.name} (ID: {user.id}), Created: {user.created_at}"
        except Exception as e:
            return f"Error: {str(e)}"

    @tool
    async def getChannelInfo() -> str:
        """Get current channel metadata."""
        if not contextChannel: return "No context."
        return f"Channel: {getattr(contextChannel, 'name', 'DM')} (ID: {contextChannel.id})"

    @tool
    async def getServerInfo() -> str:
        """Get server/guild metadata."""
        if not contextChannel or not hasattr(contextChannel, 'guild') or not contextChannel.guild:
            return "No server context."
        guild = contextChannel.guild
        return f"Server: {guild.name} (ID: {guild.id}, Members: {guild.member_count})"

    @tool
    async def searchChannel(query: str, userId: str = "") -> str:
        """Search recent chat history for keywords or user messages."""
        if not contextChannel: return "No context."
        found = []
        try:
            async for msg in contextChannel.history(limit=50):
                if userId and str(msg.author.id) != str(userId): continue
                if query and query.lower() not in msg.content.lower(): continue
                found.append(f"{msg.author.name}: {msg.clean_content}")
            return "\n".join(found[:10]) if found else "No matches."
        except Exception as e:
            return f"Error: {str(e)}"

    @tool
    async def clearMemory(userId: str) -> str:
        """Clear all stored memories for a specific user."""
        try:
            if hasattr(bot, 'memory'):
                bot.memory.forgetUser(userId)
                return f"Cleared memories for {userId}."
            return "N/A"
        except Exception as e:
            return str(e)

    @tool
    async def searchUrbanDictionary(term: str) -> str:
        """Search Urban Dictionary for the definition of slang, abbreviations, or modern internet terms."""
        try:
            import aiohttp
            url = f"https://api.urbandictionary.com/v0/define?term={term}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        definitions = data.get("list", [])
                        if not definitions:
                            return f"No definition found for '{term}'."
                        # Get the top definition (clean up the brackets UD uses for links)
                        top_def = definitions[0]
                        definition = top_def.get("definition", "").replace("[", "").replace("]", "")
                        example = top_def.get("example", "").replace("[", "").replace("]", "")
                        return f"Definition: {definition}\nExample: {example}"
                    return f"Urban Dictionary API returned status {response.status}."
        except Exception as e:
            return f"Error looking up slang: {str(e)}"

    return [getCurrentTime, searchWeb, getUserInfo, getChannelInfo, getServerInfo, searchChannel, clearMemory, searchUrbanDictionary]
