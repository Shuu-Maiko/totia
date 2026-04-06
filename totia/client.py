from typing import Optional, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from discord.ext import commands
import discord

from .config import settings
from . import prompts
from .tools import getTools

_PROVIDER_DEFAULTS = {
    "gemini": "gemini-2.5-flash",
    "groq":   "llama-3.3-70b-versatile",
}

def _buildLlm():
    provider = settings.LLM_PROVIDER.lower()
    model = settings.LLM_MODEL or _PROVIDER_DEFAULTS.get(provider, "")

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            api_key=settings.GEMINI_API_KEY,
            temperature=0.8,
            max_output_tokens=800,
        )
    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model,
            api_key=settings.GROQ_API_KEY,
            temperature=0.8,
            max_tokens=800,
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: '{provider}'")

llm = _buildLlm()

async def chat(
    prompt: str, 
    bot: commands.Bot, 
    channel: discord.abc.Messageable, 
    memories: str = ""
) -> str:
    """Send a prompt with context and return an AI response using tools."""
    
    toolsList = await getTools(bot, contextChannel=channel)
    llmWithTools = llm.bind_tools(toolsList)
    
    systemContent = prompts.SYSTEM_PROMPT_2
    if memories:
        systemContent += "\n" + prompts.MEMORY_CONTEXT_TEMPLATE.format(memories=memories)

    messages = [
        SystemMessage(content=systemContent),
        HumanMessage(content=prompt),
    ]

    for _ in range(5):
        try:
            response = await llmWithTools.ainvoke(messages)
            
            if not getattr(response, 'tool_calls', []):
                return response.content or "I don't have anything to say."

            messages.append(response)

            for toolCall in response.tool_calls:
                toolName = toolCall["name"].lower()
                toolArgs = toolCall["args"]
                selectedTool = next((t for t in toolsList if t.name.lower() == toolName), None)
                
                if selectedTool:
                    toolOutput = await selectedTool.ainvoke(toolArgs)
                    messages.append(ToolMessage(content=str(toolOutput), tool_call_id=toolCall["id"]))
                else:
                    messages.append(ToolMessage(content=f"Error: {toolName} not found.", tool_call_id=toolCall["id"]))
                    
        except Exception as e:
            return f"Thinking error: {str(e)}"

    return "Thinking too complex, cancelling."
