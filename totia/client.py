from typing import Optional, List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from discord.ext import commands
import discord
import asyncio

from .config import settings
from . import prompts
from .tools import getTools

_PROVIDER_DEFAULTS = {
    "gemini": "gemini-2.0-flash",
    "groq":   "llama-3.3-70b-versatile",
}

# Cache for LLM instances
_llmCache: Dict[str, Any] = {}

def getLlm(provider: str):
    """Factory to build or retrieve cached LLM instances."""
    provider = provider.strip().lower()
    if provider in _llmCache:
        return _llmCache[provider]
    
    model = (settings.LLM_MODEL or _PROVIDER_DEFAULTS.get(provider, "")).strip()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=model,
            api_key=settings.GEMINI_API_KEY,
            temperature=0.85,
            max_output_tokens=800,
        )
    elif provider == "groq":
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model=model,
            api_key=settings.GROQ_API_KEY,
            temperature=0.85,
            max_tokens=800,
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    _llmCache[provider] = llm
    return llm

async def chat(
    prompt: str, 
    bot: commands.Bot, 
    channel: discord.abc.Messageable, 
    memories: str = ""
) -> str:
    """Send a prompt with context. Defaults to Groq, fails over to Gemini on error."""
    
    toolsList = await getTools(bot, contextChannel=channel)
    
    systemContent = prompts.SYSTEM_PROMPT_2
    if memories:
        systemContent += "\n" + prompts.MEMORY_CONTEXT_TEMPLATE.format(memories=memories)

    messages = [
        SystemMessage(content=systemContent),
        HumanMessage(content=prompt),
    ]

    # Try Primary (Groq) then Fallback (Gemini)
    providers = ["groq", "gemini"]
    
    for provider in providers:
        try:
            print(f"[AI] Attempting response with {provider}...")
            llm = getLlm(provider)
            llmWithTools = llm.bind_tools(toolsList)
            
            # Internal tool-calling loop (max 5 iterations)
            tempMessages = list(messages)
            for i in range(5):
                print(f"[AI] {provider} - Thinking... (Iteration {i+1})")
                response = await llmWithTools.ainvoke(tempMessages)
                
                if not getattr(response, 'tool_calls', []):
                    return response.content or "..."

                tempMessages.append(response)
                for toolCall in response.tool_calls:
                    toolName = toolCall["name"].lower()
                    toolArgs = toolCall["args"]
                    selectedTool = next((t for t in toolsList if t.name.lower() == toolName), None)
                    
                    if selectedTool:
                        toolOutput = await selectedTool.ainvoke(toolArgs)
                        tempMessages.append(ToolMessage(content=str(toolOutput), tool_call_id=toolCall["id"]))
                    else:
                        tempMessages.append(ToolMessage(content=f"Error: Tool {toolName} not found.", tool_call_id=toolCall["id"]))
            
            return "Thinking too complex, even for fallback."

        except Exception as e:
            error_str = str(e)
            if "tool_use_failed" in error_str and provider == "groq":
                print(f"[AI RETRY] Groq tool validation hallucinated. Retrying {provider} without tools...")
                try:
                    # Retry cleanly without confusing Llama 3's JSON mapping
                    response = await llm.ainvoke(messages)
                    return response.content or "..."
                except Exception as retryE:
                    print(f"[AI ERROR] {provider} retry failed: {retryE}")

            print(f"[AI ERROR] {provider} failed: {type(e).__name__}: {e}")
            if provider == providers[-1]:
                return f"Total AI failure: {str(e)}"
            print(f"[AI FALLBACK] Switching to next provider...")

    return "No AI providers available."
