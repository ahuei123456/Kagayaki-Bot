from discord.ext import commands


allowed_users = []


def is_me():
    def predicate(ctx):
        return ctx.message.author.id == 144803988963983360
    return commands.check(predicate)


def is_poster():
    def predicate(ctx):
        return ctx.message.author.id in allowed_users
    return commands.check(predicate)
