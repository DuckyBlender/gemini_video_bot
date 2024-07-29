# Gemini Video Bot

This is a simple Telegram bot that processes video files and generates content using Google's Generative AI. The bot was coded in one hour and is my first Python Telegram bot. I chose Python only because of the available libraries that made the implementation straightforward.

## Features

- Responds to the `/gvid` command.
- Downloads the video file from the replied message.
- Uploads the video to a file processing API.
- Waits for the video to be processed.
- Makes an inference request to a Generative AI model.
- Sends the generated content back to the user.

## Requirements

- Python 3
- Telegram Bot API token
- Google API key for Generative AI

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/DuckyBlender/gemini_video_bot
    cd gemini-video-bot
    ```

2. Create a virtual environment and activate it:

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your API keys:

    ```
    TELEGRAM_BOT_TOKEN=your-telegram-bot-token
    GOOGLE_API_KEY=your-google-api-key
    ```

## Usage

1. Run the bot:

    ```sh
    python3 main.py
    ```

2. In your Telegram app, send a video file to the bot and reply to it with the command `/gvid`.

## Notes

- The bot checks if the video file size is within the 20MB limit.
- It handles errors gracefully and informs the user if something goes wrong during the process.

## Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram Bot API integration.
- [google-generativeai](https://github.com/google/generativeai) for the Generative AI API.

## License

Do whatever you want. I don't care.
