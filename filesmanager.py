# -*- coding: utf-8 -*-

# Se crea un diccionario con los "plugins" para servidores
# de DD soportados.
import hikkea.ddservers
import re
from threading import Thread
import hikkea.models as model 

ddservers = {}
for server in hikkea.ddservers.__all__:
    mod = __import__('hikkea.ddservers', globals(), locals(), [server], 0)
    mod = getattr(mod, server)
    ddservers[server] = mod.Server()

SIZES = {
    'T': 1 * 1024 * 1024 * 1024 * 1024,
    'G': 1 * 1024 * 1024 * 1024,
    'M': 1 * 1024 * 1024,
    'K': 1 * 1024,
    'B': 1,
    }

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

def get_data_file(server, links):
    # Detectar los datos del vídeo...
    extensions = model.Container().extensions()
    for link in links:
        # Se recorren todos los links hasta que se encuentre uno
        # que funcione y que sea un vídeo
        if link['status'] and link['name'].split('.')[-1] in extensions:
            return ddservers[server.name.lower()].download(link['url'])
    return False

def get_fansub(name):
    """
    Obtener el nombre del fansub a partir del
    nombre del archivo. Para esto, se lee el
    primer texto entre corchetes que haya en
    el nombre de archivo, y se comparará con
    la base de datos de fansubs según el
    micronombre.
    """
    microname = re.findall('\[([^\]]+)\]', name)
    if microname and model.Fansub.objects.filter(microname=microname[0]):
        fansub = model.Fansub.objects.get(microname=microname[0])
        return microname, fansub
    else:
        return '', ''

def organize_links(links, last_pkg, type_packages):
    """
    Organizar los links por paquetes, sin orden,
    no reconocidos, etc. Este paso llega cuando
    ya se tiene una lista de los links y estos
    tienen propiedades como el nombre.
    """
    packages = {}
    unsorted = []
    last_pkg += 1
    
    for link in links:
        link['nfile'] = last_pkg
        last_pkg += 1
        if 'chapter' in link:
            if not link['chapter'] in packages.keys() and type_packages == 'dd':
                packages[link['chapter']] = {}
                packages[link['chapter']]['npackage'] = last_pkg
                last_pkg += 1
            if not link['chapter'] in packages.keys() and type_packages == 'p2p':
                packages[link['chapter']] = []
                setattr(packages[link['chapter']], 'npackage', last_pkg)
                last_pkg += 1
            if type_packages == 'dd':
                # Se busca si es una de varias partes
                if re.findall('\.part(\d+)', link['name']):
                    part = re.findall('\.part(\d+)', link['name'])
                elif re.findall('\.(\d+)$', link['name']):
                    part = re.findall('\.(\d+)$', link['name'])
                else:
                    part = None
                
                if part:
                    part = int(part[0])
                else:
                    part = 1
                packages[link['chapter']][part] = link
            elif type_packages == 'p2p':
                packages[link['chapter']].append(link)
        else:
            unsorted.append(link)
    return packages, unsorted, last_pkg

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

def get_chapters(links, first_name):
    """
    Obtener los número de capítulos de los
    archivos haciendo uso get_chapter y otras
    técnicas.
    """
    if len(links) > 1:
        # Hay más de 1 capítulo, por lo que se usa
        # método de comparación de nombres
        i = 1
        igroup = None
        # Se irá probando hasta que se encuentre otro
        # archivo con el que se pueda sacar igroup
        while i < len(links) and igroup == None:
            igroup = get_chapter(links[0]['name'], links[i]['name'])
            i += 1
    elif first_name:
        # No hay más de 1 capítulo para poder comparar,
        # pero se tiene el último nombre que hubo anteriormente.
        igroup = get_chapter(links[0]['name'], first_name)
    else:
        # El igroup será el primer número que aparezca
        igroup = 0
    if igroup != None:
        for link in links:
            try:
                link['chapter'] = int(re.findall('(\d+)', link['name'])[igroup])
            except IndexError:
                pass
    else:
        # Todos los capítulos son el primer capítulo
        for link in links:
            link['chapter'] = 1

def get_ddbb_data(table, filters):
    """
    Obtener de la base de datos una fila.
    Se define por table (nombre de la tabla
    en la que buscar) y los filtros para el
    get. El dato devuelto es el id de la tabla.
    """
    if getattr(model, table).objects.filter(**filters):
        return str(getattr(model, table).objects.get(**filters).id)
    else:
        return ''

def get_urls_info(server, links_server, links, errors):
    """
    Obtener información de los links obtenidos.
    """
    if links_server and server.name.lower() in hikkea.ddservers.__all__:
        threads = []
        for link_server in links_server:
            thread = Thread(target=ddservers[server.name.lower()].check,
                            args=(link_server, links, errors))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
    else:
        for link_server in links_server:
            val = {
                'status': None,
                'name': None,
                'size': None,
                'size2': None,
                'url': link_server,
                'message': '',
                'server': server.name,
            }
            links.append(val)

def get_size(size):
    """
    Obtener en Bytes un tamaño del tipo "humano"
    (por ejemplo, "33 KiB"). Se omite si son
    bytes o bits, se tratará siempre como bytes.
    """
    keys = re.findall('([A-z])', size)
    if not keys: return 0
    if not keys[0].upper() in SIZES.keys(): return 0
    number = re.findall('(\d+|\.|,)', size)
    if not number: return 0
    return int(float(number[0]) * SIZES[keys[0].upper()])