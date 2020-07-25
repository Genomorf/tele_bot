import telebot
import subprocess

bot = telebot.TeleBot("1158344914:AAELM03sIzd9b-pWnA0pbr7V2ForhmwbRSc")

@bot.message_handler(commands=["log"])
def send_welcome(message):
        result = subprocess.run(['journalctl', '-u', 'tgbot.service'], stdout=subprocess.PIPE, text=True)
        bot.reply_to(message, result)
bot.polling()
