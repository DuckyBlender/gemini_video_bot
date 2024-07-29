import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import requests
import time

async def geminivid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gemini 1.5 Flash for the replied video."""
    try:
        # Strip the command
        text = update.message.text.replace("/gvid", "").strip()
        # Get the file ID from the message
        video = update.message.reply_to_message.video
        if video is None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please reply to a video with this command.", reply_to_message_id=update.message.message_id)
            return
        file_id = video.file_id
        size = video.file_size
        # Max 20MB
        if size > 20000000:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"File size is too large ({round(size / 1000000, 2)}MB). Max 20MB.", reply_to_message_id=update.message.message_id)
            return
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        logging.info(f"File ID: {file_id}")
        # Get the file path
        file = await context.bot.get_file(file_id)
        file_path = file.file_path
        # Download the file
        response = requests.get(file_path)
        response.raise_for_status()  # Raise an error for bad status codes
        video_file_name = "video.mp4"
        with open(video_file_name, 'wb') as f:
            f.write(response.content)
        # Upload the video file to the File API
        logging.info(f"Uploading file...")
        video_file = genai.upload_file(path=video_file_name)
        logging.info(f"Completed upload: {video_file.uri}")
        # Wait for the video to be processed
        while video_file.state.name == "PROCESSING":
            logging.info('Waiting for video to be processed.')
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)
        logging.info(f'Video processing complete: {video_file.uri}')
        
        # Make the LLM inference request
        logging.info("Making LLM inference request...")
        response = model.generate_content([text, video_file], safety_settings={
                'HATE': 'BLOCK_NONE',
                'HARASSMENT': 'BLOCK_NONE',
                'SEXUAL': 'BLOCK_NONE',
                'DANGEROUS': 'BLOCK_NONE'
            },
            request_options={"timeout": 600}
        )
        
        # Check if response contains the necessary parts
        if not response.parts:
            feedback = response.prompt_feedback
            raise ValueError(f"No candidates returned in response.parts! Feedback: {feedback}")
        
        logging.info(response.text)
        # Send the response back to the user
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response.text, reply_to_message_id=update.message.message_id)
        # Delete the uploaded file
        genai.delete_file(video_file.name)
        logging.info(f'Deleted file {video_file.uri}')
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="There was an error downloading the video file.", reply_to_message_id=update.message.message_id)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"An unexpected error occurred: {e}", reply_to_message_id=update.message.message_id)


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)

    load_dotenv()

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    system_instruction = "Respond in the users language"
    model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_instruction)
    bot = ApplicationBuilder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()

    start_handler = CommandHandler('gvid', geminivid)
    bot.add_handler(start_handler)

    bot.run_polling()
