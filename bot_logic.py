# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import telebot
from datetime import datetime
import threading
import logging
import time
import cherrypy
import requests
import bs4

# CONSTANTS
DAMN = "197381393" # for test
VEG = "139197081" # for prod
GROUP_ID = VEG
CHAT_ID = "-499017057"
TOKEN_DAMN = "fdf63f1dae61a44e0a285c4c5e977041a38fb1ac98445f835879c49fb3f7513089320970689db9ebd6da2" # for test
TOKEN_VEG = "ed7f1b64be582e8a81a824b0a5572d9b65f336aa726c58915583419ebfa66c47e004f191d4201ae24f8f5" # for prod

# telegram auth
bot = telebot.TeleBot("721671579:AAFR4Fpn-xkJnyr8cDunU9fXRvCE7QsNlB8", threaded=True)

# vk auth
vk_session = vk_api.VkApi(token=TOKEN_VEG)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# WEBHOOK
WEBHOOK_HOST = '83.220.175.88'
WEBHOOK_PORT = 443 # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше
WEBHOOK_SSL_CERT = '../webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = '../webhook_pkey.pem'  # Путь к приватному ключу
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % ("721671579:AAFR4Fpn-xkJnyr8cDunU9fXRvCE7QsNlB8")

# logger 
logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    filename='/home/gena/tele_bot/logs/bot.log', level=logging.INFO)

# cherrypy server
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)
            
# check type of user           
def type_of_user(userid):

    # user is group
    if str(userid)[0] == "-":
        try:
            group = vk.groups.getById(group_id=userid)
            User = [{'id': group[0]['id'], 'first_name': group[0]['name'], 'last_name': ""}]
            urlid = "club"
            return (User, urlid)
        except Exception as e:
            logging.exception(f'Function "type_of_user(GROUP_ID) dropped with id: {userid}')

    # user is administrator
    elif userid == 100:
        try:
            User = [{'id': GROUP_ID, 'first_name': 'Администратор', 'last_name': 'сообщества'}]
            urlid = "club"
            return (User, urlid)
        except Exception as e:
            logging.exception(f'Function "type_of_user(id = 100) dropped with id: {userid}')

    # user is common
    else:
        try:
            User = vk.users.get(user_id=userid)
            urlid = "id"
            return (User, urlid)
        except Exception as e:
            logging.exception(f'Function "type_of_user(common user) dropped with id: {userid}')


# check type of media
def what_media(ev_obj_attachments):

    # check attachments for objects
    try:
        # return empty string if there is no attachments
        media = ''
        if type(ev_obj_attachments) is type(None):
            return media
        elif type(ev_obj_attachments) is not type(None):
            media = f'\n<i>({ev_obj_attachments[0]["type"]})</i>'
           
            return media
    except Exception as e:
        logging.exception(f'What media func dropped with: \n {e}')


# check if photo already exists on the wall to prevent double posting bug
def check_post(photo_id):
    photo_id = str(photo_id)
    url = requests.get('https://vk.com/veganim')
    soup = bs4.BeautifulSoup(url.text, features="html.parser")
    # if the photo on the main page
    if soup.findAll('div', {'data-id': f'-{GROUP_ID}_{photo_id}'}):
        # if the photo in album's blocl
        if soup.findAll('div', {'data-id': f'-{GROUP_ID}_{photo_id}'})[0]['class'] == ['page_square_photo', 'crisp_image']:
            logging.info('check1')
            return True

    # if the photo on the wall with post
    if soup.findAll('div', {'data-id': f'-{GROUP_ID}_{photo_id}'}):
        logging.info('check2')
        return False

    # if everything else will happen
    logging.info('check3')
    return True

