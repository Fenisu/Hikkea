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
import json
import copy
import re
import time
from threading import Thread

import hikkea.models as model 
import hikkea.ddservers

# Variables comunes que tendrán todas las páginas
DATA = {
    'sitename': 'Hikkea',
    'lang': 'es-ES',
    }

# Se crea un diccionario con los "plugins" para servidores
# de DD soportados.
ddservers = {}
for server in hikkea.ddservers.__all__:
    mod = __import__('hikkea.ddservers', globals(), locals(), [server], 0)
    mod = getattr(mod, server)
    ddservers[server] = mod.Server()

# Extensiones de vídeo
extensions = []
for container in model.Container.objects.all():
    extensions.append(container.ext)

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

def search_link(regex, text):
    """
    Buscar mediante un patrón Regex links en el
    texto dado por el usuario (campo id Links)
    y quitarlos del texto.
    """
    links = re.findall(regex, text)
    for link in links:
        text.replace(link, '')
    return links, text

def filters_get_chapter(name):
    """
    Filtros que se aplicarán para impedir errores
    en el get_chapter
    """
    # Se quitan los CRC32
    name = re.sub('\[([a-fA-F0-9]{8})\]', '', name)
    # Se quita la extensión del archivo
    name = name.split('.')[:-1]
    # Se quita el partX
    name = re.sub('\.part\d+$', '', name)
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
            return False
        if name_a_group != name_b_groups[i]:
            return i
    return False

@csrf_exempt
def ajax_add_packages(request):
    text = request.POST['links']
    links = []
    # Primeros se buscan links de descarga Directa
    type_packages = None
    for server in model.DirectDownloadServer.objects.all():
        links_server, text = search_link(server.regex, text)
        if links_server:
            type_packages = 'dd'
        # El servidor tiene un plugin para detectar datos y
        # comprobar el estado
        if links_server and server.name.lower() in hikkea.ddservers.__all__:
            threads = []
            for link_server in links_server:
                thread = Thread(target=ddservers[server.name.lower()].check,
                                args=(link_server, links))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
            # Llegados aquí, ya todos los links se han comprobado
            datafile = False
            if request.POST['last_pkg'] == '0' and ddservers[server.name.lower()].premium:
                # Detectar los datos del vídeo...
                for link in links:
                    # Se recorren todos los links hasta que se encuentre uno
                    # que funcione y que sea un vídeo
                    if link['status'] and link['name'].split('.')[-1] in extensions:
                        datafile = ddservers[server.name.lower()].download(link['url'])
            # Intentar detectar el número de capítulo
            if len(links) > 1 or request.POST.get('first_name', False):
                # Usar método por comparación de nombres
                name_a = links[0]['name']
                name_b = request.POST.get('first_name', request.POST['first_name'])
                igroup = get_chapter(name_a, name_b)
            else:
                # El número de capítulo será el primer número que aparezca
                igroup = 0
            if isinstance(igroup, int):
                for link in links:
                    try:
                        link['chapter'] = int(re.findall('(\d+)', link['name'])[igroup])
                    except IndexError:
                        pass
            #print(datafile)
            last_package = int(request.POST.get('last_pkg', '0'))
            packages = {}
            unsorted = []
            for link in links:
                if 'chapter' in link:
                    if not link['chapter'] in packages.keys() and type_packages == 'dd':
                        packages[link['chapter']] = {}
                    if not link['chapter'] in packages.keys() and type_packages == 'p2p':
                        packages[link['chapter']] = []
                    if type_packages == 'dd':
                        # Se busca si es una de varias partes
                        part = re.findall('\.(\d+)$|\.part(\d+)', link.url)
                        if part:
                            part = int(part[0])
                        else:
                            part = 1
                        packages[link['chapter']] = {part: link}
                    elif type_packages == 'p2p':
                        packages[link['chapter']].append(link)
                else:
                    unsorted.append(link)
        # Como solo puede haber 1 server por Release, se ignoran los demás
        break
    unrecognized = re.findall('([^ ]+):([^ ]+)', text)

def ajax_search_title(request):
    titles = model.Title.objects.filter(name__contains=request.GET['term'])
    titles_list = []
    for title in titles:
        titles_list.append([title.id, title.__unicode__()])
    return jsonresponse(titles_list)