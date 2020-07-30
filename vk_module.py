import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests
import bs4
from datetime import datetime
import log_module
import tg_module
import foodr

# CONSTANTS
DAMN = "197381393" # for test
VEG = "139197081" # for prod
GROUP_ID = VEG

TOKEN_DAMN = "fdf63f1dae61a44e0a285c4c5e977041a38fb1ac98445f835879c49fb3f7513089320970689db9ebd6da2" # for test
TOKEN_VEG = "ed7f1b64be582e8a81a824b0a5572d9b65f336aa726c58915583419ebfa66c47e004f191d4201ae24f8f5" # for prod
# vk auth
vk_session = vk_api.VkApi(token=TOKEN_VEG)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
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
            logging.exception(f'Function type_of_user(GROUP_ID) dropped with id: {userid}')

    # user is administrator
    elif userid == 100:
        try:
            User = [{'id': GROUP_ID, 'first_name': 'Администратор', 'last_name': 'сообщества'}]
            urlid = "club"
            return (User, urlid)
        except Exception as e:
            log_module.logging.exception(f'Function type_of_user(id = 100) dropped with id: {userid}')

    # user is common
    else:
        try:
            User = vk.users.get(user_id=userid)
            urlid = "id"
            return (User, urlid)
        except Exception as e:
            log_module.logging.exception(f'Function "type_of_user(common user) dropped with id: {userid}')


# check type of media
def what_media(ev_obj_attachments):

    # check attachments for objects
    try:
        # return empty string if there is no attachments
        media = ''
        if type(ev_obj_attachments) is type(None):
            return media
        elif type(ev_obj_attachments) is not type(None):
            media = f'<i>({ev_obj_attachments[0]["type"]})</i>'
           
            return media
    except Exception as e:
        log_module.logging.exception(f'What media func dropped with: \n {e}')