def food_detection(url_photo):
    path_original_image = '\home\gena\tele_bot\img\t.jpg'

    # open photo from url and save
    urllib.request.urlretrieve(url_photo, path_original_image)
    im = Image.open(path_original_image)  # open
    rgb_im = im.convert('RGB')  # convert to RGB
    image_name = os.path.basename(path_original_image)  # get the name of the image
    image_name_noext = os.path.splitext(image_name)[0] # get the name without the extension

    # create the path where the new images will be saved as '.JPG'
    path = "\home\gena\tele_bot\img\new\" + image_name_noext + '.jpg'
    rgb_im.save(path)

    # get the width and the height
    width, height = rgb_im.size
    size_mb = os.path.getsize(path) >> 20
    while (size_mb >= 1):
        # resize th image 75%
        size = int(width * 0.75), int(height * 0.75)
        rez_image = rgb_im.resize(size, Image.ANTIALIAS)
        # save the resized image
        rez_image.save(path)
        # get the size in MB
        size_mb = os.path.getsize(path) >> 20
    # LogMeal API
    api_user_token = '4fe6f02673a4abb10d396669713d476122f6c60b'
    headers = {'Authorization': 'Bearer ' + api_user_token}
    url = 'https://api.logmeal.es/v2/recognition/dish'
    resp = requests.post(url, files={'image': open(path, 'rb')}, headers=headers)
    list_of_food = ['_empty_', 'meat', 'seafood', 'fish', 'fried food']

    # if photo is food
    if resp.json()['foodType'][0]['name'] == ('food' or '_empty_'):

        # if photo in meat product group
        if resp.json()['foodFamily'][0]['name'] in list_of_food\
                and resp.json()['recognition_results'][0]['prob'] > 0.2:
            # delete photo
            os.remove(path)
            # add group info if it's exist
            food_group = '(' + resp.json()['foodFamily'][0]['name'] + ')'\
            if resp.json()['foodFamily'][0]['name'] != '_empty_' else ''
            
            return ("\nBot Warning! Photo may contain not vegan food: " +
                    food_group,
                    resp.json()['recognition_results'][0]['name'])
    os.remove(path)
    return ' '
  
  
