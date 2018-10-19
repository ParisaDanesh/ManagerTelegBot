import telegram
from telegram.ext import CallbackQueryHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import RegexHandler
from telegram.ext import Updater, CommandHandler, ConversationHandler
import logging
import datetime
import calendar
# import pymysql as mysql
# import requests as rq

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# class DATABASE:
#     def __init__(self):
#         self._conn = mysql.connect(host="localhost",
#                                    user="user",
#                                    password="password",
#                                    db="books", charset="utf8")

class USER_MSG:
    def __init__(self,chat_id,user_data ):
        self.chat_id = chat_id
        for key, value in user_data.items():
            if(key == 'file'):
                self.audio = str(user_data['file'])+'.mp3'
            if(key == 'msg'):
                self.msg = user_data['msg']
            if(key == 'photo'):
                self.photo = 'photos/' + str(user_data['photo']) + '.jpg'
            else:
                continue

FIRST ,DATE , TIME ,CHOOSING, TYPING_REPLY,DONE= range(6)
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def start(bot,update):
    chat_id = update.message.chat_id
    update.message.reply_text('Hi !!! \n'
    'Use /new to set a new date and time for your message')
    # markup = telegram.ReplyKeyboardRemove()
    # bot.send_message(chat_id, "date Successfully Set",
    #                  reply_markup=markup)
    custom_keyboard = [['/new']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                resize_keyboard=True, one_time_keyboard=True)
    bot.send_message(chat_id=chat_id ,
                     text="lets start with choosing one:",
                     reply_markup= reply_markup)
    return FIRST

current_shown_dates={}
def new(bot,update):
    # update.message.reply_text("choose a date:")
    now = datetime.datetime.now()  # Current date
    chat_id = update.message.chat_id
    date = (now.year, now.month)
    current_shown_dates[chat_id] = date  # Saving the current date in a dict
    markup = create_calendar(now.year, now.month)
    bot.send_message(update.message.chat.id, "Please, choose a date:", reply_markup=markup)

    return DATE

