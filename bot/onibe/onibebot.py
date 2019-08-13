from bot.helpers import helpers
from bot.onibe.twitter import Twitter
from bot.onibe.facebook import Facebook
from bot.onibe import post
from collections import deque
from datetime import datetime
from datetime import timedelta
from discord.ext import commands
from discord import File, Message
from threading import Lock, Thread
import asyncio
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
        helpers.allowed_users = self.config['allowed_users']

    def _load_messages(self):
        try:
            self.message_queue = pickle.load(open(save_path, 'rb'))
        except FileNotFoundError:
            self.message_queue = deque()

    def _save_messages(self):
        pickle.dump(self.message_queue, open(save_path, 'wb'))

    def _init_posters(self):
        self.posters = []

        #self._load_twitter()
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

    def _clear(self):
        self.message_queue.clear()

        with self.lock:
            self._save_messages()

    async def react_complete(self, message_id: int, channel_id: int):
        channel = await self.bot.get_channel(channel_id)
        original = await channel.fetch_message(message_id)

        await original.add_reaction('✅')

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.id != self.bot.user.id:
            if message.channel.id in self.archive_channels:
                await self.queue_message(message=message)
                await message.add_reaction('⏲')

    async def queue_message(self, message=None, content=None):
        if content is None:
            content = message.content

        link = get_url(content)
        text = content.replace(link, '').strip()
        paths = await download_attachments(message.attachments)

        message = post.Message(message.id, message.channel.id, text, link, '' if len(paths) == 0 else paths[0])

        self.message_queue.append(message)

        with self.lock:
            self._save_messages()

    @commands.command()
    @helpers.is_poster()
    async def queue(self, ctx, *, content: str):
        await ctx.send('Message queued')
        await self.queue_message(ctx.message, content)

    @commands.command()
    @helpers.is_poster()
    async def post(self, ctx):
        self._post()
        await ctx.send('Message posted')

    @commands.command()
    @helpers.is_poster()
    async def clear(self, ctx):
        self._clear()
        await ctx.send('Queue cleared')

    @commands.command()
    @helpers.is_poster()
    async def dump(self, ctx):
        for message in self.message_queue:
            text = f'{message.text} {message.link}'
            await ctx.send(content=text, file=File(open(message.media, 'rb')))

    @commands.command()
    async def next(self, ctx):
        now = datetime.now()
        if now.hour > 8:
            now += timedelta(days=1)

        now = now.replace(hour=8, minute=0, second=0, microsecond=0)

        content = f'Next post will be made on {now.strftime("%b %d, %H:%M %Z")}'

        await ctx.send(content)

    @commands.command()
    @helpers.is_me()
    async def approve(self, ctx):
        allowed_users = [user.id for user in ctx.message.mentions]
        helpers.allowed_users.extend(allowed_users)

        text = f'Temporarily added users {allowed_users} to post helpers'

        await ctx.send(content=text)


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
