from bot.helpers import helpers
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
img_path = os.path.join(os.getcwd(), 'img')


class OnibeBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._load_messages()
        self._load_config()
        self._init_posters()
        self._init_scheduler()

    def _load_config(self, path=None):
        if path is None:
            path = os.path.join(os.getcwd(), 'conf', 'onibebot.json')

        with open(path) as f:
            self.config = json.load(f)

        self.archive_channels = self.config['archive_channels']

    def _load_messages(self):
        try:
            self.message_queue = pickle.load(open(save_path, 'rb'))
        except FileNotFoundError:
            self.message_queue = deque()

    def _save_messages(self):
        pickle.dump(self.message_queue, open(save_path, 'wb'))

    def _init_posters(self):
        self.posters = []

        self._load_twitter()
        #self._load_facebook()

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
            if message.channel.id in self.archive_channels:
                await self.queue_message(message=message)

    async def queue_message(self, message=None, content=None, attachments=None):
        if message is not None:
            content = message.content
            attachments = message.attachments

        link = get_url(content)
        text = content.replace(link, '').strip()
        paths = await download_attachments(attachments)

        message = post.Message(text, link, paths)

        self.message_queue.append(message)

        with self.lock:
            self._save_messages()

    @commands.command()
    @helpers.is_me()
    async def queue(self, ctx, *, content: str):
        await ctx.send('Message queued')
        await self.queue_message(content=content, attachments=ctx.message.attachments)

    @commands.command()
    @helpers.is_me()
    async def post(self, ctx):
        self._post()
        await ctx.send('Message posted')


async def download_attachments(attachments):
    paths = []

    for attachment in attachments:
        path = os.path.join(img_path, attachment.filename)
        await attachment.save(path)

        paths.append(path)

    return paths


def get_url(content):
    try:
        link = re.search(r"(?P<url>https?://[^\s]+)", content).group("url")
    except AttributeError:
        link = ''
    return link