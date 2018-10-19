# updater = Updater("496106179:AAEgVYII3-E09AQvA-_7jbR399zuvwr1sTU")
from telegram.ext import Updater, CommandHandler
import logging
import datetime
import calendar
# from telebot import types
import telebot
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi! Use /set <day> :{ \n0->Monday \n'
                                                    '1->Tuesday \n'
                                                    '2->Wendsday \n'
                                                    '3->Thursday \n'
                                                    '4->Friday \n'
                                                    '5->Saturday \n'
                                                    '6->Sunday  }\n'
                              '<Hour:Min> <your msg> to set a timer')

class USER_MSG:
    def __init__(self,chat_id,msg = None):
        self.chat_id = chat_id
        self.msg = msg
        # self.timer = datetime.datetime.strptime(timer,'%H:%M').time()

def alarm(bot, job):
    """Send the alarm message."""
    bot.send_message(chat_id=job.context.chat_id, text=job.context.msg)


current_shown_dates={}
def set_timer(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = "@parikhodam"

    now = datetime.datetime.now()  # Current date
    chat_id = update.chat.id
    date = (now.year, now.month)
    current_shown_dates[chat_id] = date  # Saving the current date in a dict
    markup = create_calendar(now.year, now.month)
    bot.send_message(update.chat.id, "Please, choose a date", reply_markup=markup)

    try:
        # args[0] should contain the time for the timer in seconds
        # due = int(args[0])
        # # update.message.reply_text(args[1])
        # if due < 0:
        #     update.message.reply_text('Sorry we can not go back to future!')
        #     return

        # Add job to queue
        timer = datetime.datetime.strptime(args[1],'%H:%M').time()
        day = int(args[0])

        msg = ""
        for i in range(2,len(args)):
            msg = msg+" "+args[i]
        tmp = USER_MSG(chat_id,msg)

        job = job_queue.run_daily(alarm, time=timer,days=(day,),context=tmp)

        update.message.reply_text('Timer successfully set! for user ')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(bot, update, chat_data):
    """Remove the job if the user changed their mind."""
    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def create_calendar(year,month):
    types = telebot.types
    markup = types.InlineKeyboardMarkup()
    #First row - Month and Year
    row=[]
    row.append(types.InlineKeyboardButton(calendar.month_name[month]+" "+str(year),callback_data="ignore"))
    markup.row(*row)
    #Second row - Week Days
    week_days=["M","T","W","R","F","S","U"]
    row=[]
    for day in week_days:
        row.append(types.InlineKeyboardButton(day,callback_data="ignore"))
    markup.row(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row=[]
        for day in week:
            if(day==0):
                row.append(types.InlineKeyboardButton(" ",callback_data="ignore"))
            else:
                row.append(types.InlineKeyboardButton(str(day),callback_data="calendar-day-"+str(day)))
        markup.row(*row)
    #Last row - Buttons
    row=[]
    row.append(types.InlineKeyboardButton("<",callback_data="previous-month"))
    row.append(types.InlineKeyboardButton(" ",callback_data="ignore"))
    row.append(types.InlineKeyboardButton(">",callback_data="next-month"))
    markup.row(*row)
    return markup


def main():
    """Run bot."""
    updater = Updater("496106179:AAEgVYII3-E09AQvA-_7jbR399zuvwr1sTU")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()