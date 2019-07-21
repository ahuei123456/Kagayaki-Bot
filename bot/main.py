from discord.ext import commands
from discord import client
from bot.mainserver.quizbot import QuizBot
import os
import json
import logging


description = "testing a new quiz bot"
bot = commands.Bot(command_prefix='?afsdihfoaijidohfaoe', description=description)


def load_credentials():
    path = os.path.join(os.getcwd(), 'conf', 'credentials.json')
    with open(path) as f:
        return json.load(f)


@client.event
async def on_ready():
    logging.info(f'Logged in as: {bot.user.name} (ID: {bot.id})')


@client.event
async def on_error(event, *args, **kwargs):
    logging.error(event)
    logging.error(args)
    logging.error(kwargs)


if __name__ == "__main__":
    credentials = load_credentials()

    bot.add_cog(QuizBot(bot))
    bot.run(credentials['discord']['token'])