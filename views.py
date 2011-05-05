# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import Context
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.forms.models import modelformset_factory as mff
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.db.models.query import QuerySet
from django.db.models import Q
import json
import copy
import re
import time
from threading import Thread

import hikkea.models as model 
import hikkea.ddservers
from hikkea import filesmanager

# Variables comunes que tendrán todas las páginas
DATA = {
    'sitename': 'Hikkea',
    'lang': 'es-ES',
    }

def transform(data):
    """
    Permite transformar un objeto (con o sin otros
    objetos recursivos) de Django, a objetos de tipo
    Python que puedan ser parseados por JSON
    """
    if isinstance(data, QuerySet):
        data = list(data)
    if isinstance(data, list) or isinstance(data, tuple):
        i = 0
        while i < len(data):
            data[i] = transform(data[i])
            i += 1
    return data

def jsonresponse(data):
    """
    Enviar datos por Ajax usando JSON
    """
    data = transform(data)
    return HttpResponse(json.dumps(data),
                            mimetype='application/javascript')

def response(page, request, new_data):
    """
    Parecido al render_to_response de Django, pero
    incluye adeás las variables comunes de DATA
    (nombre del sitio, idioma, etc.) y permite dualidad
    entre base de Ajax y base normal.
    """
    data = copy.copy(DATA)
    if 'ajax' in request.GET.keys():
        data['base'] = 'ajax.html'
    else:
        data['base'] = 'base.html'
    data.update(new_data)
    return render_to_response(page, data)

def index(request):
    """
    Portada del sitio web
    """
    return response('index.html', request,
                    {'title': 'Inicio - ' + DATA['sitename']})

def edit_release(request, ttype, taction, tid):
    """
    Formulario para Editar o añadir una Release.
    Véase las funciones "ajax_add_packages" y 
    "ajax_search_title", las cuales se encuentran
    estrechamente relacionadas (se realizan peticiones
    mediante Ajax).
    """
    if not model.TitleType.objects.filter(name=ttype):
        return HttpResponseBadRequest()
    form_set = mff(model.Release, form=model.ReleaseForm)
    if taction == 'add':
        action_name = 'Añadiendo'
        form = form_set(queryset=model.Release.objects.none())
    elif model.Release.objects.filter(id=tid):
        # SIN TERMINAR
        title = model.Release.objects.get(id=tid)
        form = form_set(queryset=model.Release.objects.none())
    return response('edit_release.html', request,
                    {'form': form,
                     'title': '%s release - %s' % (action_name, DATA['sitename']),
                     'last_pkg': 0,
                     })

def edit_title(request, ttype, taction, tid):
    """
    Editar o añadir un Title
    """
    if not model.TitleType.objects.filter(name=ttype):
        return HttpResponseBadRequest()
    form_set = mff(model.TitleVersion)
    if taction == 'add':
        action_name = 'Añadiendo'
        form = form_set(queryset=model.TitleVersion.objects.none())
    elif model.Title.objects.filter(id=tid):
        # SIN TERMINAR
        title = model.Title.objects.get(id=tid)
        titleversion = model.TitleVersion.objects.get()
        form = form_set(queryset=model.Title.objects.none())
    return response('edit_title.html', request,
                    {'form': form,
                     'title': '%s release - %s' % (action_name, DATA['sitename']),
                     })

def filters_get_chapter(name):
    """
    Filtros que se aplicarán para impedir errores
    en el get_chapter
    """
    # Se quitan los CRC32
    name = re.sub('\[([a-fA-F0-9]{8})\]', '', name)
    # Se quita la extensión del archivo
    name = '.'.join(name.split('.')[:-1])
    # Se quita el partX
    name = re.sub('\.part\d+$|\.|d+$', '', name)
    return name

def get_chapter(name_a, name_b):
    """
    Esta función halla la primera posición en la que
    hay un número distinto entre 2 archivos. Su uso
    es detectar la posición del número de capítulo
    sin equivocarse con un número del nombre del
    título. Ejemplo:
    2x2 Shinobuden 01.mkv
    2x2 Shinobuden 02.mkv
    En este caso, la posición que cambia será la tercera,
    la del 01 y del 02. El número que se devolverá será
    un 2, ya que el índice comienza por cero (0,1 2).
    En caso de no haber resultados, se devolverá False
    """
    i = 0
    name_a = filters_get_chapter(name_a)
    name_b = filters_get_chapter(name_b)
    # Quita 
    name_b_groups = re.findall('(\d+)', name_b)
    for name_a_group in re.findall('(\d+)', name_a):
        if i > len(name_b_groups):
            return None
        if name_a_group != name_b_groups[i]:
            return i
    return None

