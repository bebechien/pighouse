import os
import telegram, asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the actual token obtained from the BotF
ather
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'  # Replace with the chat ID of the user/group/chan
nel you want to send messages to

# Replace 'YOUR_FOLDER_PATH' with the path of the specific folder you want to mo
nitor
FOLDER_TO_WATCH = 'YOUR_FOLDER_PATH'

# Function to send a message via Telegram
async def send_telegram_message(text, photo_obj):
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=photo_obj, caption=text
)

# Watchdog event handler for handling file system events
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith("png"):
          new_file_path = event.src_path
          file_name = os.path.basename(new_file_path)
          message_text = f"New file added: {file_name}"
          asyncio.run(send_telegram_message(message_text, open(new_file_path, 'r
b')))

# Main function to start monitoring the folder
def main():
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=FOLDER_TO_WATCH, recursive=False)
    observer.start()

    try:
        print(f"Monitoring folder: {FOLDER_TO_WATCH}")
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
