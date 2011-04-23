# -*- coding: utf-8 -*-
from django.contrib import admin
import hikkea.models as hm # Hikkea Models

admin.site.register(hm.TitleType)
admin.site.register(hm.Title)
admin.site.register(hm.TitleVersion)
admin.site.register(hm.P2PDownloadType)
admin.site.register(hm.P2PDownloadProvider)
admin.site.register(hm.DirectDownloadServer)
admin.site.register(hm.Container)