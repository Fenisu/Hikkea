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

@csrf_exempt
def edit_release(request, ttype, taction, tid):
    """
    Formulario para Editar o añadir una Release.
    Véase las funciones "ajax_add_packages" y 
    "ajax_search_title", las cuales se encuentran
    estrechamente relacionadas (se realizan peticiones
    mediante Ajax).
    """
    form_set = mff(model.Release, form=model.ReleaseForm)
    if request.method == "POST" and taction == 'add':
        f = form_set(request.POST, queryset=model.Release.objects.none())
        # El usuario se pone manualmente en el modo en desarrollo
        f.data['form-0-user'] = '1'
        f.user = model.User.objects.get(id=1)
        files = {}
        pkgs = {}
        chapters = {}
        for key, value in request.POST.items():
            key = key.split('_')
            if key[0] == 'file':
                dct = files
            elif key[0] == 'pkg':
                dct = pkgs
            else:
                continue
            if not int(key[1]) in dct.keys():
                dct[int(key[1])] = {}
            dct[int(key[1])][key[2]] = value
        print(files)
        print(pkgs)
        print(f.errors)
        f.save()

        if request.POST['form-0-download_type'] == 'dd':
            for file in files.values():
                if not file['status'] == 'True': continue
                new_file = model.DirectDownload()
                new_file.url = file['url']
                new_file.filename = file['name']
                new_file.size = filesmanager.get_size(file['size2'])
                new_file.server = model.DirectDownloadServer.objects.get(
                    name=file['server'].title(),
                )
                new_file.online = True
                #new_file.checksum = # Para uso posteriormente
                new_file.part = file['part']
                new_file.save()
                if not file['chapter'] in chapters.keys():
                    chapters[file['chapter']] = []
                chapters[file['chapter']].append(new_file)
            for pkg in pkgs.values():
                new_pkg = model.DirectDownloadPackage()
                new_pkg.name = pkg['name']
                total_size = 0
                for file in chapters[pkg['chapter']]:
                    new_pkg.files.add(file.id)
                    total_size += file.size
                new_pkg.size = total_pkg
                new_pkg.release = f
                
    else:
        if not model.TitleType.objects.filter(name=ttype):
            return HttpResponseBadRequest()
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
                        'arg0': ttype,
                        'arg1': taction,
                        'arg2': tid,
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
        filesmanager.get_urls_info(server, links_server, links, errors)
        # Si es la primera petición y el servidor tiene premium,
        # se baja el primer capítulo para ver la información
        if not last_pkg and filesmanager.ddservers[server.name.lower()].premium:
            datafile = filesmanager.get_data_file(server, links)
    
    # ### P2P....
    
    
    if not links:
        return
    # Detectar el fansub si es la primera petición y el primer
    # capítulo tiene nombre
    if not last_pkg and links[0]['name']:
        microname, fansub = filesmanager.get_fansub(links[0]['name'])
        other_data['fansub_microname'] = microname
        other_data['fansub'] = fansub
    # Intentar detectar el número de capítulo
    filesmanager.get_chapters(links, first_name)
    packages, unsorted, last_pkg = filesmanager.organize_links(links, last_pkg,
                                                               type_packages)
    unrecognized = re.findall('([^ ]+):([^ ]+)', text)
    video_data = {'download_type': type_packages}
    if datafile:
        video_data['container'] = filesmanager.get_ddbb_data('Container',
                                                {'mime': datafile.mime})
        video_data['videocodec'] = filesmanager.get_ddbb_data('VideoCodec', 
                                                {'name': datafile.video[0].codec})
        video_data['resolution'] = filesmanager.get_ddbb_data('VideoResolution', 
                                                {'width': datafile.video[0].width,
                                                'height': datafile.video[0].height})
        video_data['audiocodec'] = filesmanager.get_ddbb_data('AudioCodec', 
                                                {'name': datafile.audio[0].codec})
        video_data['audiohertz'] = filesmanager.get_ddbb_data('AudioHertz', 
                                                {'name': float(datafile.audio[0].samplerate)})
    
    return  {
        'last_pkg': last_pkg,
        'unsorted': unsorted,
        'packages': packages,
        'first_request': first_request,
        'links': links,
        'type_packages': type_packages,
        'ajax': True,
        'errors': errors,
        'other_data': other_data,
        'video_data': video_data,
    }

@csrf_exempt
def ajax_add_packages(request):
    text = request.POST['links']
    last_pkg = request.POST.get('last_pkg', '0')
    first_name = request.POST.get('first_name', False)
    data = get_packages(text, last_pkg, first_name)
    if not data:
        return response('edit_packages_ajax_msg.html', request,{
            'messages': ['No se encontraron links.'], 
        })
    form = model.ReleaseForm(data['video_data'])
    return response('edit_release.html', request, {
        'last_pkg': data['last_pkg'],
        'unsorted': data['unsorted'],
        'packages': data['packages'],
        'first_request': data['first_request'],
        'first_name': data['links'][0]['name'],
        'type_packages': data['type_packages'],
        'form': form,
        'ajax': True,
        'other_data': data['other_data'],
        'arg0': request.POST['arg0'],
        'arg1': request.POST['arg1'],
        'arg2': request.POST['arg2'],
    })

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