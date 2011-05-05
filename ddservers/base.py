# -*- coding: utf-8 -*-
import random, sys, tempfile, os
import __main__
kaa = __main__.settings.kaa
kaa.metadata = __main__.settings.kaa.metadata


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

AGENTS = [#'Acer E101: ACER E101 Profile/MIDP-2.0 Configuration/CLDC-1.1 UNTRUSTED/1.0',
          #'Alcatel OT-708: Alcatel-OT-708/1.0 Profile/MIDP-2.0 Configuration/CLDC-1.1 ObigoInternetBrowser/Q03C',
          #'Apple iPhone: Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/1A542a Safari/419.3',
          #'S68: SIE-S68/36 UP.Browser/7.1.0.e.18 (GUI) MMP/2.0 Profile/MIDP-2.0 Configuration/CLDC-1.1',
          #'BlackBerry 7100i: BlackBerry7100i/4.1.0 Profile/MIDP-2.0 Configuration/CLDC-1.1 VendorID/103',
          #'Android SDK 1.5r3: Mozilla/5.0 (Linux; U; Android 1.5; de-; sdk Build/CUPCAKE) AppleWebkit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1',
          #'Desire: Mozilla/5.0 (Linux; U; Android 2.1-update1; fr-fr; desire_A8181 Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17',
          #'LG U880: LG/U880/v1.0',
          #'Motorola SLVR L6: MOT-L6/0A.52.2BR MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1',
          #'Nokia 2610: Nokia2610/2.0 (07.04a) Profile/MIDP-2.0 Configuration/CLDC-1.1 UP.Link/6.3.1.20.0',
          #'Treo 650: Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; PalmSource/hspr-H102; Blazer/4.0) 16;320x320',
          #'Samsung A737: SAMSUNG-SGH-A737/UCGI3 SHP/VPP/R5 NetFront/3.4 SMM-MMS/1.2.0 profile/MIDP-2.0 configuration/CLDC-1.1 UP.Link/6.3.1.17.0',
          #'SonyEricsson K510i: SonyEricssonK510i/R4CJ Browser/NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1',
          #'V8301: ZTE-V8301/MB6801_V1_Z1_VN_F1BPa101 Profile/MIDP-2.0 Configuration/CLDC-1.1 Obigo/Q03C',
          'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (FM Scene 4.6.1)',
          ]

class DownloadInterrupt(Exception):
    pass

class Base(object):
    sizes = {'b': 1, 'B': 8, 'KiB': 1024, 'MiB': 1048576.0, 'GiB': 1073741824.0}
    
    def __init__(self):
        self.cookie_j = cookiejar.CookieJar()
        cookie_h = request.HTTPCookieProcessor(self.cookie_j)
        self.opener = request.build_opener(cookie_h)
        #self.opener = request.FancyURLopener()
        self.opener.addheaders = [('User-agent', random.choice(AGENTS))]
        if 'init' in dir(self):
            self.init()

    def progress(self, block_count, block_size, total_size):
        size = (block_count * block_size) / 1024
        if size >= 1024:
            # Sí, este es el método para parar una descarga :P
            raise DownloadInterrupt

    def get_data(self, file):
        data = {}
        info = kaa.metadata.parse(file)
        return info
        

    def download(self, url):
        #request.install_opener(self.opener)
        file = tempfile.mkstemp()[1]
        print(file)
        #try:
            #request.urlretrieve(url, file, self.progress)
        #except DownloadInterrupt:
            #pass
        f = open(file, 'wb')
        f.write(self.opener.open(url).read(1024 * 1024))
        f.close()

        return self.get_data(file)

    def get_float(self, num, size):
        if round(num / size, 1) == num // size:
            num = int(num // size)
        else:
            num = round(num / size, 1)
        return num
    
    def get_size(self, num):
        """Simplificar el tamaño"""
        for size in self.sizes.keys():
            if num / 1024 >  self.sizes[size]:
                pass
            else:
                num = self.get_float(num, self.sizes[size])
                return '%s %s' % (num, size)
        # No se encuentra dentro de los rangos, se usa el último visto
        num = self.get_float(num, self.sizes[size])
        return '%s %s' % (num, size)