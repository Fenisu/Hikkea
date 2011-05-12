from kaa.metadata.video.mp4 import MPEG4
from kaa.metadata.video import core
# python imports
import zlib
import logging
import StringIO
import struct

# get logging object
log = logging.getLogger('metadata')


# http://developer.apple.com/documentation/QuickTime/QTFF/index.html
# http://developer.apple.com/documentation/QuickTime/QTFF/QTFFChap4/\
#     chapter_5_section_2.html#//apple_ref/doc/uid/TP40000939-CH206-BBCBIICE
# Note: May need to define custom log level to work like ATOM_DEBUG did here

QTUDTA = {
    'nam': 'title',
    'aut': 'artist',
    'cpy': 'copyright'
}

QTLANGUAGES = {
    0 : "en",
    1 : "fr",
    2 : "de",
    3 : "it",
    4 : "nl",
    5 : "sv",
    6 : "es",
    7 : "da",
    8 : "pt",
    9 : "no",
    10 : "he",
    11 : "ja",
    12 : "ar",
    13 : "fi",
    14 : "el",
    15 : "is",
    16 : "mt",
    17 : "tr",
    18 : "hr",
    19 : "Traditional Chinese",
    20 : "ur",
    21 : "hi",
    22 : "th",
    23 : "ko",
    24 : "lt",
    25 : "pl",
    26 : "hu",
    27 : "et",
    28 : "lv",
    29 : "Lappish",
    30 : "fo",
    31 : "Farsi",
    32 : "ru",
    33 : "Simplified Chinese",
    34 : "Flemish",
    35 : "ga",
    36 : "sq",
    37 : "ro",
    38 : "cs",
    39 : "sk",
    40 : "sl",
    41 : "yi",
    42 : "sr",
    43 : "mk",
    44 : "bg",
    45 : "uk",
    46 : "be",
    47 : "uz",
    48 : "kk",
    49 : "az",
    50 : "AzerbaijanAr",
    51 : "hy",
    52 : "ka",
    53 : "mo",
    54 : "ky",
    55 : "tg",
    56 : "tk",
    57 : "mn",
    58 : "MongolianCyr",
    59 : "ps",
    60 : "ku",
    61 : "ks",
    62 : "sd",
    63 : "bo",
    64 : "ne",
    65 : "sa",
    66 : "mr",
    67 : "bn",
    68 : "as",
    69 : "gu",
    70 : "pa",
    71 : "or",
    72 : "ml",
    73 : "kn",
    74 : "ta",
    75 : "te",
    76 : "si",
    77 : "my",
    78 : "Khmer",
    79 : "lo",
    80 : "vi",
    81 : "id",
    82 : "tl",
    83 : "MalayRoman",
    84 : "MalayArabic",
    85 : "am",
    86 : "ti",
    87 : "om",
    88 : "so",
    89 : "sw",
    90 : "Ruanda",
    91 : "Rundi",
    92 : "Chewa",
    93 : "mg",
    94 : "eo",
    128 : "cy",
    129 : "eu",
    130 : "ca",
    131 : "la",
    132 : "qu",
    133 : "gn",
    134 : "ay",
    135 : "tt",
    136 : "ug",
    137 : "Dzongkha",
    138 : "JavaneseRom",
}

AUDIO_IDS = {
    1: 'AAC Main',
    2: 'AAC LC',
    3: 'AAC SSR',
    4: 'AAC LTP',
    5: 'SBR',
    6: 'AAC Scalable',
    7: 'TwinVQ',
    8: 'CELP',
    9: 'HVXC',
    12: 'TTSI',
    13: 'Main synthesis',
    14: 'Wavetable synthesis',
    15: 'General MIDI',
    16: 'Algorithmic Synthesis and Audio Effects',
    17: 'ER AAC LC',
    19: 'ER AAC LTP',
    20: 'ER AAC Scalable',
    21: 'ER TwinVQ',
    22: 'ER BSAC',
    23: 'ER AAC LD',
    24: 'ER CELP',
    25: 'ER HVXC',
    26: 'ER HILN',
    27: 'ER Parametric',
    28: 'SSC',
    29: 'PS',
    30: 'MPEG Surround',
    32: 'MPEG-1/2 Layer-1',
    33: 'MPEG-1/2 Layer-2',
    34: 'MPEG-1/2 Layer-3',
    35: 'DST',
    36: 'ALS',
    37: 'SLS',
    38: 'SLS non-core',
    39: 'ER AAC ELD',
    40: 'SMR',
    41: 'SMR Main',
    42: 'USAC',
    43: 'SAOC',
    44: 'LD MPEG Surround',
    45: 'USAC',
}

