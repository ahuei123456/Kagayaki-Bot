from bot.onibe.post import Message, Postable
import os
import tweepy

save_path = os.path.join(os.getcwd(), 'data', 'tweets.sav')


class Twitter(Postable):
    def __init__(self, credentials):
        self._init_api(credentials)

    def _init_api(self, credentials):
        c_key = credentials['client_key']
        c_secret = credentials['client_secret']
        a_token = credentials['access_token']
        a_secret = credentials['access_secret']
        auth = tweepy.OAuthHandler(c_key, c_secret)
        auth.set_access_token(a_token, a_secret)

        self.twitter = tweepy.API(auth)

    def post(self, message: Message):
        try:
            media_ids = []

            for fp in message.media:
                media_ids.append(self.twitter.media_upload(fp))

            self.twitter.update_status(message.text, media_ids=media_ids)
        except IndexError:
            pass