def create_calendar(year,month):
    markup = []
    # First row - Month and Year
    row = []
    row.append(telegram.InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data="ignore"))
    markup.append(row)
    # Second row - Week Days
    week_days = ["M", "T", "W", "R", "F", "S", "U"]
    row = []
    for day in week_days:
        row.append(telegram.InlineKeyboardButton(day, callback_data="ignore"))
    markup.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if (day == 0):
                row.append(telegram.InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                row.append(telegram.InlineKeyboardButton(str(day), callback_data= str(year) +"-"+ str(month) +"-"+ str(day)))
        markup.append(row)
    # Last row - Buttons
    row = []
    row.append(telegram.InlineKeyboardButton("<", callback_data="previous-month"))
    row.append(telegram.InlineKeyboardButton(" ", callback_data="ignore"))
    row.append(telegram.InlineKeyboardButton(">", callback_data="next-month"))
    markup.append(row)
    markup = telegram.InlineKeyboardMarkup(markup)

    return markup

def set_timer(bot, update,user_data):
    # print args[0]
    chat_id = update.message.chat_id
    now = datetime.datetime.now().time()  # Current date
    timer = update.message.text
    print timer
    timeSetString = datetime.datetime.strptime(timer, '%H:%M').time()
    if(now > timeSetString):
        bot.send_message(chat_id, "incorrect,set again:")
    else:
        user_data['time'] = timeSetString

        markup = telegram.ReplyKeyboardRemove()
        bot.send_message(chat_id, "Time Successfully Set",
                         reply_markup=markup)

        custom_keyboard = [['Message','Photo','File'],['Done','/cancel']]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                    resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(chat_id=chat_id,
                         text="Now,Choose One Below: ",
                         reply_markup=reply_markup)


        return CHOOSING


def button(bot, update, user_data):
    query = update.callback_query
    msg_id = query.inline_message_id
    # print "here!"
    if(query.data== "next-month"):
        # print "here!"
        chat_id = query.message.chat_id
        saved_date = current_shown_dates.get(chat_id)
        if (saved_date is not None):
            year, month = saved_date
            month += 1
            if month > 12:
                month = 1
                year += 1
            date = (year, month)
            current_shown_dates[chat_id] = date
            markup = create_calendar(year, month)
            bot.edit_message_text("Please, choose a date:", query.from_user.id, query.message.message_id,
                                  reply_markup=markup)
            # bot.answer_callback_query(query.id, text="")
        else:
            # Do something to inform of the error
            pass

    if(query.data == "previous-month"):

        chat_id = query.message.chat.id
        saved_date = current_shown_dates.get(chat_id)
        if (saved_date is not None):
            year, month = saved_date
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            date = (year, month)
            current_shown_dates[chat_id] = date
            markup = create_calendar(year, month)
            bot.edit_message_text("Please, choose a date", query.from_user.id, query.message.message_id,
                                  reply_markup=markup)
            # bot.answer_callback_query(query.id, text="")
        else:
            # Do something to inform of the error
            pass

    if(query.data == "ignore"):
        pass
    if(query.data != "previous-month" and query.data != "next-month" and query.data != "ignore"):
        # bot.editMessageText(text="Selected: %s" %query.data,
        #                     chat_id=query.message.chat_id,
        #                     message_id=query.message.message_id)
        now = datetime.datetime.now()
        tmp = datetime.datetime.strptime(query.data, "%Y-%m-%d")
        # print now>tmp
        if(now.day > tmp.day or now.month > tmp.month or now.year > tmp.year):
            chat_id = query.message.chat_id
            date = (now.year, now.month)
            current_shown_dates[chat_id] = date  # Saving the current date in a dict
            markup = create_calendar(now.year, now.month)
            bot.edit_message_text("incorrect,please choose a date again:", query.from_user.id, query.message.message_id,
                                  reply_markup=markup)
        else:
            # print "here"
            chat_id = query.message.chat_id
            user_data['date'] = tmp
            # print user_data['job']
            custom_keyboard = [['/cancel']]
            new_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                      resize_keyboard=True)
            markup = telegram.ReplyKeyboardRemove()
            bot.send_message(chat_id, "date Successfully Set",
                             reply_markup=markup)
            bot.send_message(chat_id=chat_id,
                             text="now enter time in <Hour:Min> format :",
                             reply_markup=new_markup)
            # set_timer(bot, update, query.data)
            # print "here"
            return TIME

def alarm(bot, job):
    """Send the alarm message."""
    print
    if(job.context.msg):
        bot.send_message(chat_id=job.context.chat_id, text=job.context.msg)
    elif(job.context.photo):
        bot.send_photo(chat_id=job.context.chat_id, photo=open(job.context.photo))
    elif(job.context.audio):
        print "here"
        bot.send_audio(chat_id=job.context.chat_id, audio=open(job.context.audio , 'rb'))
        print "2"

def done(bot, update, job_queue,user_data):
    chat_id = update.message.chat_id
    bot.send_message(chat_id,text="Done! All Thing Successfully Set!!!")

    finalDate = datetime.datetime.combine(user_data['date'],user_data['time'])
    # user_data['finalDate'] = finalDate
    # print finalDate
    print user_data
    channel_id = "@parikhodam"
    # tmp = USER_MSG(channel_id, user_data['msg'], user_data['photo'])
    tmp = USER_MSG(channel_id, user_data)
    job = job_queue.run_once(alarm, finalDate, context=tmp)

    markup = telegram.ReplyKeyboardRemove()
    bot.send_message(update.message.chat_id, "Thank You!",
                     reply_markup=markup)
    custom_keyboard = [['/new']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                resize_keyboard=True, one_time_keyboard=True)

    update.message.reply_text('You Can Start New Job', reply_markup=reply_markup)
    user_data.clear()

    return ConversationHandler.END

def cancel(bot, update, user_data):
    user = update.message.from_user

    markup = telegram.ReplyKeyboardRemove()
    bot.send_message(update.message.chat_id, "Bye!",
                     reply_markup=markup)
    custom_keyboard = [['/new']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                resize_keyboard=True, one_time_keyboard=True)
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('You Can Start New Job',reply_markup=reply_markup)
    user_data.clear()

    return ConversationHandler.END