def _readatom(self, file):
    s = file.read(8)
    if len(s) < 8:
        return 0

    atomsize,atomtype = struct.unpack('>I4s', s)
    log.debug((atomsize, atomtype))
    if not str(atomtype).decode('latin1').isalnum():
        # stop at nonsense data
        return 0

    log.debug('%s [%X]' % (atomtype,atomsize))

    if atomtype == 'udta':
        # Userdata (Metadata)
        pos = 0
        tabl = {}
        i18ntabl = {}
        atomdata = file.read(atomsize-8)
        while pos < atomsize-12:
            (datasize, datatype) = struct.unpack('>I4s', atomdata[pos:pos+8])
            log.debug((datasize, datatype))
            if ord(datatype[0]) == 169:
                # i18n Metadata...
                mypos = 8+pos
                while mypos + 4 < datasize+pos:
                    # first 4 Bytes are i18n header
                    (tlen, lang) = struct.unpack('>HH', atomdata[mypos:mypos+4])
                    log.debug((tlen, lang))
                    i18ntabl[lang] = i18ntabl.get(lang, {})
                    l = atomdata[mypos+4:mypos+tlen+4]
                    i18ntabl[lang][datatype[1:]] = l
                    mypos += tlen+4
            elif datatype == 'WLOC':
                # Drop Window Location
                pass
            else:
                if ord(atomdata[pos+8:pos+datasize][0]) > 1:
                    tabl[datatype] = atomdata[pos+8:pos+datasize]
            pos += datasize
        if len(i18ntabl.keys()) > 0:
            for k in i18ntabl.keys():
                if QTLANGUAGES.has_key(k) and QTLANGUAGES[k] == 'en':
                    self._appendtable('QTUDTA', i18ntabl[k])
                    self._appendtable('QTUDTA', tabl)
        else:
            log.debug('NO i18')
            self._appendtable('QTUDTA', tabl)

    elif atomtype == 'trak':
        atomdata = file.read(atomsize-8)
        pos = 0
        trackinfo = {}
        tracktype = None
        while pos < atomsize-8:
            (datasize, datatype) = struct.unpack('>I4s', atomdata[pos:pos+8])
            log.debug((datasize, datatype))

            if datatype == 'tkhd':
                tkhd = struct.unpack('>6I8x4H36xII', atomdata[pos+8:pos+datasize])
                log.debug(tkhd)
                trackinfo['width'] = tkhd[10] >> 16
                trackinfo['height'] = tkhd[11] >> 16
                trackinfo['id'] = tkhd[3]

                try:
                    # XXX Timestamp of Seconds is since January 1st 1904!
                    # XXX 2082844800 is the difference between Unix and
                    # XXX Apple time. FIXME to work on Apple, too
                    self.timestamp = int(tkhd[1]) - 2082844800
                except Exception, e:
                    log.exception('There was trouble extracting timestamp')

            elif datatype == 'mdia':
                pos      += 8
                datasize -= 8
                log.debug('--> mdia information')

                while datasize:
                    mdia = struct.unpack('>I4s', atomdata[pos:pos+8])
                    log.debug(mdia)
                    if mdia[1] == 'mdhd':
                        mdhd = struct.unpack('>IIIIIhh', atomdata[pos+8:pos+8+24])
                        log.debug(mdhd)
                        trackinfo['samplerate'] = float(mdhd[3])
                        # duration / time scale
                        trackinfo['length'] = mdhd[4] / mdhd[3]
                        if mdhd[5] in QTLANGUAGES:
                            trackinfo['language'] = QTLANGUAGES[mdhd[5]]
                        # mdhd[6] == quality
                        self.length = max(self.length, mdhd[4] / mdhd[3])
                    elif mdia[1] == 'minf':
                        # minf has only atoms inside
                        pos -=      (mdia[0] - 8)
                        datasize += (mdia[0] - 8)
                    elif mdia[1] == 'stbl':
                        # stbl has only atoms inside
                        pos -=      (mdia[0] - 8)
                        datasize += (mdia[0] - 8)
                    elif mdia[1] == 'hdlr':
                        hdlr = struct.unpack('>I4s4s', atomdata[pos+8:pos+8+12])
                        log.debug(hdlr)
                        if hdlr[1] == 'mhlr':
                            if hdlr[2] == 'vide':
                                tracktype = 'video'
                            if hdlr[2] == 'soun':
                                tracktype = 'audio'
                    elif mdia[1] == 'stsd':
                        stsd = struct.unpack('>2I', atomdata[pos+8:pos+8+8])
                        log.debug(stsd)
                        if stsd[1] > 0:
                            codec = atomdata[pos+16:pos+16+8]
                            codec = struct.unpack('>I4s', codec)
                            log.debug(codec)
                            trackinfo['codec'] = codec[1]
                            if codec[1] == 'jpeg':
                                tracktype = 'image'
                    elif mdia[1] == 'dinf':
                        dref = struct.unpack('>I4s', atomdata[pos+8:pos+8+8])
                        log.debug(dref)
                        log.debug('  --> %s, %s (useless)' % mdia)
                        if dref[1] == 'dref':
                            num = struct.unpack('>I', atomdata[pos+20:pos+20+4])[0]
                            log.debug(num)
                            rpos = pos+20+4
                            for ref in range(num):
                                # FIXME: do somthing if this references
                                ref = struct.unpack('>I3s', atomdata[rpos:rpos+7])
                                log.debug(ref)
                                data = atomdata[rpos+7:rpos+ref[0]]
                                rpos += ref[0]
                    else:
                        if mdia[1].startswith('st'):
                            log.debug('  --> %s, %s (sample)' % mdia)
                        elif mdia[1] in ('vmhd',) and not tracktype:
                            # indicates that this track is video
                            tracktype = 'video'
                        elif mdia[1] in ('vmhd', 'smhd') and not tracktype:
                            # indicates that this track is audio
                            tracktype = 'audio'
                        else:
                            log.debug('  --> %s, %s (unknown)' % mdia)

                    pos      += mdia[0]
                    datasize -= mdia[0]

            elif datatype == 'udta':
                log.debug(struct.unpack('>I4s', atomdata[:8]))
            else:
                if datatype == 'edts':
                    log.debug('--> %s [%d] (edit list)' % \
                                (datatype, datasize))
                else:
                    log.debug('--> %s [%d] (unknown)' % \
                                (datatype, datasize))
            pos += datasize

        info = None
        if tracktype == 'video':
            info = core.VideoStream()
            self.video.append(info)
        if tracktype == 'audio':
            info = core.AudioStream()
            self.audio.append(info)
            if trackinfo['codec'] == 'mp4a':
                trackinfo['codec'] = AUDIO_IDS[trackinfo['id']]
        if info:
            for key, value in trackinfo.items():
                # Se establecen los valores
                #print(key, value)
                setattr(info, key, value)

    elif atomtype == 'mvhd':
        # movie header
        mvhd = struct.unpack('>6I2h', file.read(28))
        log.debug(mvhd)
        self.length = max(self.length, mvhd[4] / mvhd[3])
        self.volume = mvhd[6]
        file.seek(atomsize-8-28,1)


    elif atomtype == 'cmov':
        # compressed movie
        datasize, atomtype = struct.unpack('>I4s', file.read(8))
        log.debug((datasize, atomtype))
        if not atomtype == 'dcom':
            return atomsize

        method = struct.unpack('>4s', file.read(datasize-8))[0]
        log.debug(method)

        datasize, atomtype = struct.unpack('>I4s', file.read(8))
        log.debug((datasize, atomtype))
        if not atomtype == 'cmvd':
            return atomsize

        if method == 'zlib':
            data = file.read(datasize-8)
            try:
                decompressed = zlib.decompress(data)
            except Exception, e:
                try:
                    decompressed = zlib.decompress(data[4:])
                except Exception, e:
                    log.exception('There was a proble decompressiong atom')
                    return atomsize

            decompressedIO = StringIO.StringIO(decompressed)
            while self._readatom(decompressedIO):
                pass

        else:
            log.info('unknown compression %s' % method)
            # unknown compression method
            file.seek(datasize-8,1)

    elif atomtype == 'moov':
        # decompressed movie info
        while self._readatom(file):
            pass

    elif atomtype == 'mdat':
        pos = file.tell() + atomsize - 8
        # maybe there is data inside the mdat
        log.info('parsing mdat')
        while self._readatom(file):
            pass
        log.info('end of mdat')
        file.seek(pos, 0)


    elif atomtype == 'rmra':
        # reference list
        while self._readatom(file):
            pass

    elif atomtype == 'rmda':
        # reference
        atomdata = file.read(atomsize-8)
        pos   = 0
        url = ''
        quality = 0
        datarate = 0
        while pos < atomsize-8:
            (datasize, datatype) = struct.unpack('>I4s', atomdata[pos:pos+8])
            log.debug((datasize, datatype))
            if datatype == 'rdrf':
                rflags, rtype, rlen = struct.unpack('>I4sI', atomdata[pos+8:pos+20])
                log.debug((rflags, rtype, rlen))
                if rtype == 'url ':
                    url = atomdata[pos+20:pos+20+rlen]
                    if url.find('\0') > 0:
                        url = url[:url.find('\0')]
            elif datatype == 'rmqu':
                quality = struct.unpack('>I', atomdata[pos+8:pos+12])[0]
                log.debug(quality)

            elif datatype == 'rmdr':
                datarate = struct.unpack('>I', atomdata[pos+12:pos+16])[0]
                log.debug(datarate)

            pos += datasize
        if url:
            self._references.append((url, quality, datarate))

    else:
        if not atomtype in ('wide', 'free'):
            log.info('unhandled base atom %s' % atomtype)

        # Skip unknown atoms
        try:
            file.seek(atomsize-8,1)
        except IOError:
            return 0

    return atomsize

setattr(MPEG4, '_readatom', _readatom)