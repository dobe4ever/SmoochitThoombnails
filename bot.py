import os
from telegram import Bot, Update
from telegram.ext import Filters, MessageHandler, Updater
from keep_alive import keep_alive_ping, keep_alive
import threading
from gpt import run_conversation
from auto_thoombnail import crop_edges

keep_alive_ping()

bot_token = os.environ['BOT_TOKEN']
H = int(os.environ['HEL_ID'])
T = int(os.environ['TROY_ID'])
bot = Bot(token=bot_token)


def handle_text(update: Update, context):  
    userid=update.message.from_user.id
    text=update.message.text
    if userid not in {H, T}: return

    resp=run_conversation(userid, text)    
    if resp is not None:
        bot.send_message(chat_id=userid, text=resp)


def get_photo(update: Update, context):
    userid=update.message.from_user.id
    if userid not in {H, T}: return

    file_id = update.message.photo[-1].file_id
    file = context.bot.get_file(file_id)
    # Get file extension from the file_path
    extension = file.file_path.split('.')[-1]
    # download file
    file.download(f"uploads/photo.{extension}") 

    # Crop the image & overwrite the original one with the cropped one
    crop_edges(f"uploads/photo.{extension}")

    resp = run_conversation(userid, "Here's the image: uploads/photo.jpg")
    bot.send_message(chat_id=userid, text=resp)


def main():
    updater = Updater(token=bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.photo, get_photo))
    dp.add_handler(MessageHandler(Filters.text, handle_text))

    updater.start_polling()

    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    updater.idle()
    updater.stop()

if __name__ == '__main__':
    main()

### BOT ACTIONS ###
#UPLOAD_PHOTO UPLOAD_AUDIO UPLOAD_DOCUMENT
#TYPING RECORD_AUDIO RECORD_VIDEO