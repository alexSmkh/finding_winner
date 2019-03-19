from instabot import Bot
from os import getenv
from os import getcwd
from os.path import join
from dotenv import load_dotenv
import random
import re
import argparse


def get_users_mentioned_two_friends(comments_info):
    breaker = 0
    users_exist = []
    pattern = '(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'
    for comment_info in comments_info:
        two_mentioned_users = set(re.findall(pattern, comment_info['text']))
        if not len(two_mentioned_users) > 1:
            continue
        if not is_user_exist(two_mentioned_users):
            continue
        users_exist.append(
            (
                str(comment_info['user_id']),
                comment_info['user']['username']
            )
        )
        breaker += 1
        if breaker > 20: break
    return users_exist


def get_followers(users, post_authors_name):
    author_id = bot.get_user_id_from_username(post_authors_name)
    follower_list = bot.get_user_followers(author_id)
    followers = [user for user in users if user[0] in follower_list]
    return followers


def get_users_liked_post(existings_users, media_id):
    users_id_ = bot.get_media_likers(str(media_id))
    index_for_user_id = 0
    liked_user = [
        user for user in existings_users if user[index_for_user_id] in users_id_
    ]
    return liked_user


def is_user_exist(usernames):
    result = [
        True if bot.get_user_id_from_username(user_name) else False
        for user_name in usernames
    ]
    return True if result[0] and result[1] else False


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
    link_post, post_authors_name = get_link_post_and_username()
    login = getenv('LOGIN')
    password = getenv('PASSWORD')
    bot = Bot()
    bot.login(username=login, password=password)
    media_id = bot.get_media_id_from_link(link_post)
    comments_info = bot.get_media_comments_all(media_id)
    users_exist = get_users_mentioned_two_friends(comments_info)
    users_liked_post = get_users_liked_post(users_exist, media_id)
    followers = get_followers(users_liked_post, post_authors_name)
    follower_usernames = set(name for id, name in followers)
    print('Наш победитель - {}!'.format(*random.sample(follower_usernames, 1)))
