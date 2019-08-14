from bot.onibe.post import Message, Postable
import html
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

    def newest(self):
        statuses = self.twitter.user_timeline(count=1, tweet_mode='extended')
        status = statuses[0]
        return build_message(status)


def is_retweet(status):
    return hasattr(status, 'retweeted_status')


def get_status(status):
    if is_retweet(status):
        return status.retweeted_status

    return status


def get_text(status):
    status = get_status(status)
    try:
        text = status.extended_tweet['full_text']
    except AttributeError:
        text = status.full_text

    try:
        medias = get_media_entities(status)
        url = medias[0]['url']
        text = text.replace(url, '').strip()
    except IndexError:
        pass

    return html.unescape(text)


def get_media_entities(status):
    status = get_status(status)

    try:
        try:
            e_status = status.extended_tweet
            return e_status['extended_entities']['media']
        except AttributeError:
            return status.extended_entities['media']
    except KeyError:
        return []


def get_first_url(status):
    status = get_status(status)

    try:
        return status.entities['urls'][0]
    except (AttributeError, KeyError, IndexError):
        return ''


def get_first_photo(status):
    medias = get_media_entities(status)

    try:
        media = medias[0]
        if media['type'] == 'photo':
            return media['media_url']
    except IndexError:
        return None

    return None


def build_message(status):
    text = get_text(status)
    link = get_first_url(status)
    media = get_first_photo(status)

    return Message(0, 0, text, link, media)
