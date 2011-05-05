# -*- coding: utf-8 -*-

import re, sys
from . import base
from . import shadow
_entity_re = re.compile(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));")

if sys.version_info < (3,0):
    import urllib as request
    parse = request
    import urllib2
    for method in dir(urllib2):
        setattr(request, method, getattr(urllib2, method))
    import cookielib as cookiejar
    
else:
    from http import cookiejar
    from urllib import parse, request

class Server(base.Base):
    server_name = 'megaupload'
    check_url = "http://www.megaupload.com/mgr_linkcheck.php"
    premium = True
    
    def init(self):
        post = parse.urlencode({"login": "1", "redir": "1",
                                "username": shadow.servers['megaupload'][0],
                                "password": shadow.servers['megaupload'][1],
                                })
        self.opener.open('http://www.megaupload.com/?c=login', post).read()
        # Si la autentificación es correcta, se devuelve True
        if len(self.cookie_j):
            return True

    def check(self, url, links=False, errors=None):
        """Checkear el estado de un enlace."""
        data = request.urlopen(self.check_url,
                                parse.urlencode({"id0": url.split('d=')[1]}), 5).read()
        data = str(data)
        if len(data) > 4:
            status = True
            name = self.unescape_entities(data.split('n=')[1])
            size = int(data.split('s=')[1].split('&')[0])
            size2 = self.get_size(size)
        else:
            status = False
            name = url
            size = -1

        val = {
            'status': status,
            'name': name,
            'size': size,
            'size2': size2,
            'url': url,
            'message': '',
            'server': self.server_name,
        }
        if links != False:
            links.append(val)
        return val

    def unescape_entities(self, text):
        return _entity_re.sub(self._replace_entity, text)

    def _replace_entity(self, match):
        text = match.group(1)
        if text[0] =='#':
            text = text[1:]
            try:
                if text[0] in 'xX':
                    c = int(text[1:], 16)
                else:
                    c = int(text)
                return unichr(c)
            except ValueError:
                return match.group(0)
        else:
            try:
                return unichr(name2codepoint[text])
            except (ValueError, KeyError):
                return match.group(0)