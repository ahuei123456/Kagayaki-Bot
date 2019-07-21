from collections import deque
from discord.ext import commands
from discord import Message
from bot.onibe import post
from bot.onibe.twitter import Twitter
from bot.onibe.facebook import Facebook
import json
import os
import pickle
import schedule

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
        self.tweet_queue = pickle.load(open(save_path, 'rb'))
        if self.tweet_queue is not deque:
            self.tweet_queue = deque()

    def _save_messages(self):
        pickle.dump(self.tweet_queue, open(save_path, 'wb'))

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
        pass

    def post(self):
        pass

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.id != self.bot.user.id:
            if message.channel.id == self.config['archive_channel']:
                pass