#
# def test(bot, update, user_data):
#     print user_data
#     bot.send_message(update.message.chat.id , user_data)

def custom_choice(bot,update,user_data):
    text = update.message.text
    user_data['choice'] = text
    # print "choice :", user_data['choice']
    update.message.reply_text(
        'OK! Please Send Me Your '+user_data['choice']+ ' :')

    # if(text == 'Photo'):
    #
    # if(text == 'Message'):
    #     chat_id = update.message.chat_id
    #     bot.send_message(chat_id, text="Enter Your Yext")
    #     msg = update.message.text
    #     user_data['msg'] = msg
    #     chat_id = update.message.chat_id
    # if(text == 'File'):

    return TYPING_REPLY

def received_info(bot,update, user_data):
    # print "here!vorood"
    # print user_data['choice']
    chat_id = update.message.chat_id
    if(user_data['choice'] == 'Message'):
        msg = update.message.text
        print msg
        user_data['msg'] = msg
        bot.send_message(chat_id, text="Done! Your Msg Successfully Set!!!"
                                       "Press Done If You Dont Want To Send Anything Else...")
        del user_data['choice']
    elif(user_data['choice'] == 'Photo'):
        user = update.message.from_user
        photo_file = bot.getFile(update.message.photo[-1].file_id)
        photo_file.download('photos/'+str(chat_id)+'.jpg')
        user_data['photo'] = chat_id
        # print user_data['photo']
        logger.info("Photo of %s: %s" % (user.first_name, 'user_photo.jpg'))
        update.message.reply_text('Done! Your Photo Successfully Set!!!'
                                  "Press Done If You Dont Want To Send Anything Else...")
        del user_data['choice']

    elif(user_data['choice'] == 'File'):
        user = update.message.from_user
        photo_file = bot.getFile(update.message.audio.file_id)
        photo_file.download(str(chat_id)+'.mp3')
        user_data['file'] = chat_id
        # print user_data['photo']
        logger.info("Photo of %s: %s" % (user.first_name, 'test.mp3'))
        update.message.reply_text('Done! Your File Successfully Set!!!'
                                  "Press Done If You Dont Want To Send Anything Else...")
        del user_data['choice']

    return CHOOSING
    # elif(user_data['choice'] == 'File'):

def main():
    """Run bot."""
    updater = Updater("496106179:AAEgVYII3-E09AQvA-_7jbR399zuvwr1sTU", request_kwargs={
        'proxy_url': 'socks5://127.0.0.1:9050/'
    })

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("new", new))
    # dp.add_handler(CommandHandler("set", test,pass_user_data=True))
    # dp.add_handler(CallbackQueryHandler(button))
    # dp.add_handler(CommandHandler("test",test,pass_user_data=True))


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('new',new)],

        states={
            # FIRST: [CommandHandler('new',new)],
            DATE: [CallbackQueryHandler(button,pass_user_data=True)],
            TIME: [MessageHandler(Filters.text, set_timer ,pass_user_data=True)],
            # MESSAGE: [MessageHandler(Filters.text, getMessage ,pass_job_queue=True,pass_user_data=True)]
            CHOOSING: [RegexHandler('^(Message|Photo|File)$',
                                    custom_choice,
                                    pass_user_data=True)
                       ],
            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_info,
                                          pass_user_data=True),
                           MessageHandler(Filters.photo,
                                          received_info,
                                          pass_user_data=True),
                           MessageHandler(Filters.audio,
                                          received_info,
                                          pass_user_data=True),
                           ],
        },
        fallbacks=[RegexHandler('^Done$',
                                    done,pass_job_queue=True,
                                pass_user_data=True),
                   CommandHandler('cancel',
                                  cancel,pass_user_data=True)
                   ]
    )

    updater.dispatcher.add_handler(conv_handler)

    # dp.add_handler(CommandHandler('test',test,pass_user_data=True))
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