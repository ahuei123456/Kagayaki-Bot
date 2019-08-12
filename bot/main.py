from discord.ext import commands
from bot.mainserver.quizbot import QuizBot
from bot.onibe.onibebot import OnibeBot
import os
import json
import logging


description = "testing a new quiz bot"
bot = commands.Bot(command_prefix='>', description=description)
bot.owner_id = 144803988963983360


def load_credentials():
    path = os.path.join(os.getcwd(), 'conf', 'credentials.json')
    with open(path) as f:
        return json.load(f)


@bot.event
async def on_ready():
    logging.info(f'Logged in as: {bot.user.name} (ID: {bot.user.id})')


if __name__ == "__main__":
    credentials = load_credentials()

    bot.add_cog(QuizBot(bot))
    bot.add_cog(OnibeBot(bot))
    bot.run(credentials['discord']['token'])