# check if photo already exists on the wall to prevent double posting bug
def check_post(photo_id):
    photo_id = str(photo_id)
    url = requests.get('https://vk.com/veganim')
    soup = bs4.BeautifulSoup(url.text, features="html.parser")
    # if the photo on the main page
    if soup.findAll('div', {'data-id': f'-{GROUP_ID}_{photo_id}'}):
        # if the photo in album's blocl
        if soup.findAll('div', {'data-id': f'-{GROUP_ID}_{photo_id}'})[0]['class'] == ['page_square_photo', 'crisp_image']:
            log_module.logging.info('check1')
            return True
    # if the photo on the wall with post
    if soup.findAll('div', {'data-id': f'-{GROUP_ID}_{photo_id}'}):
        log_module.logging.info('check2')
        return False

    # if everything else will happen
    log_module.logging.info('check3')
    return True
 
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
                    
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> добавил(а) <a href="https://vk.com/wall-{GROUP_ID}_'
                                          f'{event.object.post_id}?reply={event.object.id}&thread='
                                          f'{event.obj.parents_stack[0]}">комментарий на стене:</a> <pre>'
                                          f'{event.obj.text}</pre>\n{media}'
                                          f'{" ".join(foodr.food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'WALL RELPY TO USER dropped with: \n {e}')
            else:
                try:
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> добавил(а) <a href="https://vk.com/wall-{GROUP_ID}_'
                                          f'{event.object.post_id}?reply={event.object.id}">комментарий на стене:'
                                          f'</a> <pre>{event.obj.text}</pre>\n{media}'
                                          f' {" ".join(foodr.food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'WALL REPLY dropped with: \n {e}')

        # without reply to user
        if event.type == VkBotEventType.WALL_REPLY_EDIT:
            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)
            if event.obj.reply_to_comment:
                try:
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> изменил(а) <a href="https://vk.com/wall-{GROUP_ID}_'
                                          f'{event.object.post_id}?reply={event.object.id}&thread='
                                          f'{event.obj.parents_stack[0]}">комментарий на стене:</a> <pre>'
                                          f'{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'WALL REPLY TO USER EDIT dropped with: \n {e}')
            else:
                try:
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> изменил(а) <a href="https://vk.com/wall-{GROUP_ID}_'
                                          f'{event.object.post_id}?reply={event.object.id}">комментарий на стене:'
                                          f'</a> <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'WALL EDIT dropped with: \n {e}')
        if event.type == VkBotEventType.BOARD_POST_NEW:
            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)
            try:
                tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                      f'</a> добавил(а) <a href="https://vk.com/topic-{GROUP_ID}_'
                                      f'{event.object.topic_id}?post={event.object.id}">комментарий в обсуждении:'
                                      f'</a> <pre>{event.obj.text}</pre>\n{media}'
                                      f'{" ".join(foodr.food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                log_module.logging.exception(f'BOARD POST NEW dropped with: \n {e}')
        if event.type == VkBotEventType.BOARD_POST_EDIT:
            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)
            try:
                tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                      f'</a> изменил(а) <a href="https://vk.com/topic-{GROUP_ID}_'
                                      f'{event.object.topic_id}?post={event.object.id}">комментарий в обсуждении:'
                                      f'</a> <pre>{event.obj.text}</pre> {media}',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                log_module.logging.exception(f'BOARD POST EDIT with: \n {e}')
        if event.type == VkBotEventType.PHOTO_NEW:
            # User info
            User, urlid = type_of_user(event.obj.user_id)
            try:
                tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                      f'</a> добавил(а) <a href="https://vk.com/photo-{GROUP_ID}_{event.obj.id}">'
                                      f'фотографию</a>'
                                      f'\n{" ".join(foodr.food_detection(event.obj.sizes[-1]["url"]))}',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                log_module.logging.exception(f'PHOTO NEW dropped with: \n {e}')
        if event.type == VkBotEventType.PHOTO_COMMENT_NEW:
            if check_post(event.obj.photo_id):
                # User info
                User, urlid = type_of_user(event.obj.from_id)
                media = what_media(event.obj.attachments)

                if event.obj.reply_to_comment:
                    try:
                        tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a>'
                                              f' добавил(а) комментарий к <a href="https://vk.com/photo-{GROUP_ID}_'
                                              f'{event.obj.photo_id}?reply={event.obj.id}&thread='
                                              f'{event.obj.reply_to_commet}">фотографии:</a> '
                                              f'<pre>{event.object.text}</pre>\n{media}'
                                              f'{" ".join(foodr.food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                         parse_mode='HTML', disable_web_page_preview=True)
                    except Exception as e:
                        log_module.logging.exception(f'PHOTO COMMENT REPLY TO USER dropped with: \n {e}')
                else:
                    try:
                        tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                                              f'добавил(а) комментарий к <a href="https://vk.com/photo-{GROUP_ID}_'
                                              f'{event.obj.photo_id}?reply={event.obj.id}">фотографии:</a> '
                                              f'<pre>{event.object.text}</pre> {media}'
                                              f'{" ".join(foodr.food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                         parse_mode='HTML', disable_web_page_preview=True)
                    except Exception as e:
                        log_module.logging.exception(f'PHOTO COMMENT DROPPED dropped with: \n {e}')
        if event.type == VkBotEventType.PHOTO_COMMENT_EDIT:
            if check_post(event.obj.photo_id):
                # User info
                User, urlid = type_of_user(event.obj.from_id)
                media = what_media(event.obj.attachments)
                if event.obj.reply_to_comment:
                    try:
                        tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                              f'</a> изменил(а) комментарий к <a href="https://vk.com/photo-{GROUP_ID}_'
                                              f'{event.obj.photo_id}?reply={event.obj.id}&thread='
                                              f'{event.obj.reply_to_comment}">фотографии:</a>'
                                              f' <pre>{event.object.text}</pre> {media}',
                                         parse_mode='HTML', disable_web_page_preview=True)
                    except Exception as e:
                        log_module.logging.exception(f'PHOTO COMMENT EDIT RELY TO USER dropped with: \n {e}')
                else:
                    try:
                        tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                              f'</a> изменил(а) комментарий к <a href="https://vk.com/photo-{GROUP_ID}_'
                                              f'{event.obj.photo_id}?reply={event.obj.id}">фотографии:</a>'
                                              f' <pre>{event.object.text}</pre> {media}',
                                         parse_mode='HTML', disable_web_page_preview=True)
                    except Exception as e:
                        log_module.logging.exception(f'PHOTO COMMENT EDIT dropped with: \n {e}')
        if event.type == VkBotEventType.VIDEO_NEW:
            User, urlid = type_of_user(event.obj.owner_id)

            try:
                tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                      f'</a> добавил(а) <a href="https://vk.com/video-{GROUP_ID}_'
                                      f'{event.obj.id}">видео</a> в видеозаписи группы: '
                                      f'<b>{event.obj.title}</b>',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                log_module.logging.exception(f'VIDEO NEW dropped with: \n {e}')
        if event.type == VkBotEventType.VIDEO_COMMENT_NEW:
            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)

            if event.obj.reply_to_comment:
                try:
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> добавил(а) комментарий к <a href="https://vk.com/video-{GROUP_ID}_'
                                          f'{event.object.video_id}?reply={event.obj.id}&thread='
                                          f'{event.obj.reply_to_comment}">видеозаписи:</a>'
                                          f' <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'VIDEO NEW COMMENT REPLY TO USER dropped with: \n {e}')
            else:
                try:
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> добавил(а) комментарий к <a href="https://vk.com/video-{GROUP_ID}_'
                                          f'{event.object.video_id}?reply={event.obj.id}">видеозаписи:</a>'
                                          f' <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'VIDEO COMMENT with: \n {e}')
        if event.type == VkBotEventType.VIDEO_COMMENT_EDIT:

            # User info
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)

            if event.obj.reply_to_comment:
                try:
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> изменил(а) комментарий к <a href="https://vk.com/video-{GROUP_ID}_'
                                          f'{event.object.video_id}?reply={event.obj.id}&thread='
                                          f'{event.obj.reply_to_comment}">видеозаписи:</a>'
                                          f' <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'VIDEO COMMENT EDIT REPLY TO USER dropped with: \n {e}')
            else:
                try:
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                          f'</a> изменил(а) комментарий к <a href="https://vk.com/video-{GROUP_ID}_'
                                          f'{event.object.video_id}?reply={event.obj.id}">видеозаписи:</a>'
                                          f' <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'VIDEO COMMENT EDIT dropped with: \n {e}')
        if event.type == VkBotEventType.WALL_POST_NEW:
            User, urlid = type_of_user(event.obj.from_id)
            media = what_media(event.obj.attachments)
            if event.obj.post_type == "suggest":
                try:
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                                          f'предложил(а) новую <a href="https://vk.com/'
                                          f'wall-{GROUP_ID}_{event.obj.id}">запись:</a> <pre>{event.obj.text}</pre> {media}'
                                          f'{" ".join(foodr.food_detection(event.obj.attachments[0]["photo"]["sizes"][-1]["url"])) if media == "<i>(photo)</i>" else ""}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'WALL POST SUGGEST dropped with: \n {e}')
            else:
                try:
                    tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                     text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                          f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                                          f'опубликовал(а) на стене сообщества новую <a href="https://vk.com/'
                                          f'wall-{GROUP_ID}_{event.obj.id}">запись:</a> <pre>{event.obj.text}</pre> {media}',
                                     parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    log_module.logging.exception(f'WALL POST NEW dropped with: \n {e}')
        if event.type == VkBotEventType.USER_BLOCK:
            admin_id, admin_urlid = type_of_user(event.obj.admin_id)
            User, urlid = type_of_user(event.obj.user_id)
            comment = ""
            if event.obj.comment:
                comment = f'Комментарий: <pre>{event.obj.comment}</pre>'
            reason_dict = {1: "спам", 2: "оскорбление участников",
                           3: "нецензурные выражения", 4: "сообщения не по теме", 0: " другое"}
            try:
                tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{admin_urlid}'
                                      f'{admin_id[0]["id"]}">{admin_id[0]["first_name"]} {admin_id[0]["last_name"]}</a> '
                                      f'заблокировал(а) пользователя <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                                      f'{"на срок до " + (datetime.datetime.utcfromtimestamp(event.obj.unblock_date).strftime("%Y-%m-%d %H:%M:%S")) if event.obj.unblock_date != 0 else "навсегда"}'
                                      f'. Причина: {reason_dict[event.obj.reason]}.\n{comment}',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                log_module.logging.exception(f'BLOCK USER dropped with: \n {e}')
        if event.type == VkBotEventType.USER_UNBLOCK:
            admin_id, admin_urlid = type_of_user(event.obj.admin_id)
            User, urlid = type_of_user(event.obj.user_id)
            try:
                tg_module.bot.send_message(chat_id=tg_module.CHAT_ID,
                                 text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{admin_urlid}'
                                      f'{admin_id[0]["id"]}">{admin_id[0]["first_name"]} {admin_id[0]["last_name"]}</a> '
                                      f'разблокировал(а) пользователя <a href="https://vk.com/{urlid}'
                                      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> ',
                                 parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                log_module.logging.exception(f'UNBLOCK USER dropped with: \n {e}')



