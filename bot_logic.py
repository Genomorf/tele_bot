import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
#import pymysql.cursors
import requests
import telebot
from datetime import datetime

# constantss
Text = ''
GroupId = "197381393"
ChatId = "-499017057"
token1 = "fdf63f1dae61a44e0a285c4c5e977041a38fb1ac98445f835879c49fb3f7513089320970689db9ebd6da2"
token2 = "ed7f1b64be582e8a81a824b0a5572d9b65f336aa726c58915583419ebfa66c47e004f191d4201ae24f8f5"
# AUTH
bot = telebot.TeleBot("721671579:AAFR4Fpn-xkJnyr8cDunU9fXRvCE7QsNlB8")
vk_session = vk_api.VkApi(token=token1)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GroupId)


def type_of_user(userid):

    if str(userid)[0] == "-":
        group = vk.groups.getById(group_id=userid)
        User = [{'id': group[0]['id'], 'first_name': group[0]['name'], 'last_name':""}]
        urlid = "club"
    elif userid == 100:
        User = [{'id': GroupId, 'first_name': 'Администратор', 'last_name': 'сообщества'}]
        urlid = "club"
    else:
        User = vk.users.get(user_id=userid)
        urlid = "id"
    return (User, urlid)


for event in longpoll.listen():

    # WALL
    if event.type == VkBotEventType.WALL_REPLY_NEW:

        # User info
        User, urlid = type_of_user(event.obj.from_id)
        if event.obj.reply_to_comment:
             bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> добавил(а) <a href="https://vk.com/wall-{GroupId}_'
                                  f'{event.object.post_id}?reply={event.object.id}&thread='
                                  f'{event.obj.parents_stack[0]}">комментарий на стене:</a> <pre>'
                                  f'{event.obj.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> добавил(а) <a href="https://vk.com/wall-{GroupId}_'
                                  f'{event.object.post_id}?reply={event.object.id}">комментарий на стене:'
                                  f'</a> <pre>{event.obj.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.WALL_REPLY_EDIT:
        # User info
        User, urlid = type_of_user(event.obj.from_id)

        if event.obj.reply_to_comment:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> изменил(а) <a href="https://vk.com/wall-{GroupId}_'
                                  f'{event.object.post_id}?reply={event.object.id}&thread='
                                  f'{event.obj.parents_stack[0]}">комментарий на стене:</a> <pre>'
                                  f'{event.obj.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> изменил(а) <a href="https://vk.com/wall-{GroupId}_'
                                  f'{event.object.post_id}?reply={event.object.id}">комментарий на стене:'
                                  f'</a> <pre>{event.obj.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.BOARD_POST_NEW:
        # User info
        User, urlid = type_of_user(event.obj.from_id)

        bot.send_message(chat_id=ChatId,
                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                              f'</a> добавил(а) <a href="https://vk.com/topic-{GroupId}_'
                              f'{event.object.topic_id}?post={event.object.id}">комментарий в обсуждении:'
                              f'</a> <pre>{event.obj.text}</pre>',
                         parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.BOARD_POST_EDIT:
        # User info
        User, urlid = type_of_user(event.obj.from_id)

        bot.send_message(chat_id=ChatId,
                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                              f'</a> изменил(а) <a href="https://vk.com/topic-{GroupId}_'
                              f'{event.object.topic_id}?post={event.object.id}">комментарий в обсуждении:'
                              f'</a> <pre>{event.obj.text}</pre>',
                         parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.PHOTO_NEW:

        # User info
        User, urlid = type_of_user(event.obj.user_id)

        bot.send_message(chat_id=ChatId,
                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                              f'</a> добавил(а) <a href="https://vk.com/photo-{GroupId}_{event.obj.id}">'
                              f'фотографию</a>',
                         parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.PHOTO_COMMENT_NEW:
        # User info
        User, urlid = type_of_user(event.obj.from_id)
        if event.obj.reply_to_comment:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a>'
                                  f' добавил(а) комментарий к <a href="https://vk.com/photo-{GroupId}_'
                                  f'{event.obj.photo_id}?reply={event.obj.id}&thread='
                                  f'{event.obj.reply_to_commet}">фотографии:</a> '
                                  f'<pre>{event.object.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                                  f'добавил(а) комментарий к <a href="https://vk.com/photo-{GroupId}_'
                                  f'{event.obj.photo_id}?reply={event.obj.id}">фотографии:</a> '
                                  f'<pre>{event.object.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.PHOTO_COMMENT_EDIT:
        # User info
        User, urlid = type_of_user(event.obj.from_id)

        if event.obj.reply_to_comment:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> изменил(а) комментарий к <a href="https://vk.com/photo-{GroupId}_'
                                  f'{event.obj.photo_id}?reply={event.obj.id}&thread='
                                  f'{event.obj.reply_to_comment}">фотографии:</a>'
                                  f' <pre>{event.object.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> изменил(а) комментарий к <a href="https://vk.com/photo-{GroupId}_'
                                  f'{event.obj.photo_id}?reply={event.obj.id}">фотографии:</a>'
                                  f' <pre>{event.object.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.VIDEO_NEW:
        User, urlid = type_of_user(event.obj.owner_id)
        bot.send_message(chat_id=ChatId,
                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                              f'</a> добавил(а) <a href="https://vk.com/video-{GroupId}_'
                              f'{event.obj.id}">видео</a> в видеозаписи группы: '
                              f'<b>{event.obj.title}</b>',
                         parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.VIDEO_COMMENT_NEW:
        # User info
        User, urlid = type_of_user(event.obj.from_id)
        if event.obj.reply_to_comment:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> добавил(а) комментарий к <a href="https://vk.com/video-{GroupId}_'
                                  f'{event.object.video_id}?reply={event.obj.id}&thread='
                                  f'{event.obj.reply_to_comment}">видеозаписи:</a>'
                                  f' <pre>{event.obj.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)

        else:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> добавил(а) комментарий к <a href="https://vk.com/video-{GroupId}_'
                                  f'{event.object.video_id}?reply={event.obj.id}">видеозаписи:</a>'
                                  f' <pre>{event.obj.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.VIDEO_COMMENT_EDIT:
        # User info
        User, urlid = type_of_user(event.obj.from_id)
        if event.obj.reply_to_comment:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> изменил(а) комментарий к <a href="https://vk.com/video-{GroupId}_'
                                  f'{event.object.video_id}?reply={event.obj.id}&thread='
                                  f'{event.obj.reply_to_comment}">видеозаписи:</a>'
                                  f' <pre>{event.obj.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)

        else:
            bot.send_message(chat_id=ChatId,
                             text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                                  f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}'
                                  f'</a> изменил(а) комментарий к <a href="https://vk.com/video-{GroupId}_'
                                  f'{event.object.video_id}?reply={event.obj.id}">видеозаписи:</a>'
                                  f' <pre>{event.obj.text}</pre>',
                             parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.WALL_POST_NEW:
        User, urlid = type_of_user(event.obj.from_id)

        bot.send_message(chat_id=ChatId,
                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                              f'опубликовал(а) на стене сообщества новую <a href="https://vk.com/'
                              f'wall-{GroupId}_{event.obj.id}">запись:</a> <pre>{event.obj.text}</pre>',
                         parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.USER_BLOCK:
        admin_id, admin_urlid = type_of_user(event.obj.admin_id)
        User, urlid = type_of_user(event.obj.user_id)
        comment = ""
        if event.obj.comment:
            comment = f'Комментарий: <pre>{event.obj.comment}</pre>'
        reason_dict = {1: "спам", 2: "оскорбление участников",
                       3: "нецензурные выражения", 4: "сообщения не по теме", 0: " другое"}
        bot.send_message(chat_id=ChatId,
                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{admin_urlid}'
                              f'{admin_id[0]["id"]}">{admin_id[0]["first_name"]} {admin_id[0]["last_name"]}</a> '
                              f'заблокировал(а) пользователя <a href="https://vk.com/{urlid}'
                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                              f'{"на срок до "+(datetime.utcfromtimestamp(event.obj.unblock_date).strftime("%Y-%m-%d %H:%M:%S")) if event.obj.unblock_date != 0 else "навсегда"}'
                              f'. Причина: {reason_dict[event.obj.reason]}.\n{comment}',
                         parse_mode='HTML', disable_web_page_preview=True)

    if event.type == VkBotEventType.USER_UNBLOCK:
        admin_id, admin_urlid = type_of_user(event.obj.admin_id)
        User, urlid = type_of_user(event.obj.user_id)
        bot.send_message(chat_id=ChatId,
                         text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{admin_urlid}'
                              f'{admin_id[0]["id"]}">{admin_id[0]["first_name"]} {admin_id[0]["last_name"]}</a> '
                              f'разблокировал(а) пользователя <a href="https://vk.com/{urlid}'
                              f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> ',
                         parse_mode='HTML', disable_web_page_preview=True)

    # if event.type == VkBotEventType.GR:
    #     print("O")
    #     User, urlid = type_of_user(event.obj.user_id)
    #     changes_dict = {"title": "название", "description": "описание", "access": "тип группы",
    #                "screen_name": "короткий адрес", "public_category": "категорию публичной страницы",
    #                "public_subcategory": "подкатегорию публичной страницы",
    #                "age_limits": "возрастные ограничения", "website": "веб-сайт",
    #                "enable_status_default": "статус", "enable_audio": "аудио", "enable_photo": "фото",
    #                "enable_video": "видео", "enable_market": "маркет"}
    #     bot.send_message(chat_id=ChatId, text="AAAA")
                         # text=f'В сообществе <b>"Веганим Вместе"</b> <a href="https://vk.com/{urlid}'
                         #      f'{User[0]["id"]}">{User[0]["first_name"]} {User[0]["last_name"]}</a> '
                         #      f'изменил(а) {changes_dict[event.obj.changes]} c {event.obj.old_value}'
                         #      f'на {event.obj.new_value}.',
                         # parse_mode='HTML', disable_web_page_preview=True)

