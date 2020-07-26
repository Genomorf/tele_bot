import telebot
import subprocess

bot = telebot.TeleBot("1158344914:AAELM03sIzd9b-pWnA0pbr7V2ForhmwbRSc")


def send_to_log(message, log_name):
    log=''
    with open(f'/home/gena/tele_bot/logs/{log_name}', 'r') as F:
        for string in F:
            log += string
    for i in range(0, len(log), 200):
        if len(log) - i < 200:
            bot.reply_to(message, log[i:len(log)])
        else:
            bot.reply_to(message, log[i:i+100])


@bot.message_handler(commands=["sd_log"])
def send_welcome(message):
    send_to_log(message, "app_sd.log")


@bot.message_handler(commands=["err_log"])
def send_welcome(message):
    send_to_log(message, "ap_err.log")


@bot.message_handler(commands=["log"])
def send_welcome(message):
    send_to_log(message, "bot.log")


@bot.message_handler(commands=["process"])
def send_welcome(message):
    result = subprocess.run(['superviserctl', 'status', 'tele_bot'], stdout=subprocess.PIPE)
    bot.reply_to(message, result.stdout)


bot.polling()


