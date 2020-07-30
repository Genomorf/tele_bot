# -*- coding: utf-8 -*-
import threading
import cherrypy
import tg_module
import vk_module
import log_module
import time


# threading processes
# first thread is vk longpoll listner
t1 = threading.Thread(target=vk_module.listen)
t1.start()
log_module.logging.info("Vk longpoll started")
 # handler for user commands from telegram         
@tg_module.bot.message_handler(commands=['check'])
def send_check_message(message):
    if threading.Thread.is_alive(t1):
        tg_module.bot.send_message(chat_id=tg_module.CHAT_ID, text='OK')
    else:
        tg_module.bot.send_message(chat_id=tg_module.CHAT_ID, text='dead :(')
      
# second thread is telegram handler
t2 = threading.Thread(target=tg_module.Webhook_listen)
t2.start()
log_module.logging.info("Telegram webhook started")

# while true loop to ignore crashes
while True:
    try:
        time.sleep(60)
        if not(threading.Thread.is_alive(t1)):
            t1 = threading.Thread(target=vk_module.listen)
            t1.start()
            log_module.logging.info('Vk longpoll have started from the loop')
    except Exception as e:
        log_module.logging.exception(f'Couldn\'t start Vk lonpoll from the loop with: \n {e}')
    try:
        time.sleep(60)
        if not(threading.Thread.is_alive(t2)):
            print(threading.Thread.is_alive(t2))
            t2 = threading.Thread(target=tg_module.Webhook_listen)
            t2.start()
            print('Telegram webhook have started from the loop')
    except Exception as e:
        log_module.logging.exception(f'Couldn\'t start telegram webhook from the loop with: \n {e}')


