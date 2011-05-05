import hikkea.models as model

form = model.Fansub(name='Nanikano', microname='NF')
form.save()

form = model.VideoCodec(name='H.264 AVC', quality='8')
form.save()
form = model.VideoCodec(name='XviD MPEG-4', quality='6')
form.save()
form = model.VideoCodec(name='Windows Media Video V8', quality='5')
form.save()

form = model.AudioCodec(name='MPEG Layer 3', quality='4')
form.save()
form = model.AudioCodec(name='MPEG-4 Audio', quality='4')
form.save()
form = model.AudioCodec(name='Windows Media Audio V7 / V8 / V9', quality='3')
form.save()

form = model.SubtitleCodec(name='HardSub', quality='1')
form.save()
form = model.SubtitleCodec(name='SubRip (srt)', quality='5')
form.save()
form = model.SubtitleCodec(name='Advanced Substation Alpha (SSA/ASS)', quality='10')
form.save()
form = model.SubtitleCodec(name='MicroDVD (sub)', quality='4')
form.save()
form = model.SubtitleCodec(name='Universal Subtitle Format (USF)', quality='10')
form.save()

form = model.AudioHertz(name=48000.0)
form.save()
form = model.AudioHertz(name=44100.0)
form.save()

form = model.AudioChannel(name=1, quality=1)
form.save()
form = model.AudioChannel(name=2, quality=5)
form.save()
form = model.AudioChannel(name=5, quality=8)
form.save()
form = model.AudioChannel(name=8, quality=10)
form.save()

form = model.VideoAspectRatio(name='16:9', relation=1.7777777777777777, quality=10)
form.save()
form = model.VideoAspectRatio(name='4:3', relation=1.3333333333333333, quality=6)
form.save()

form = model.VideoResolution(name='FullHD', width=1920, height=1080, quality=10, aspect=model.VideoAspectRatio.objects.get(id=1))
form.save()
form = model.VideoResolution(name='HD', width=1280, height=720, quality=7, aspect=model.VideoAspectRatio.objects.get(id=1))
form.save()
form = model.VideoResolution(name='SDTV PAL 16:9', width=1024, height=576, quality=6, aspect=model.VideoAspectRatio.objects.get(id=1))
form.save()
form = model.VideoResolution(name='SDTV PAL 16:9', width=1048, height=576, quality=6, aspect=model.VideoAspectRatio.objects.get(id=1))
form.save()
form = model.VideoResolution(name='SDTV PAL* 16:9', width=768, height=432, quality=4, aspect=model.VideoAspectRatio.objects.get(id=1))
form.save()
form = model.VideoResolution(name='SDTV PAL 4:3', width=768, height=576, quality=4, aspect=model.VideoAspectRatio.objects.get(id=2))
form.save()
form = model.VideoResolution(name='SDTV PAL 4:3', width=786, height=576, quality=4, aspect=model.VideoAspectRatio.objects.get(id=2))
form.save()
form = model.VideoResolution(name='SDTV NTSC 16:9', width=872, height=480, quality=4, aspect=model.VideoAspectRatio.objects.get(id=2))
form.save()
form = model.VideoResolution(name='SDTV NTSC 4:3', width=640, height=480, quality=4, aspect=model.VideoAspectRatio.objects.get(id=2))
form.save()
#form = model.VideoResolution(name='HD+', width=1600, height=900, quality=9, aspect=model.VideoAspectRatio.objects.get(id=1))
#form.save()
#form = model.VideoResolution(name='WXGA', width=1360, height=768, quality=8, aspect=model.VideoAspectRatio.objects.get(id=1))
#form.save()

form = model.Container(name='Matrioska', ext='mkv', mime='application/mkv', quality=10)
form.save()
form = model.Container(name='MPEG-4 Parte 14', ext='mp4', mime='video/mp4', quality=7)
form.save()
form = model.Container(name='Audio Video Interleave', ext='avi', mime='video/avi', quality=5)
form.save()