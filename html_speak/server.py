import falcon
from ttslib.local import tts


class SpeakResource:
    def on_get(self, req, resp):
        tts(req.params['s'], req.params['lang'])


api = falcon.API()
api.add_route('/', SpeakResource())
