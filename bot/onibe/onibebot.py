from bot.onibe.twitter import Twitter
from bot.onibe.facebook import Facebook
from bot.onibe import post
from collections import deque
from datetime import datetime
from discord.ext import commands
from discord import Message
from threading import Lock, Thread
import json
import os
import pickle
import re
import time

save_path = os.path.join(os.getcwd(), 'data', 'messages.sav')


class OnibeBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._load_messages()
        self._load_config()
        self._init_posters()

    def _load_config(self, path=None):
        if path is None:
            path = os.path.join(os.getcwd(), 'conf', 'onibebot.json')

        with open(path) as f:
            self.config = json.load(f)

    def _load_messages(self):
        self.message_queue = pickle.load(open(save_path, 'rb'))
        if self.message_queue is not deque:
            self.message_queue = deque()

    def _save_messages(self):
        pickle.dump(self.message_queue, open(save_path, 'wb'))

    def _init_posters(self):
        self.posters = []

        self._load_twitter()
        self._load_facebook()

    def _load_twitter(self):
        tw = Twitter(self.config['twitter'])
        self.posters.append(tw)

    def _load_facebook(self):
        fb = Facebook(self.config['facebook'])
        self.posters.append(fb)

    def _init_scheduler(self):
        today = datetime.today()
        self.date = today.day
        self.lock = Lock()
        self.loop = Thread(target=self._loop)
        self.loop.start()

    def _loop(self):
        today = datetime.today()
        length = 3600 - today.minute * 60 - today.second

        time.sleep(length)

        while True:
            today = datetime.today()
            if today.day != self.date and today.hour > 8:
                self.date = today.day
                self._post()

            time.sleep(3600)

    def _post(self):
        if len(self.message_queue) > 0:
            message = self.message_queue.popleft()
            for poster in self.posters:
                poster.post(message)

            with self.lock:
                self._save_messages()

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.id != self.bot.user.id:
            if message.channel.id == self.config['archive_channel']:
                link = re.search(r"(?P<url>https?://[^\s]+)", message.content).group("url")
                text = message.content.replace(link, '').strip()
                message = post.Message(text, link, [])

                self.message_queue.append(message)
