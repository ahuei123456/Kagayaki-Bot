import facebook
from bot.onibe.post import Message, Postable


class Facebook(Postable):
    def __init__(self, credentials):
        self._init_api(credentials)

    def _init_api(self, credentials):
        self.facebook = facebook.GraphAPI(access_token=credentials['access_token'])

    def post(self, message: Message):
        self.facebook.put_object(parent_object='me', connection_name='feed', message=message.text, link=message.link)
        pass
