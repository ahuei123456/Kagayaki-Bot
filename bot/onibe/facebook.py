import facebook
import logging
from bot.onibe.post import Message, Postable

logger = logging.getLogger(__name__)


class Facebook(Postable):
    def __init__(self, credentials):
        self._init_api(credentials)

    def _init_api(self, credentials):
        logger.info('Initializing Facebook')
        self.facebook = facebook.GraphAPI(access_token=credentials['access_token'])
        logger.info('Successfully logged in to Facebook')

    def post(self, message: Message):
        logger.info('Posting to Facebook')
        if message.media is not None and len(message.media) > 0:
            self.facebook.put_photo(image=open(message.media, 'rb'), caption=f'{message.text}\n\n{message.link}')
        else:
            self.facebook.put_object(parent_object='me', connection_name='feed', message=message.text,
                                     link=message.link)

        logger.info('Successfully posted to Facebook')

    def newest(self):
        pass

