from discord.ext import commands


def is_me():
    def predicate(ctx):
        return ctx.message.author.id == 144803988963983360
    return commands.check(predicate)