# main vk loop
def listen():
    for event in longpoll.listen():

        # WALL
        if event.type == VkBotEventType.WALL_REPLY_NEW:

            # user info
            User, urlid = type_of_user(event.obj.from_id)

            # type of media
            media = what_media(event.obj.attachments)

            # reply to comment
            if event.obj.reply_to_comment:
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> добавил(а) <a href="https://vk.com/wall-{GROUP_ID}_'
                                          f'{event.object.post_id}?reply={event.object.id}&thread='
                                          f'{event.obj.parents_stack[0]}">комментарий на стене:</a> <pre>'
                                          f'{event.obj.text}</pre> {media}',
                                          f'{" ".join(food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'WALL RELPY TO USER dropped with: \n {e}')
            else:
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> добавил(а) <a href="https://vk.com/wall-{GROUP_ID}_'
                                          f'{event.object.post_id}?reply={event.object.id}">комментарий на стене:'
                                          f'</a> <pre>{event.obj.text}</pre> {media}'
                                          f' {" ".join(food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'WALL REPLY dropped with: \n {e}')

        # without reply to user
        if event.type == VkBotEventType.WALL_REPLY_EDIT:
            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)
            if event.obj.reply_to_comment:
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> изменил(а) <a href="https://vk.com/wall-{GROUP_ID}_'
                                          f'{event.object.post_id}?reply={event.object.id}&thread='
                                          f'{event.obj.parents_stack[0]}">комментарий на стене:</a> <pre>'
                                          f'{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'WALL REPLY TO USER EDIT dropped with: \n {e}')
            else:
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> изменил(а) <a href="https://vk.com/wall-{GROUP_ID}_'
                                          f'{event.object.post_id}?reply={event.object.id}">комментарий на стене:'
                                          f'</a> <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'WALL EDIT dropped with: \n {e}')
        if event.type == VkBotEventType.BOARD_POST_NEW:
            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)
            try:
                bot.send_message(chat_id=CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                      f'</a> добавил(а) <a href="https://vk.com/topic-{GROUP_ID}_'
                                      f'{event.object.topic_id}?post={event.object.id}">комментарий в обсуждении:'
                                      f'</a> <pre>{event.obj.text}</pre> {media}'
                                      f'{" ".join(food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logging.exception(f'BOARD POST NEW dropped with: \n {e}')
        if event.type == VkBotEventType.BOARD_POST_EDIT:
            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)
            try:
                bot.send_message(chat_id=CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                      f'</a> изменил(а) <a href="https://vk.com/topic-{GROUP_ID}_'
                                      f'{event.object.topic_id}?post={event.object.id}">комментарий в обсуждении:'
                                      f'</a> <pre>{event.obj.text}</pre> {media}',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logging.exception(f'BOARD POST EDIT with: \n {e}')
        if event.type == VkBotEventType.PHOTO_NEW:
            # User info
            User, urlid = type_of_user(event.obj.user_id)
            try:
                bot.send_message(chat_id=CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                      f'</a> добавил(а) <a href="https://vk.com/photo-{GROUP_ID}_{event.obj.id}">'
                                      f'фотографию</a>'
                                      f'{" ".join(food_detection(event.obj.sizes[-1]["url"]))}',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logging.exception(f'PHOTO NEW dropped with: \n {e}')
        if event.type == VkBotEventType.PHOTO_COMMENT_NEW:
            if check_post(event.obj.photo_id):
                # User info
                User, urlid = type_of_user(event.obj.from_id)
                media = what_media(event.obj.attachments)

                if event.obj.reply_to_comment:
                    try:
                        bot.send_message(chat_id=CHAT_ID,
                                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a>'
                                              f' добавил(а) комментарий к <a href="https://vk.com/photo-{GROUP_ID}_'
                                              f'{event.obj.photo_id}?reply={event.obj.id}&thread='
                                              f'{event.obj.reply_to_commet}">фотографии:</a> '
                                              f'<pre>{event.object.text}</pre> {media}'
                                              f'{" ".join(food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                         parse_mode='HTML', disable_web_page_preview=True)
                    except Exception as e:
                        logging.exception(f'PHOTO COMMENT REPLY TO USER dropped with: \n {e}')
                else:
                    try:
                        bot.send_message(chat_id=CHAT_ID,
                                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                                              f'добавил(а) комментарий к <a href="https://vk.com/photo-{GROUP_ID}_'
                                              f'{event.obj.photo_id}?reply={event.obj.id}">фотографии:</a> '
                                              f'<pre>{event.object.text}</pre> {media}',
                                         parse_mode='HTML', disable_web_page_preview=True)
                    except Exception as e:
                        logging.exception(f'PHOTO COMMENT DROPPED dropped with: \n {e}')
        if event.type == VkBotEventType.PHOTO_COMMENT_EDIT:
            if check_post(event.obj.photo_id):
                # User info
                User, urlid = type_of_user(event.obj.from_id)
                media = what_media(event.obj.attachments)
                if event.obj.reply_to_comment:
                    try:
                        bot.send_message(chat_id=CHAT_ID,
                                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                              f'</a> изменил(а) комментарий к <a href="https://vk.com/photo-{GROUP_ID}_'
                                              f'{event.obj.photo_id}?reply={event.obj.id}&thread='
                                              f'{event.obj.reply_to_comment}">фотографии:</a>'
                                              f' <pre>{event.object.text}</pre> {media}',
                                         parse_mode='HTML', disable_web_page_preview=True)
                    except Exception as e:
                        logging.exception(f'PHOTO COMMENT EDIT RELY TO USER dropped with: \n {e}')
                else:
                    try:
                        bot.send_message(chat_id=CHAT_ID,
                                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                              f'</a> изменил(а) комментарий к <a href="https://vk.com/photo-{GROUP_ID}_'
                                              f'{event.obj.photo_id}?reply={event.obj.id}">фотографии:</a>'
                                              f' <pre>{event.object.text}</pre> {media}',
                                         parse_mode='HTML', disable_web_page_preview=True)
                    except Exception as e:
                        logging.exception(f'PHOTO COMMENT EDIT dropped with: \n {e}')
        if event.type == VkBotEventType.VIDEO_NEW:
            User, urlid = type_of_user(event.obj.owner_id)

            try:
                bot.send_message(chat_id=CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                      f'</a> добавил(а) <a href="https://vk.com/video-{GROUP_ID}_'
                                      f'{event.obj.id}">видео</a> в видеозаписи группы: '
                                      f'<b>{event.obj.title}</b>',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logging.exception(f'VIDEO NEW dropped with: \n {e}')
        if event.type == VkBotEventType.VIDEO_COMMENT_NEW:
            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)

            if event.obj.reply_to_comment:
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> добавил(а) комментарий к <a href="https://vk.com/video-{GROUP_ID}_'
                                          f'{event.object.video_id}?reply={event.obj.id}&thread='
                                          f'{event.obj.reply_to_comment}">видеозаписи:</a>'
                                          f' <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'VIDEO NEW COMMENT REPLY TO USER dropped with: \n {e}')
            else:
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> добавил(а) комментарий к <a href="https://vk.com/video-{GROUP_ID}_'
                                          f'{event.object.video_id}?reply={event.obj.id}">видеозаписи:</a>'
                                          f' <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'VIDEO COMMENT with: \n {e}')
        if event.type == VkBotEventType.VIDEO_COMMENT_EDIT:

            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)

            if event.obj.reply_to_comment:
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> изменил(а) комментарий к <a href="https://vk.com/video-{GROUP_ID}_'
                                          f'{event.object.video_id}?reply={event.obj.id}&thread='
                                          f'{event.obj.reply_to_comment}">видеозаписи:</a>'
                                          f' <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'VIDEO COMMENT EDIT REPLY TO USER dropped with: \n {e}')
            else:
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> изменил(а) комментарий к <a href="https://vk.com/video-{GROUP_ID}_'
                                          f'{event.object.video_id}?reply={event.obj.id}">видеозаписи:</a>'
                                          f' <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'VIDEO COMMENT EDIT dropped with: \n {e}')
        if event.type == VkBotEventType.WALL_POST_NEW:
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)
            if event.obj.post_type == "suggest":
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                                          f'предложил(а) новую <a href="https://vk.com/'
                                          f'wall-{GROUP_ID}_{event.obj.id}">запись:</a> <pre>{event.obj.text}</pre> {media}'
                                          f'{" ".join(food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'WALL POST SUGGEST dropped with: \n {e}')
            else:
                try:
                    bot.send_message(chat_id=CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                                          f'опубликовал(а) на стене сообщества новую <a href="https://vk.com/'
                                          f'wall-{GROUP_ID}_{event.obj.id}">запись:</a> <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    logging.exception(f'WALL POST NEW dropped with: \n {e}')
        if event.type == VkBotEventType.USER_BLOCK:
            admin_id, admin_urlid = type_of_user(event.obj.admin_id)
            User, urlid = type_of_user(event.obj.user_id)
            comment = ""
            if event.obj.comment:
                comment = f'Комментарий: <pre>{event.obj.comment}</pre>'
            reason_dict = {1: "спам", 2: "оскорбление участников",
                           3: "нецензурные выражения", 4: "сообщения не по теме", 0: " другое"}
            try:
                bot.send_message(chat_id=CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{admin_urlid}'
                                      f'{admin_id[0]["id"]}">{admin_id[0]["first_name"]} {admin_id[0]["last_name"]}</a> '
                                      f'заблокировал(а) пользователя <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                                      f'{"на срок до " + (datetime.utcfromtimestamp(event.obj.unblock_date).strftime("%Y-%m-%d %H:%M:%S")) if event.obj.unblock_date != 0 else "навсегда"}'
                                      f'. Причина: {reason_dict[event.obj.reason]}.\n{comment}',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logging.exception(f'BLOCK USER dropped with: \n {e}')
        if event.type == VkBotEventType.USER_UNBLOCK:
            admin_id, admin_urlid = type_of_user(event.obj.admin_id)
            User, urlid = type_of_user(event.obj.user_id)
            try:
                bot.send_message(chat_id=CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{admin_urlid}'
                                      f'{admin_id[0]["id"]}">{admin_id[0]["first_name"]} {admin_id[0]["last_name"]}</a> '
                                      f'разблокировал(а) пользователя <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> ',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logging.exception(f'UNBLOCK USER dropped with: \n {e}')

# handler for user commands from telegram         
@bot.message_handler(commands=['check'])
def send_check_message(message):
    if threading.Thread.is_alive(t1):
        bot.send_message(chat_id=CHAT_ID, text='OK')
    else:
        bot.send_message(chat_id=CHAT_ID, text='dead :(')
      
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})
def Webhook_listen():
  cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
  
# threading processes
# first thread is vk longpoll listner
t1 = threading.Thread(target=listen)
t1.start()
logging.info("Vk lonpoll started")

# second thread is telegram handler
t2 = threading.Thread(target=Webhook_listen)
t2.start()
logging.info("Telegram webhook started")

# while true loop to ignore crashes
while True:
    try:
        time.sleep(60)
        if not(threading.Thread.is_alive(t1)):
            t1 = threading.Thread(target=listen)
            t1.start()
            logging.info('Vk longpoll have started from the loop')
    except Exception as e:
        logging.exception(f'Couldn\'t start Vk lonpoll from the loop with: \n {e}')
    try:
        time.sleep(60)
        if not(threading.Thread.is_alive(t2)):
            print(threading.Thread.is_alive(t2))
            t2 = threading.Thread(target=Webhook_listen)
            t2.start()
            print('Telegram webhook have started from the loop')
    except Exception as e:
        logging.exception(f'Couldn\'t start telegram webhook from the loop with: \n {e}')


