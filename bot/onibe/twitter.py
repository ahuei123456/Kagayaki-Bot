from bot.onibe.post import Message, Postable
import logging
import tweepy

logger = logging.getLogger(__name__)


class Twitter(Postable):
    def __init__(self, credentials):
        self._init_api(credentials)

    def _init_api(self, credentials):
        logger.info('Initializing Twitter')

        c_key = credentials['client_key']
        c_secret = credentials['client_secret']
        a_token = credentials['access_token']
        a_secret = credentials['access_secret']
        auth = tweepy.OAuthHandler(c_key, c_secret)
        auth.set_access_token(a_token, a_secret)

        self.twitter = tweepy.API(auth)
        logger.info('Successfully logged in to Twitter')

    def post(self, message: Message):
        logger.info('Posting to Twitter')
        try:
            media_ids = []

            if message.media is not None and len(message.media) > 0:
                media_ids.append(self.twitter.media_upload(message.media).media_id)

            text = f'{message.text} {message.link}'

            try:
                self.twitter.update_status(text, media_ids=media_ids)
            except tweepy.error.TweepError as e:
                print(e)
            logger.info('Successfully posted to Twitter')
        except IndexError:
            pass
