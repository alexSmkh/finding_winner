from instabot import Bot
from os import getenv
from os import getcwd
from os.path import join
from dotenv import load_dotenv
import random
import re
import argparse


def get_users_mentioned_two_friends(comments):
    existing_users = []
    """
    regex for instagram username was taken:
    https://blog.jstassen.com/2016/03/code-regex-for-instagram-username-and-hashtags/
    """
    pattern = '(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'
    for comment in comments:
        mentioned_users = set(re.findall(pattern, comment['text']))
        """
        Поясните, пожалуйста, где здесь была ошибка в логике. 
        Первый if я делал для того, чтобы отсеять пустые или имеющие один элемент
        множества, чтобы лишний раз не отправлять запрос на сервер.
        Вторым if-ом проверял существуют ли одновременно оба mentioned_users.
        """
        if not is_users_exist(mentioned_users):
            continue
        if not len(mentioned_users) > 1:
            continue

        existing_users.append(
            (
                str(comment['user_id']),
                comment['user']['username']
            )
        )
    return existing_users


def is_users_exist(usernames):
    return all([True if bot.get_user_id_from_username(username) else False for username in usernames])


def get_followers(users, post_author_name):
    author_id = bot.get_user_id_from_username(post_author_name)
    follower_list = bot.get_user_followers(author_id)
    followers = [user for user in users if user[0] in follower_list]
    return followers


def get_users_liked_post(existing_users, media_id):
    users_ids = bot.get_media_likers(str(media_id))
    index_for_user_id = 0
    liked_users = [
        user for user in existing_users if user[index_for_user_id] in users_ids
    ]
    return liked_users


def get_link_post_and_username():
    parser = argparse.ArgumentParser(
        description='Ищем победителя розыгрыша в Instagram'
    )
    parser.add_argument('url', help='Ссылка на пост с розыгрышем')
    parser.add_argument('login', help='Логин автора розыгрыша')
    args = parser.parse_args()
    return args.url, args.login


if __name__ == '__main__':
    env_patn = join(getcwd(), '.env')
    load_dotenv(env_patn)
    link_post, post_author_name = get_link_post_and_username()
    login = getenv('LOGIN')
    password = getenv('PASSWORD')
    bot = Bot()
    bot.login(username=login, password=password)
    media_id = bot.get_media_id_from_link(link_post)
    comments = bot.get_media_comments_all(media_id)
    users_exist = get_users_mentioned_two_friends(comments)
    users_liked_post = get_users_liked_post(users_exist, media_id)
    followers = get_followers(users_liked_post, post_author_name)
    follower_usernames = set(name for id, name in followers)
    print('Наш победитель - {}!'.format(*random.sample(follower_usernames, 1)))
