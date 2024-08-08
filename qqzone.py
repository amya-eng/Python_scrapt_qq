import os
import re
import time
import json
import csv
import random
import warnings
import requests
from bs4 import BeautifulSoup
from utils.misc import *
from utils.get_cookies import get_cookies

warnings.filterwarnings('ignore')


class QQFriendSpider():
    def __init__(self, qq_number, g_tk, proxies=None):
        self.qq_number = qq_number
        self.g_tk = g_tk
        self.session = requests.Session()
        self.session.proxies = proxies
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }

    def get_friends(self):
        url = 'https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi'
        params = {
            'uin': self.qq_number,
            'do': '1',
            'g_tk': self.g_tk
        }
        response = self.session.get(url, headers=self.headers, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')

        friends = []
        for friend_link in soup.select('.f-info .username a'):
            friend = {}
            friend['qq_number'] = re.findall(r'uin=(\d+)', friend_link['href'])[0]
            friend['nickname'] = friend_link.get_text()
            friends.append(friend)

        return friends

    def get_friend_friends(self, friend_qq_number):
        url = 'https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/qqgroupfriend_extend.cgi'
        params = {
            'uin': self.qq_number,
            'do': '1',
            'g_tk': self.g_tk,
            'rd': random.random(),
            'fupdate': '1'
        }
        data = {
            'uin': friend_qq_number,
            'do': '1'
        }
        response = self.session.post(url, headers=self.headers, params=params, data=data)
        soup = BeautifulSoup(response.text, 'html.parser')

        friends = []
        for friend_link in soup.select('.f-info .username a'):
            friend = {}
            friend['qq_number'] = re.findall(r'uin=(\d+)', friend_link['href'])[0]
            friend['nickname'] = friend_link.get_text()
            friends.append(friend)

        return friends

    def crawl(self):
        friends = self.get_friends()

        data = []
        for friend in friends:
            friend_friends = self.get_friend_friends(friend['qq_number'])
            data.append({
                'qq_number': friend['qq_number'],
                'nickname': friend['nickname'],
                'friend_count': len(friend_friends)
            })
            for friend_friend in friend_friends:
                friend_friend_friends = self.get_friend_friends(friend_friend['qq_number'])
                data.append({
                    'qq_number': friend_friend['qq_number'],
                    'nickname': friend_friend['nickname'],
                    'friend_count': len(friend_friend_friends)
                })
                for friend_friend_friend in friend_friend_friends:
                    data.append({
                        'qq_number': friend_friend_friend['qq_number'],
                        'nickname': friend_friend_friend['nickname'],
                        'friend_count': 0
                    })

        self.save_to_csv(data, 'friends.csv')

    def save_to_csv(self, data, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['qq_number', 'nickname', 'friend_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)