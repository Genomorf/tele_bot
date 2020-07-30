import telebot
import subprocess
from telebot import util
bot = telebot.TeleBot("1158344914:AAELM03sIzd9b-pWnA0pbr7V2ForhmwbRSc")



def send_to_log(message1, log_name):
    large_text = open(f'/home/gena/tele_bot/logs/{log_name}', "rb").read()
    splitted_text = util.split_string(large_text, 3000)
    for text in splitted_text:
	    bot.reply_to(message1, "start: ' + str(text))



@bot.message_handler(commands=["log"])
def send_welcome(message):
    send_to_log(message, "bot.log")

@bot.message_handler(commands=["restart"])
def restart_bot(message):
    res = subprocess.run(["sudo", "systemctl","restart","tgbot"], stdout=subprocess.PIPE)
    res1 = 'stdout: '
    bot.reply_to(message,res1 + str(res.stdout))

@bot.message_handler(commands=["status"])
def status_bot(message):
    res = subprocess.run(["sudo", "systemctl", "status", "tgbot"], stdout=subprocess.PIPE)
    res1 = 'status: '
    bot.reply_to(message,res1 + str(res.stdout))
			
@bot.message_handler(commands=["journal"])
def status_bot(message):
    res = subprocess.run(["sudo", "journalctl", "-u", "tgbot.service"], stdout=subprocess.PIPE)
    res1 = 'status: '
    bot.reply_to(message,res1 + str(res.stdout))
bot.polling()
