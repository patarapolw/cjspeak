import subprocess
import sys
import atexit
from pathlib import Path
import json
import regex
from urllib.parse import quote

from .util import is_html


class SpeakServer:
    def __init__(self, port=29633, lang='zh_cn'):
        self.port = port
        self.server = subprocess.Popen([
            'gunicorn',
            'html_speak.server:api',
            '-b', f'127.0.0.1:{self.port}'
        ])
        self.lang = lang

        env_python = Path(sys.argv[0]).name

        if 'ipykernel' in env_python:
            atexit.register(self.close)
        elif 'pydev' in env_python:
            print('hello')
            atexit.register(self.close)
            # signal.signal(signal.SIGINT, lambda s, f: self.close())
        else:
            try:
                self.server.wait()
            except KeyboardInterrupt:
                self.close()

    def close(self):
        self.server.kill()

    def view(self, obj, lang=None):
        if not lang:
            lang = self.lang

        return SpeakableHTML(obj, lang, self.port)


class SpeakableHTML:
    def __init__(self, obj, lang, port):
        self.obj = obj
        self.lang = lang
        self.port = port

    def _repr_html_(self):
        def _sub(x):
            vocab = x.group(1)

            return f'''
            <div onclick="fetch('http://localhost:{self.port}/?s={quote(vocab)}&lang={self.lang}')"
                    class="speakable">
                {vocab}
            </div>
            '''

        s = '''
        <style>
        .speakable {
            color: blue;
            text-decoration: underline; 
            display: inline;
        }
        </style>
        '''
        s += json.dumps(self.obj, cls=CustomEncoder, indent=4, ensure_ascii=False, default=repr)\
            .replace('\n', '<br/>')\
            .replace(' ', '&nbsp;')

        if self.lang.startswith('ja'):
            regex_entity = r'([\p{IsHan}\p{IsBopo}\p{IsHira}\p{IsKatakana}\p{Block=CJK_Symbols_And_Punctuation}]+)'
        elif self.lang.startswith('zh'):
            regex_entity = r'([\p{IsHan}\p{Block=CJK_Symbols_And_Punctuation}]+)'
        else:
            return s

        return regex.sub(regex_entity, _sub, s)


class CustomEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        if isinstance(o, str) and is_html(o):
            return o
        else:
            return json.JSONEncoder.iterencode(self, o, _one_shot)
