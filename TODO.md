# AI Chat-Oriented Modifications for Totia Discord Bot

This document outlines suggested modifications focused on enhancing the bot's AI chat capabilities and personality within a Discord channel context.

## TODO List

- [ ] **Enhanced Context Management:**
    - [ ] Implement a strategy to periodically summarize older parts of the channel conversation to retain key information without exceeding token limits.
    - [ ] Allow configuration of the number of recent messages or token count the bot should remember for the channel's context.
    - [ ] Differentiate between users in a channel, maintaining individual user conversation context while allowing for shared channel context.

- [ ] **"Forget" or "Clear Context" Command:**
    - [ ] Add a command (e.g., `+forget` or `+clear_context`) that allows an authorized user to reset the channel's current `gemini_chat` session, effectively clearing its memory for a fresh start.

- [ ] **Dynamic Personality Switching:**
    - [ ] Implement a command (e.g., `+set_persona Astra` or `+set_persona Totia`) to dynamically change the bot's system instruction (and thus its personality) for the entire channel.

- [ ] **Proactive Channel Engagement:**
    - [ ] Develop a feature for the bot to periodically post conversation starters, interesting facts, or open-ended questions to encourage discussion within the channel.

- [ ] **AI Image Generation:**
    - [ ] Integrate Gemini's image generation capabilities, adding a command like `+imagine <description>` for users to generate images based on text prompts.

- [ ] **External Persona Configuration:**
    - [ ] Refactor the bot to load detailed persona attributes (name, age, hobbies, etc.) from an external configuration file (e.g., `config.json`) instead of hardcoding them in `totia/prompts.py`.
