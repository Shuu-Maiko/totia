# Totia Discord Bot

A simple Discord bot that uses Google's Gemini AI to interact with users in a specific channel.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Shuu-Maiko/totia.git 
    cd totia
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**

    Create a `.env` file in the root of the project by copying the example file:
    ```bash
    cp .env.example .env
    ```

    Now, open the `.env` file and add your specific credentials:

    -   `DISCORD_TOKEN`: Your Discord bot token.
    -   `CHANNEL_ID`: The ID of the channel you want the bot to be active in.
    -   `GEMINI_API_KEY`: Your Google Generative AI API key.

## Usage

Once you have completed the setup, you can run the bot with the following command:

```bash
python3 -m totia
```
