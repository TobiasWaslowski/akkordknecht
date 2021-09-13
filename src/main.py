from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, MessageHandler, Filters
import ug_data_retriever
import os
import pdf_writer
from search_step import SearchStep

# Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
print(os.environ['telegram_token'])
updater = Updater(token=os.environ['telegram_token'], use_context=True)
dispatcher = updater.dispatcher

# globals to keep the state
# temp_response maintains the current selection of songs
current_songs = []
current_song_metadata = {}
current_song_body = ''
# search_step can be one of the following: '' (initiate search), 'PICKING', 'PREVIEWING', 'TRANSPOSING'
search_step = SearchStep.IDLE


def start_handler(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, ich bin der Akkordknecht!\n")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Du kannst mit /find [songname] die Suche starten."
                                                                    "Probier's doch einfach mal aus!")
    logging.info("Started chat %d", update.effective_chat.id)


def find_handler(update, context):
    global search_step
    global current_songs
    query = ' '.join(context.args)
    songs = ug_data_retriever.get_search_results_for_song_name(query)
    current_songs = songs
    display_song_choices(context, update)


def display_song_choices(context, update):
    global search_step
    response = "I found the following songs: \n"
    response += _stringify_songs(current_songs)
    response += "Which ones would you like? Choose or (c)ancel."
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    search_step = SearchStep.PICKING


def help_handler(update, context):
    help_text = 'You can use the following commands: \n'
    help_text += '/start to start this conversation \n'
    help_text += '/find [songname] to search \n'
    help_text += 'Also, I\'m open source! Check out my Github Repo at ... \n'
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


def message_handler(update, context):
    logging.debug(search_step == search_step.PICKING)
    if search_step == SearchStep.IDLE:
        pass
    if search_step == SearchStep.PICKING:
        handle_pick(update, context)
    elif search_step == SearchStep.PREVIEWING:
        handle_preview(update, context)
    elif search_step == SearchStep.TRANSPOSING:
        handle_preview(update, context)


def handle_pick(update, context):
    global current_song_body, current_song_metadata
    prompt = update.message.text
    logging.info("PICKING step: processing pick\n")
    if prompt == 'c' or prompt == 'cancel':
        cancel(context, update)
    elif is_valid_integer(prompt):
        current_song_metadata = current_songs[int(prompt)]
        current_song_body = ug_data_retriever.get_song_by_url(current_song_metadata['url'])
        preview_song(update, context, current_song_body)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Your pick was not recognized. Please try again.")


def preview_song(update, context, song_body):
    global search_step
    response = "This is what this song looks like: \n"
    for line in song_body[:7]:
        response += line + "\n"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=response)
    response = "Do you want to have the song like this?\n"
    response += "(Y)es, (N)o, (T)ranspose, (O)ther options"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=response)
    search_step = SearchStep.PREVIEWING


def handle_preview(update, context):
    global search_step
    prompt = update.message.text.lower()
    if prompt == 'y' or prompt == 'yes':
        send_song(update, context, current_song_metadata, current_song_body)
    elif prompt == 'n' or prompt == 'no':
        cancel(context, update)
    elif prompt == 'o' or prompt == 'other':
        search_step = SearchStep.PICKING
        display_song_choices(context, update)
    elif prompt == 't' or prompt == 'transpose':
        # search_step = SearchStep.TRANSPOSING
        handle_transposition(update, context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sorry, I didn't quite get that.")


def handle_transposition(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, transposition isn't implemented yet. Check back in a while ;)")
    preview_song(update, context, current_song_body)


def send_song(update, context, song_metadata, song_body):
    pdf = pdf_writer.write_song(song_metadata, song_body).encode('latin-1')
    song_title = song_metadata['title'] + '.pdf'
    context.bot.send_document(chat_id=update.effective_chat.id, filename=song_title, document=pdf)


def cancel(context, update):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Alright, just pick a new song :)")
    reset()


def reset():
    global search_step, current_songs, current_song_metadata, current_song_body
    search_step = SearchStep.IDLE
    current_songs = []
    current_song_metadata = {}
    current_song_body = ''


def is_valid_integer(s):
    try:
        i = int(s)
        return i < 5
    except ValueError:
        return False


def _stringify_songs(search_results):
    response = ""
    for x in range(len(search_results)):
        response += f"({x}) {search_results[x]['artist']}: "
        response += f"{search_results[x]['title']} | "
        response += f"Votes: {search_results[x]['votes']}\n"
    return response


dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('find', find_handler))
dispatcher.add_handler(CommandHandler('help', help_handler))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), message_handler))

updater.start_polling()