def get_packages(text, last_pkg, first_name):
    # Un listado con diccionarios de los links
    links = []
    # Tipo de descarga, p2p o dd
    type_packages = None
    # Un listado con los errores ocurridos
    errors = []
    # El último paquete para ID
    last_pkg = int(last_pkg)
    # Es la primera petición
    if last_pkg:
        first_request = False
    else:
        first_request = True
    # Información del archivo de vídeo
    datafile = False
    # Otra información varia (como el fansub)
    other_data = {}

    # Primeros se buscan links de descarga Directa
    for server in model.DirectDownloadServer.objects.all():
        links_server, text = filesmanager.search_link(server.regex, text)
        if links_server:
            # Se han encontrado enlaces
            type_packages = 'dd'
        else:
            continue
        # Obtener información de los links. Los resultados se
        # Guardan en 'links'
        filesmanager.gets_urls_info(server, links_server, links, errors)
        # Si es la primera petición y el servidor tiene premium,
        # se baja el primer capítulo para ver la información
        if not last_pkg and ddservers[server.name.lower()].premium:
            datafile = filesmanager.get_data_file(server, links)
    
    # ### P2P....
    
    # Detectar el fansub si es la primera petición y el primer
    # capítulo tiene nombre
    if not last_pkg and links[0]['name']:
        microname, fansub = filesmanager.get_fansub(links[0]['name'])
        other_data['fansub_microname'] = microname
        other_data['fansub'] = fansub
    # Intentar detectar el número de capítulo
    filesmanager.get_chapters(links)
    
    packages, unsorted, last_pkg = filesmanager.organize_links(links)
    
    unrecognized = re.findall('([^ ]+):([^ ]+)', text)
    
    
    
    video_data = {'download_type': type_packages}
    video_data['container'] = filesmanager.get_ddbb_data('Container', {'mime': datafile.mime})
    video_data['videocodec'] = filesmanager.get_ddbb_data('VideoCodec', {'name': datafile.video[0].codec})
    
    
    if model.Container.objects.filter(mime=datafile.mime):
        false_post_data['container'] = str(model.Container.objects.get(mime=datafile.mime).id)
    if model.VideoCodec.objects.filter(name=datafile.video[0].codec):
        false_post_data['videocodec'] = \
                             str(model.VideoCodec.objects.get(name=datafile.video[0].codec).id)
    if model.VideoResolution.objects.filter(width=datafile.video[0].width,
                                                               height=datafile.video[0].height):
        false_post_data['resolution'] = str(model.VideoResolution.objects.get(width=datafile.video[0].width,
                                            height=datafile.video[0].height).id)
    if model.AudioCodec.objects.filter(name=datafile.audio[0].codec):
        false_post_data['audiocodec'] = str(model.AudioCodec.objects.get(name=datafile.audio[0].codec).id)
    if 'samplerate' in dir(datafile.audio[0]) and \
                         model.AudioHertz.objects.filter(name=datafile.audio[0].samplerate):
        false_post_data['audiohertz'] = \
           str(model.AudioHertz.objects.get(name=float(datafile.audio[0].samplerate)).id)
    form = model.ReleaseForm(false_post_data)
    return response('edit_release.html', request, {'last_pkg': last_pkg,
                                                   'unsorted': unsorted,
                                                   'packages': packages,
                                                   'first_request': first_request,
                                                   'first_name': links[0]['name'],
                                                   'type_packages': type_packages,
                                                   'form': form,
                                                   'ajax': True,
                                                   'other_data': other_data,
                                                    })

@csrf_exempt
def ajax_add_packages(request):
    text = request.POST['links']
    last_pkg = request.POST.get('last_pkg', '0')
    first_name = request.POST.get('first_name', False)
    get_packages(text, last_pkg, first_name)

def ajax_search_title(request):
    titles = model.Title.objects.filter(name__contains=request.GET['term'])
    titles_list = []
    for title in titles:
        titles_list.append([title.id, title.__unicode__()])
    return jsonresponse(titles_list)

def ajax_search_fansub(request):
    term = request.GET['term']
    qset = (Q(name__contains=term) | Q(microname__contains=term))
    fansubs = model.Fansub.objects.filter(qset)
    fansubs_list = []
    for fansub in fansubs:
        fansubs_list.append([fansub.id, fansub.__unicode__()])
    return jsonresponse(fansubs_list)