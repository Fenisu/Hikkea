# -*- coding: utf-8 -*-

'''
Mixed models. In the future the models regarding releases
should be moved to a new django app.
One of the obejctives is to make it 100% modular.
'''
from django.db import models
from django import forms

from django.contrib.auth.models import User

class Group(models.Model):
    '''
    Los grupos definen los permisos de los usuarios y
    los trabajos que desempeñan. Por ejemplo, el grupo
    "admin" tiene acceso parcialmente completo, y el
    grupo "warehouseman" puede cambiar links en las
    Releases.
    '''
    name = models.CharField(max_length=32, blank=False)
    subgroups = models.ManyToManyField('self', related_name='groupsubgroup',
                                       blank=True,
                                       null=True)
    def __unicode__(self):
        return '%s' % self.name                                      

class PollOption(models.Model):
    '''
    Una opción para votar en una determinada encuesta.
    name es la definición de la opción y voters una
    lista de los usuarios que han votado a dicha opción.
    Es necesario tener una contabilización de lo que ha
    votado cada usuario para que se pueda cambiar el voto.
    '''
    name = models.CharField(max_length=32, blank=False)
    voters = models.ManyToManyField(User, related_name='polloptionvoters',
                                    blank=True,
                                    null=True)
    def __unicode__(self):
        return '%s' % self.name      

class Poll(models.Model):
    '''
    Una encuesta de cualquier tipo. Puede ser bien
    numérica (¿Qué le parece este artículo? seleccione
    entre 0, 1, 2, 3, 4) o de pregunta con una o varias
    opciones.
    
    * max_multuple_answers le permite definir el número
      máximo de votos por usuario. Por defecto 1, no puede
      superar el número deopciones
    * change_vote activado permite al usuario cambiar su
      voto. Por defecto False.
    * score_poll define que es una encuesta de tipo numérico.
      Al estar activado, permitirá realizar una media de los
      resultados.
    '''
    question = models.CharField(max_length=128, blank=False)
    max_multiple_answers = models.IntegerField(default=1)
    change_vote = models.BooleanField(default=False)
    scores_poll = models.BooleanField(default=False) # Options: 1, 2, 3...
    options = models.ManyToManyField(PollOption, related_name='pollpolloption')
    # This option is for groups...
    groups = models.ManyToManyField(User, related_name='pollgroups',
                                    blank=True, null=True)
    start = models.DateTimeField(auto_now_add=True)
    update_options = models.DateTimeField(blank=True, null=True)
    
    def count_voters(self):
        total_voters = 0
        # ALERT ¿Esto funciona?
        for option in self.options.objects.all():
            total_voters += len(option.voters.objects.all())
        return total_voters
    
    def __unicode__(self):
        return '%s' % self.question

class SocialVote(models.Model):
    '''
    Una versión simplificada de Poll con usos específicos.
    Permite 2 únicas opciones como opinión "me gusta" y
    "no me gusta". Estos nombres pueden ser luego cambiados
    por otros como "+1" o "-1". Incluye además una opción
    "reportar", para avisar de que el comentario incumple
    las normas. Cuando se reporta un comentario, se da un
    aviso a un responsable.
    
    Un uso de SocialVote es por ejemplo los comentarios.
    '''
    reports =  models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_reports_related")
    ilike = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_ilike_related")
    ihate = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_ihate_related")

class ImageFormat(models.Model):
    '''
    Diferentes formatos de imagen, como PNG, JPEG...
    * El name define el nombre oficial (ej. JPEG)
    * ext_regex es un patrón regex para la selección por
      la extensión (ej. jpg|jpeg).
    * description se trata de una ayuda para los usuarios
      para comprender las ventajas y desventajas del
      formato.
    '''
    name = models.CharField(max_length=16, blank=False)
    ext_regex = models.CharField(max_length=32, blank=False)
    description = models.CharField(max_length=1024, blank=True, null=True)
    def __unicode__(self):
        return '%s' % self.name

class ImageMirrorName(models.Model):
    '''
    Nombres de los sitios a los que se suben las imágenes.
    Por ejemplo, Imageshack, flickr, etc.
    Permite votar para que los usuarios puedan expresar
    si les gusta el servidor o no.
    main define si es el servidor por defecto.
    '''
    name = models.CharField(max_length=64, blank=False)
    website = models.URLField()
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    main = models.BooleanField()
        
    def __unicode__(self):
        return '%s' % self.name

class Image(models.Model):
    '''
    Una imagen del servidor. Cuando se sube una imagen
    al servidor, se crea una fila con su checksum y el
    nombre si se conociese. Cuando se va a buscar dicha
    imagen, se busca por el id de la fila. Hay muchas
    copias de la imagen en ImageMirror, y se servirá una
    u otra dependiendo de las preferencias del usuario y
    de los administradores del sistema.
    '''
    cheksum = models.ForeignKey('CheckSum', blank=False) # original Image
    filename = models.CharField(max_length=128, blank=True, null=True)
    height = models.IntegerField()
    width = models.IntegerField()
    def __unicode__(self):
        return '%s: %s (filename: %s)' % (self.checksum.type.name,
                                          self.checksum.name,
                                          self.filename)


class ImageMirror(models.Model):
    '''
    Una de las copias de una misma imagen. Una imagen,
    cuando se sube al servidor, se crean varias copias
    en diferentes calidades y formatos, y luego se
    suben a una serie de servidores alojadores de imágenes
    (flickr, imageshack, etc.). Cada fila es una de estas
    imágenes.
    * image define la imagen original al que se refiere.
    * 
    '''
    image = models.ForeignKey(Image, related_name='image',
                              blank=False)
    format = models.ForeignKey(ImageFormat, blank=False)
    quality = models.IntegerField(blank=False) # In PNG 100%
    size = models.IntegerField(blank=False) # Bytes
    mirror_name = models.ForeignKey(ImageMirrorName, blank=False)
    url = models.URLField()
    cheksum = models.ForeignKey('CheckSum', blank=False)
    def __unicode__(self):
        return '%s in %s [URL: %s]' % (self.image.filename,
                                       self.mirror_name.name,
                                       self.url)

class Comment(models.Model):
    '''
    Los comentarios son la forma de expresión más sencilla
    de los usuarios en Titles, Release, etc. Los Comment
    se pueden añadir a cualquier modelo para habilitar los
    comentarios. Cada fila es un comentario.
    
    Se recomienda añadir en los modelos en los que se
    habiliten los comentarios lo siguiente:
    
    open_comments = models.BooleanField(default=True)
    
    Gracias a esta opción se podrán habilitar y deshabilitar
    los comentarios para los usuarios comunes.
    '''
    user = models.ForeignKey(User, blank=False,
            related_name="%(app_label)s_%(class)s_user_related")
    reply_to = models.ForeignKey('self', blank=True, null=True,
            related_name="%(app_label)s_%(class)s_replyto_related")
    comment = models.CharField(max_length=2048, blank=False)
    add_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(blank=True, null=True)
    edit_user = models.ForeignKey(User, blank=True, null=True,
            related_name="%(app_label)s_%(class)s_edituser_related")
    edit_reason = models.CharField(max_length=128, blank=True, null=True)
    socialvote = models.ForeignKey(SocialVote, blank=True, null=True)

class Genre(models.Model):
    '''
    Los géneros son el catalogador principal de los ánimes,
    los mangas y los doramas. Ejemplos de géneros son el
    gore, la ciencia ficción, la comedia, etc. Algunos
    artículos pueden poseer advertencias de contenido que
    puede herir los sentimientos por el mero hecho de tener
    un género. Un ejemplo es el hentai.
    
    Un artículo puede tener más de un género, aunque en
    ocasiones, por decisión de los administradores, 2 o
    varios géneros pueden unirse para dar uno solo. Un ejemplo
    es la comedia romántica, sin que se catalogue dicho
    artículo en comedia y romántica.
    '''
    name = models.CharField(max_length=64, blank=False)
    warning = models.BooleanField(default=False)
    def __unicode__(self):
        return '%s' % self.name

class Tags(models.Model):
    '''
    Son un método catalogador más general. A diferencia de
    Genre, no buscan catalogar globalmente el artículo sino
    definir sus rasgos más superficiales y elementos visibles.
    Ejemplos son Mechas, militar, etc.
    
    Los tags no pertencen necesariamente a un Genre. Por ejemplo,
    sería fácil pensar que el tag "Militar" pertenece únicamente
    al Genre "Bélico", pero esto no siempre se cumple. Full Metal
    Panic Fumoffu es una comedia romántica con un alto contenido
    militar y de mechas.
    '''
    name = models.CharField(max_length=64, blank=False)
    def __unicode__(self):
        return '%s' % self.name

class Profession(models.Model):
    '''
    Una profesión. Las personas tienen profesiones, como por
    ejemplo "Seiyuu" o "director".
    '''
    name = models.CharField(max_length=32, blank=False)
    def __unicode__(self):
        return '%s' % self.name
    

class People(models.Model):
    '''
    Una persona, generalmente refiriéndose a celebridades.
    No debe confundirse con "User", el cual se refiere a
    usuarios de la web, con People, que es una persona de
    un artículo.
    '''
    name = models.CharField(max_length=32, blank=False)
    nationality =  models.ForeignKey('Country', blank=True, null=True)
    sex = models.ForeignKey('Sex', blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True)
    profession = models.ManyToManyField(Profession, related_name='peopleprofession',
                                        blank=True, null=True)
    description = models.CharField(max_length=3000, blank=True, null=True)
    greatest_hits = models.ManyToManyField('Title', related_name='peopletitle',
                                           blank=True, null=True)
    open_comments = models.BooleanField(default=True)
    comments = models.ManyToManyField(Comment, blank=True, null=True)
    def __unicode__(self):
        return '%s' % self.name

class Company(models.Model):
    '''
    Una compañía u organización de una ficha. Puede ser un
    estudio, una cadena. etc. No debe referirse a compañías
    ficticias, como las de un Anime/Manga/Dorama.
    '''
    name = models.CharField(max_length=32, blank=False)
    description = models.CharField(max_length=3000, blank=True, null=True)
    start_year = models.IntegerField(blank=True, null=True)
    greatest_hits = models.ManyToManyField('Title', related_name='studiotitle',
                                           blank=True, null=True)
    open_comments = models.BooleanField(default=True)
    comments = models.ManyToManyField(Comment, blank=True, null=True)
    def __unicode__(self):
        return '%s' % self.name

class TitleType(models.Model):
    '''
    Los títulos pueden se diferentes tipos, como manga,
    anime o dorama.
    '''
    name = models.CharField(max_length=32, blank=False)
    def __unicode__(self):
        return '%s' % self.name

class RelationshipType(models.Model):
    '''
    Un título puede estar relacionado con otro de
    diferentes maneras: que sea un Spinoff, un Remake,
    una nueva temporada... cada fila es el nombre de cada
    una de estas opciones.
    '''
    name = models.CharField(max_length=32, blank=False)
    def __unicode__(self):
        return '%s' % self.name

class Relationship(models.Model):
    '''
    Un título puede tener varias relaciones con otros
    títulos, de maneras diferentes (definido en
    RelationshipType). Cada fila es un título y una manera
    de relación, y Relationship es contenido en Title
    '''
    title = models.ForeignKey('Title', blank=False)
    type = models.ForeignKey(TitleType, blank=False)
    def __unicode__(self):
        return '%s' % self.title.name

class OtherName(models.Model):
    '''
    Nombres alternativos a un Title, bien sea en otros
    idiomas, en el original, etc.
    '''
    name = models.CharField(max_length=64, blank=False)
    def __unicode__(self):
        return '%s' % self.name

class ReferenceSource(models.Model):
    '''
    La fuente de la referencia, como por ejemplo
    Wikipedia, anidb, ANN, etc.
    '''
    # Nombre del sitio. Ejemplo: wikipedia
    name = models.CharField(max_length=64, blank=False)
    # Url del sitio
    website = models.URLField()
    # Patrón Regex para detectar si se trata de la fuente
    regex = models.CharField(max_length=128, blank=False)
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    # La fuente es la considerada principal para la web
    main = models.BooleanField()
    # Idioma principal de la web de referencia.
    lang = models.ForeignKey('Language', blank=False)
        
    def __unicode__(self):
        return '%s in %s' % (self.title.name, self.source.name)

class Reference(models.Model):
    '''
    Las referencias son la fuente de la información,
    como el contenido de los TitleVersion. Pueden
    añadirse referencias automáticamente si el contenido
    es añadido desde la fuentes por un script.
    '''
    url = models.URLField(verify_exists=True)
    # Fuente de la que proviene. Véase ReferenceSource
    source = models.ForeignKey(ReferenceSource, blank=False)
    def __unicode__(self):
        return '%s in %s' % (self.title.name, self.source.name)

class TitleVersion(models.Model):
    '''
    Las versiones de los títulos son un método para
    crear una ficha de un título entre varios usuarios,
    pudiendo revisar los cambios realizados por cada uno
    de estos usuarios, y poder regresar a versiones
    anteriores.
    
    Cada TitleVersion es una versión del mismo Title,
    y en self.title se define qué Title está versionando.
    Por su parse, Title dirá cuál de las versiones será
    la que se muestre al público.
    '''
    # El Title que se está versionando.
    title = models.ForeignKey('Title', blank=True, null=True)
    # Fecha de envío
    date = models.DateTimeField(auto_now_add=True)
    # Autor de la versión
    author = models.ForeignKey(User, unique=True)
    edit_reason = models.CharField(max_length=256, blank=True)
    # Comentario SOBRE la versión, no el Title. Por ejemplo,
    # para preguntar sobre el motivo de un cambio en la versión.
    # Serían los comentarios para los desarrolladores de las
    # versiones.
    comments = models.ManyToManyField(Comment, blank=True)
    # Nombre del artículo.
    name = models.CharField('Título', max_length=64, blank=False)
    alternative_name = models.ManyToManyField(OtherName,
                                              related_name='titleversionothername',
                                              blank=True,
                                              null=True)
    # Anime, manga or Dorama
    type = models.ForeignKey(TitleType, blank=False)
    # Episodios en anime y dorama. Volúmenes en manga
    episodes = models.IntegerField(blank=False)
    description = models.CharField(max_length=4096)
    # Fuentes de referencia de la información
    references = models.ManyToManyField('Fansub',
                                        related_name='titleversionreferences',
                                        blank=True,
                                        null=True)
    genre = models.ManyToManyField(Reference,
                                   related_name='titleversiongenre',
                                   blank=True,
                                   null=True)
    # Minutos en anime y dorama. páginas en Manga
    duration = models.IntegerField(blank=True, null=True)
    # Drama, action...
    genre = models.ManyToManyField('Fansub',
                                   related_name='titleversiongenre',
                                   blank=True,
                                   null=True)
    # Mecha, military...
    tags = models.ManyToManyField(Tags,
                                  related_name='titleversiontags',
                                  blank=True,
                                  null=True)
    season = models.IntegerField(blank=False, default=1)
    # Publication year
    year = models.IntegerField(blank=True, null=True)
    # Fecha de comienzo de emisión
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    director = models.ManyToManyField(People,
                                      related_name='titleversiondirector',
                                      blank=True,
                                      null=True)
    screenwriter = models.ManyToManyField(People,
                                          related_name='titleversionwriter',
                                          blank=True,
                                          null=True)
    studio = models.ManyToManyField(Company,
                                    related_name='titleversionstudio',
                                    blank=True,
                                    null=True)
    # Relaciones con otros Titles. Véase Relationship
    relations = models.ManyToManyField(Relationship, blank=True, null=True)
    # La imagen que representa al Title. Para capturas
    # se tomarán las de la mejor Release por la crítica.
    thumb = models.ForeignKey(Image, blank=True, null=True)
    # Si se ha terminado de publicar
    complete = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Incluir aquí que al guardar TitleVersion, se cambie
        # el name de Title en caso de ser la versión aceptada
        super(TitleVersion, self).save(*args, **kwargs)
    def __unicode__(self):
        return '%s' % self.name

class Title(models.Model):
    '''
    Title es una ficha de un anime, un manga, un dorama,
    u otro tipo de producto en un futuro. En el se incluye
    información como año, género, una descripción, etc.
    
    Los Title al ser creados por la comunidad, requieren una
    forma de control, para saber qué aportación ha hecho
    cada usuario y poder regresar a una versión anterior en
    caso de vandalismo. En accepted se define cual es la
    versión que se mostrará.
    
    Es necesario que cierta información de los Title no se
    encuentre versionada. Ejemplo son la puntuación, los
    comentarios, etc. De lo contrario, en cada versión se
    perdería esta información.
    '''
    # El name se incluye para agililizar las búsquedas en la
    # base de datos, debe ser el mismo al TitleVersion de
    # accepted
    name = models.CharField('Título', max_length=64, blank=False)
    accepted = models.ForeignKey(TitleVersion, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_accepted_related")
    score = models.IntegerField(blank=True, null=True)
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    open_comments = models.BooleanField(default=True)
    comments = models.ManyToManyField(Comment, blank=True, null=True)
    # Impedir cambios a usuarios normales.
    close = models.BooleanField(default=False)
    def __unicode__(self):
        return '%s' % self.accepted.name

class Medal(models.Model):
    '''
    Las medallas son un método de reconocimiento que se
    ofrece bien de forma manual, como de forma automática.
    Se otorgan a fansubs y usuarios.
    '''
    name = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=512, blank=False)
    image = models.ForeignKey(Image, blank=False)
    def __unicode__(self):
        return '%s' % (self.name)

class Fansub(models.Model):
    '''
    Los fansubs son los encargados de la traducción de los
    Titles, y sus trabajos se encuentran en Release, bien
    publicados por ellos de manera oficial, como por otros
    usuarios.
    
    Cualquiera puede crear un esbozo de una ficha de fansub,
    con el name y el microname, pero debe ser un administrador
    o responsable el que agrege los otros datos, o bien los
    propios responsables del fansub, si demuestran que
    pertenecen al susodicho fansub.
    
    El fansub "RAW" es un nombre genérico de fansub para
    referirse a contenido en bruto, sin subtítulos ni
    modificaciones.
    '''
    name = models.CharField(max_length=64, blank=False)
    # El microname es una forma abreviada de decir el nombre del
    # fansub. En ocasiones es el mismo que name.
    microname = models.CharField(max_length=16, blank=False)
    description = models.CharField(max_length=16, blank=True)
    url = models.URLField(verify_exists=True, blank=True)
    irc = models.CharField(max_length=128, blank=True)
    jabber = models.CharField(max_length=128, blank=True)
    contact = models.EmailField(max_length=128, blank=True) # Email
    logo = models.ForeignKey(Image, blank=True, null=True)
    start_year = models.IntegerField(blank=True)
    # Las medallas son dadas por el sistema, no las toma el fansub
    medals = models.ManyToManyField(Medal, blank=True, null=True)
    # Las releases oficiales son las creadas y publicadas por el
    # propio fansub, siendo las originales. Los miembros del fansub
    # pueden añadir o editar las releases dependiendo de sus permisos,
    # independientemente de quien las haya subido.
    official_releases = models.ManyToManyField('Release', blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_officialrelease_related")
    # Los grupos de tareas pendientes permiten a los
    # fansubs tener un espacio propio en el que asignar
    # tareas a otros miembros, y recibir reportes de fallos
    # en sus traducciones
    task_groups = models.ManyToManyField('TaskGroup', blank=True, null=True)
    def __unicode__(self):
        return '[%s] - %s' % (self.microname, self.name)

class FansubUser(models.Model):
    '''
    Los fansubs pueden tener una serie de miembros con
    diferentes permisos en la edición y trabajo del fansub.
    Cada fila define un usuario, un fansub (al cual pertenece
    dicho usuario) y los permisos de dicho usuario dentro del
    fansub.
    
    Es importante diferenciar entre los grupos a los que pertenece
    un usuario en UserProfile, y a los que pertenece en
    FansubUser, ya que los grupos a los que pertenece en FansubUser
    son exclusivos para dentro del susodicho fansub, y no son
    válidos en otros fansubs.
    '''
    user = models.ForeignKey(User, blank=False)
    fansub = models.ForeignKey(Fansub, blank=False,
                        related_name="%(app_label)s_%(class)s_fansub_related")
    groups = models.ManyToManyField(Fansub, blank=True, null=True,
                        related_name="%(app_label)s_%(class)s_groups_related")
    def __unicode__(self):
        return '%s in %s' % (self.user.name, self.fansub.name)

class VideoCodec(models.Model):
    '''
    Códec de vídeo. Permite una descripción y votos por los usuarios.
    Un ejemplo sería H.264. Permite además establecer un qualitiy,
    para definir lo bueno que es este códec. Las puntuaciones vienen
    dadas del 1 al 10.
    '''
    name = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=2048, blank=True)
    quality = models.IntegerField()
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    main = models.BooleanField() # Codec recomendado
    def __unicode__(self):
        return '%s' % self.name
 
class AudioCodec(models.Model):
    '''
    Igual que códec de vídeo, pero aplicándose al audio. Un
    ejemplo sería mp3.
    '''
    name = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=2048, blank=True)
    quality = models.IntegerField()
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    main = models.BooleanField()
    def __unicode__(self):
        return '%s' % self.name

class SubtitleCodec(models.Model):
    '''
    Subtitle formats used on the releases.
    Hardsub is also considered a format.
    '''
    name = models.CharField(max_length=32, blank=False)
    description = models.CharField(max_length=2048, blank=True, null=True)
    quality = models.IntegerField()
    users_score = models.ForeignKey(Poll, blank=True)
    main = models.BooleanField()
    def __unicode__(self):
        return '%s' % self.name

class Language(models.Model):
    '''
    Idioma o dialecto. Se hace distinción entre español de
    España y español de sudamérica. La imagen es un icono
    representativo del idioma.
    '''
    name = models.CharField(max_length=32, blank=False)
    image = models.ForeignKey(Image, blank=False)
    def __unicode__(self):
        return '%s' % self.name
 
class VideoAspectRatio(models.Model):
    '''
    Video Aspect Ratio, mostly 4:3 and 16:9.
    '''
    name = models.CharField(max_length=16, blank=False) # ex. 16:9
    relation = models.FloatField() # ex. 1.7777 (16/9)
    quality = models.IntegerField(blank=True)
    def __unicode__(self):
        return '%s' % self.name
 
class VideoResolution(models.Model):
    '''
    Resolución de vídeo. resolution viene dado de la siguiente
    manera: <anchura>x<altura>. Por ejemplo, 1920x1080. El
    quality es igual que en los códecs. 
    '''
    resolution = models.CharField(max_length=32, blank=False)
    width = models.IntegerField()
    height = models.IntegerField()
    quality = models.IntegerField(blank=True)
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    main = models.BooleanField()
    def __unicode__(self):
        return '%s' % self.resolution
 
class AudioChannel(models.Model):
    '''
    Audio Channels, 2.1, 5.1...
    '''
    name = models.CharField(max_length=16, blank=False)
    description = models.CharField(max_length=2048, blank=True)
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    quality = models.IntegerField()
    main = models.BooleanField()
    def __unicode__(self):
        return '%s' % self.name
 
class AudioHertz(models.Model):
    '''
    Audio Hertz, 44.1, 48... khz
    '''
    name = models.CharField(max_length=16, blank=False)
    quality = models.IntegerField()
    def __unicode__(self):
        return '%s' % self.name
 
class Container(models.Model):
    '''
    File Container, mkv, avi...
    '''
    name = models.CharField(max_length=64, blank=False)
    ext = models.CharField(max_length=8, blank=False)
    description = models.CharField(max_length=2048, blank=True)
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    quality = models.IntegerField()
    main = models.BooleanField()
    def __unicode__(self):
        return '%s (.%s)' % (self.name, self.ext)
 
class SourceRelease(models.Model):
    '''
    Media Source, bdmv, ts...
    '''
    name = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=2048, blank=True)
    def __unicode__(self):
        return '%s' % self.name

DOWNLOAD_TYPE = (('dd', 'Direct Download'),
                 ('p2p', 'Peer to Peer'),
                 )

class Release(models.Model):
    '''
    Una Release es una forma de descarga de un Title, con unas
    propiedades que la caracterizan. Estas son su codec de vídeo,
    su idioma, el fansub que lo traduce, su método de descarga...
    no puede haber 2 propiedades diferentes a un mismo campo en una
    Release. Por ejemplo, no puede haber unos capítulso traducidos
    por un fansub y otros por otro (salvo contadas excepciones) o
    encontrarse, en el caso de la Descarga Directa, en varios
    servidores diferentes (esta regla es inquebrantable).
    
    Una Release se encuentra relacionada con un Title mediante un
    ForeignKey, pero no establece una relación directa con sus
    descargas. Serán las descargas las que establezcan una relación
    con la Release por medio de un ForeignKey. En cambio, se introduce
    la opción 'download_type', la cual dirá si es necesario buscar en
    DirectDownloadPackage, o en P2PDownloadPackage.
    '''
    # Usuario que envía la release
    user = models.ForeignKey(User, blank=False,
                    related_name="%(app_label)s_%(class)s_user_related")
    # Es necesario que en un inicio title sea True para poder validar
    # cuando después se va a crear el Title.
    title = models.ForeignKey(Title, blank=True, null=True)
    fansub = models.ManyToManyField(Fansub, blank=False)
    # alang se refiere a Idioma de Audio
    alang = models.ManyToManyField(Language, blank=False,
                    related_name="%(app_label)s_%(class)s_alang_related")
    # slang se refiere a Idioma de Subtítulo
    slang = models.ManyToManyField(Language, blank=False,
                    related_name="%(app_label)s_%(class)s_slang_related")
    # Sobra en el manga
    videocodec = models.ManyToManyField(VideoCodec, blank=True, null=True)
    resolution = models.ManyToManyField(VideoResolution, blank=False)
    # Sobra en el manga
    audiocodec = models.ManyToManyField(AudioCodec, blank=True, null=True)
    # Sobra en el manga
    audiochannel = models.ManyToManyField(AudioChannel, blank=True, null=True)
    # Sobra en el manga
    audiohertz = models.ManyToManyField(AudioHertz, blank=True, null=True)
    # Sobra en el manga
    subtitlecodec = models.ManyToManyField(SubtitleCodec, blank=True, null=True)
    # Sobra en el manga
    container = models.ManyToManyField(Container, blank=True, null=True)
    # La fuente del vídeo. Por ejemplo, DVD, HDTV, etc. (Sobra en el manga)
    source = models.ManyToManyField(SourceRelease, blank=True, null=True)
    
    staff_tl = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_stafftl_related")
    staff_tlc = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_stafftlc_related")
    staff_time = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_stafftime_related")
    staff_sign = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_staffsign_related")
    staff_kar = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_staffkar_related")
    staff_style = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_staffstyle_related")
    staff_encode = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_staffencode_related")
    staff_qc = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_staffqc_related")
    staff_otros = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_staffotros_related")
    
    # Un breve comentario. No se permite añadir links ni nada
    # parecido en los comentarios.
    submitter_comment = models.CharField(max_length=500, blank=True)
    open_comments = models.BooleanField(default=True)
    comments = models.ManyToManyField(Comment, blank=True, null=True)
    screenshots = models.ManyToManyField(Image, blank=True, null=True)
    # Si es DD o P2P
    download_type = models.CharField(max_length=4, blank=False,
                                     choices=DOWNLOAD_TYPE)
    # La crítica lo considera el método principal
    accepted = models.BooleanField(default=False)
    add_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(blank=True)
    edit_user = models.ForeignKey(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_edituser_related")
    edit_reason = models.CharField(max_length=128, blank=True)
    socialvote = models.ForeignKey(SocialVote, blank=True, null=True)
    def __unicode__(self):
        return '%s' % self.title.name

class ReleaseForm(forms.ModelForm):
    download_type = forms.CharField(widget=forms.RadioSelect(choices=DOWNLOAD_TYPE))
    class Meta:
        model = Release
    def __init__(self, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)

class CheckSumType(models.Model):
    '''
    Ateniendo a la posibilidad de que no se llegue a un
    acuerdo en el checksum a utilizar, se ofrecerá la
    posibilidad de elegir el que se desee por parte del
    uploader. Este apartado solo ofrece una información
    sobre el checksum, siendo 'len' la longitud máxima
    del Checksum en cuestión.
    
    Ejemplos serían CRC32, SHA1 o MD5.
    '''
    name = models.CharField(max_length=32, blank=False)
    description = models.CharField(max_length=512, blank=False)
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    main = models.BooleanField()
    len = models.IntegerField()
    def __unicode__(self):
        return '%s' % self.name

class CheckSum(models.Model):
    '''
    El checksum es un método de verificación utilizado
    para comprobar que la integridad de los datos
    transferidos es correcta. Es usado en telecomunicaciones
    y para seguridad. Los hashes son lo que se llaman "de
    sentido único" y a partir de un hash, es imposible volver
    al contenido original. En este caso su uso es ofrece a
    los usuarios un método para comprobar que el contenido
    que reciben es correcto, y en el servidor para verificar
    que no hay datos repetidos (por ejemplo, imágenes).
    '''
    name = models.CharField(max_length=2048, blank=False)
    type = models.ForeignKey(CheckSumType, blank=False)
    def __unicode__(self):
        return '%s' % self.name

class Protection(models.Model):
    '''
    Permite establecer métodos de protección para los links
    que recurrentemente han sido borrados. El name establece
    el nombre de la protección.
    '''
    name = models.CharField(max_length=32, blank=False)
    def __unicode__(self):
        return '%s' % self.name

class DirectDownloadServer(models.Model):
    '''
    Tipo de servidor de Descarga Directa. Por ejemplo,
    Megauplod, Rapidshare, etc. Ofrece información
    sobre el servidor y permite votar a los usuarios para
    hacerse una idea de cuál es su servidor favorito. El
    regex es un patrón de búsqueda para encontrar el link
    entre un listado de links.
    '''
    name = models.CharField(max_length=32, blank=False)
    mininame = models.CharField(max_length=6, blank=True, null=True)
    regex = models.CharField(max_length=512)
    website = models.URLField()
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    main = models.BooleanField()
    def __unicode__(self):
        return '%s' % self.name

class DirectDownload(models.Model):
    '''
    Un link de Descarga Directa. Ofrece campos para
    establecer cierta información sobre el link, como si
    se encuentra online, la última comprobación del link,
    etc.
    
    El part solo se usa en archivos divididos de un mismo
    archivo (del tipo .partX.rar o .00X).
    
    El mirrors permite establecer links alternativos del
    MISMO archivo, por si uno se cayese. Los mirrors deben
    ser del mismo servidor.
    '''
    url = models.URLField()
    filename = models.CharField(max_length=512, blank=True, null=True)
    size = models.IntegerField(blank=True)
    server = models.ForeignKey(DirectDownloadServer, blank=False)
    online = models.BooleanField(blank=False)
    checksum = models.ForeignKey(CheckSum, blank=True, null=True)
    part = models.IntegerField(blank=True) # In split files
    last_check = models.DateTimeField(blank=True)
    mirrors = models.ManyToManyField('self', blank=True, null=True)
    protection = models.ManyToManyField(Protection, blank=True, null=True)
    def __unicode__(self):
        return '%s' % self.url

class DirectDownloadPackage(models.Model):
    '''
    El DirectDownloadPackage es un conjunto de links (o
    un único link) de un mismo capítulo/tomo. Cuando el
    archivo se encuentra dividido (archivos .partX, .00X)
    el paquete contendrá todos los links que completen
    el archivo. En caso de caer un link, se considerará
    todo el paquete como caído.
    
    ADVERTENCIA: Pando será considerado como método de
    Descarga Directa, ya que comparte sus mismas
    características.
    '''
    name = models.CharField(max_length=512, blank=True, null=True)
    size = models.IntegerField(blank=True)
    checksum = models.ForeignKey(CheckSum, blank=True)
    files = models.ManyToManyField(DirectDownload, blank=False)
    release = models.ForeignKey(Release, blank=True, null=True)  
    def __unicode__(self):
        return '%s' % self.name

class P2PDownloadProvider(models.Model):
    '''
    El nombre del Tracker e información del mismo.
    DHT, el cual no es realmente un tracker, será
    considerado como un proveedor. Esto es solo
    necesario en métodos P2P centralizados.
    '''
    name = models.CharField(max_length=64, blank=True, null=True)
    regex = models.CharField(max_length=512, blank=True, null=True)
    website = models.URLField(blank=True)
    score = models.IntegerField(blank=True)
    users_score = models.ForeignKey(Poll, blank=True)
    main = models.BooleanField()
    def __unicode__(self):
        return '%s' % self.name
 
class P2PDownloadType(models.Model):
    '''
    Tipo de P2P. Por ejemplo, edk2, Torrent, etc.
    Permite puntuaciones para que los usuarios
    opinen sobre sus tipos de P2P favoritos.
    '''
    name = models.CharField(max_length=64, blank=False)
    regex = models.CharField(max_length=512, blank=True, null=True)
    website = models.URLField(blank=True)
    score = models.IntegerField(blank=True)
    users_score = models.ForeignKey(Poll, blank=True, null=True)
    main = models.BooleanField()
    def __unicode__(self):
        return '%s' % self.name

class P2PDownload(models.Model):
    '''
    La URL de descarga del archivo .torrent (en
    caso de torrent), o la URI en caso de DHT,
    edk2, etc.
    '''
    url = models.URLField()
    provider = models.ForeignKey(P2PDownloadProvider, blank=True, null=True)
    seeders = models.IntegerField(blank=True)
    leechers = models.IntegerField(blank=True)
    last_check = models.DateTimeField(blank=True)
    def __unicode__(self):
        return '%s' % self.url

class P2PDownloadPackage(models.Model):
    '''
    Un paquete de métodos P2P no es exactamente igual
    a uno de enlaces de Descarga Directa. Ambos,
    tienen como fin distribuir un capítulo o tomo,
    pero mientras que el de DD solo tiene un mirror,
    el de P2P puede tener varios. Por ejemplo, un MISMO
    archivo Torrent puede estar subido a varios trackers,
    y cada trackers será un P2PDownload. Esto no sucede
    con edk2, en que no es necesario varios trackers. Lo
    que no se llegarán a mezclar bajo ningún concepto, son
    varios tipos de P2P. Esto quiere decir que no se
    mezclarán links de edk2 con links de Torrent. El tipo
    de P2P viene definido en type.
    
    El checksum no es estrictamente necesario, pues la gran
    mayoría de los tipos de P2P incluyen un método de checksum.
    '''
    name = models.CharField(max_length=512, blank=True, null=True)
    type = models.ForeignKey(P2PDownloadType, blank=False)
    size = models.IntegerField(blank=True)
    checksum = models.ForeignKey(CheckSum, blank=True, null=True)
    files = models.ManyToManyField(P2PDownload, blank=False)
    release = models.ForeignKey(Release, blank=True, null=True)
                                 
                                 
class Country(models.Model):
    '''
    País de residencia para los perfiles de usuario
    y fichas de personas.
    '''
    name = models.CharField(max_length=32, blank=False)
    image = models.ForeignKey(Image, blank=False)
    lang = models.ForeignKey(Language, blank=False)
    # Husos horario del país. Puede haber varios
    timezone = models.ManyToManyField('TimeZone', blank=True, null=True)
    def __unicode__(self):
        return '%s' % self.name

GENDER_CHOICES = (
    (u'M', u'Male'),
    (u'F', u'Female'),
)

class Sex(models.Model):
    '''
    Sexo en los perfiles de usuario y fichas
    de personas.
    '''
    name = models.CharField(max_length=2, choices=GENDER_CHOICES)
    image = models.ForeignKey(Image, blank=False)
    def __unicode__(self):
        return '%s' % self.name

GROUPS_STATUS = (('gs_owner', 'Propietario'),
                 ('gs_admin', 'Administrador'),
                 ('gs_moderator', 'Moderador'),
                 ('gs_contributors', 'Colaborador'),
                 ('gs_member', 'Miembro'),
                 ('gs_anon', 'Anónimo'),
                 ('gs_bot', 'Bot'),
                 ('gs_searcher', 'Buscador'),
                 )

class Theme(models.Model):
    '''
    Soporte para el futuro de diferentes temas en la
    web. Por defecto 'default'. El 'name' es el título
    identificativo para los usuarios y el 'code' el que
    utilizará el programa para identificar el tema en
    cuestión.
    '''
    name = models.CharField(max_length=32, blank=False) # for humans
    code = models.CharField(max_length=32, blank=False)
    thumb = models.ForeignKey(Image, blank=False)
    def __unicode__(self):
        return '%s' % self.name   

ENSING_TYPES = (('pendant', 'Colgante'),
                ('shield', 'Escudo'),
                ('bandana', 'Bandana'),
                )

class Ensing(models.Model):
    '''
    Las ensignias son elementos decorativos que aparecen
    bajo el avatar o "colgado" de este (en el caso de los
    colgantes). Los usuarios son recomensados tras
    determinadas acciones (al igual que las medallas) con
    insignias para que puedan equiparse con una de estas.
    '''
    name = models.CharField(max_length=32, blank=False) # for humans
    type = models.CharField(max_length=32, choices=ENSING_TYPES)
    code = models.CharField(max_length=32, blank=False)
    thumb = models.ForeignKey(Image, blank=False)
    def __unicode__(self):
        return '%s' % self.name  

LIST_TITLES_OPTIONS = (('lto1', 'La quiero ver'),
                       ('lto2', 'Ya la he visto'),
                       ('lto3', 'Siguiéndola'), # Está en emisión o para emisión,
                       ('lto4', 'Viéndola'), # Se ha terminado y se está viendo,
                       ('lto5', 'Abandonada definitivamente'),
                       ('lto6', 'Dejada de momento'),
                       )

class ListTitles(models.Model):
    '''
    Permite a los usuarios establecer un estado de visualización
    de los títulos (la he visto, la quiero ver, etc.)
    
    ADVERTENCIA: Los textos descriptivos de las opciones (lo
    quier ver, etc.) deben cambiar el verbo "ver" por "leer" en el
    caso del manga y otros que se lean.
    '''
    title = models.ForeignKey(Title, blank=False)
    status = models.CharField(max_length=6, blank=False,
                              choices=LIST_TITLES_OPTIONS)
    # Mostrar a la gente las notas puestas
    show_notes = models.BooleanField(default=False)
    notes = models.CharField(max_length=128, blank=True, null=True)
    # Rellenar en caso de no haberse terminado
    season = models.IntegerField(blank=True, null=True)
    episodes = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return '%s' % self.title.name 

class TimeZone(models.Model):
    '''
    Diferentes zonas horarias para que los usuarios puedan
    elegir la que se adapta a su país.
    '''
    code = models.CharField(max_length=16, blank=False) # UTC, DST, etc.
    diffutc = models.FloatField(blank=False) # diferencia respecto UTC
    
    def __unicode__(self):
        if self.diffutc >= 0:
            return '%s (UTC+%f)' % (self.code, self.diffutc)
        else:
            return '%s (UTC%f)' % (self.code, self.diffutc)

TASK_PRIORITY = (('lvl0', 'Trivial'),
                 ('lvl1', 'Menor'),
                 ('lvl2', 'Normal'),
                 ('lvl3', 'Alta'),
                 ('lvl4', 'Muy alta'),
                 ('lvl5', 'Crítica'),
                 )

TASK_STATUS = (('new', 'Nuevo'),
               ('reopen', 'Reabierto'),
               ('needinfo', 'Faltan datos'),
               ('rejected', 'Rechazado'),
               ('pendant', 'Pendiente'),
               ('assigned', 'Asignado'),
               ('working', 'En proceso'),
               ('close', 'Cerrado'),
               )    

class TaskGroup(models.Model):
    '''
    Los grupos de trabajo en las tareas pueden ser
    bien abiertos o bien cerrados. En el primer caso,
    cualquiera puede enviar una nueva tarea. En el
    segundo, solo podrán hacerlo miembros del grupo.
    
    Los propietarios (owner) son los únicos con poderes
    para añadir nuevos miembros o borrar el grupo. Los
    miembros podrán añadir nuevas tareas y modificarlas,
    incluso siendo estas agenas.
    '''
    name = models.CharField(max_length=128, blank=False) # Title
    owner = models.ManyToManyField(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_owner_related")
    members = models.ManyToManyField(User, null=True, blank=True,
                    related_name="%(app_label)s_%(class)s_members_related")
    public = models.BooleanField(default=False)
    def __unicode__(self):
        return self.name

class Task(models.Model):
    '''
    Las tareas son quellos quehaceres pendientes, bien
    para la web, bien para los fansubs. Por ejemplo, los
    fansubs pueden usarlo para establecer tareas a
    realizar en la traducción por diferentes personas,
    y en la web para poner como tarea pendiente el resubir
    un anime.
    
    En el caso de que la tarea sea pública, cualquiera podrá
    ver la tarea y añadir comentarios.
    '''
    name = models.CharField(max_length=128, blank=False) # Title
    text = models.TextField()
    status = models.CharField(max_length=8, default='new',
                              choices=TASK_STATUS)
    status_notes = models.CharField(max_length=256, blank=True, null=True)
    priority = models.CharField(max_length=16, default='lvl0',
                              choices=TASK_STATUS)
    groups = models.ManyToManyField(TaskGroup, blank=True, null=True)
    public = models.BooleanField(default=False)
    submitted = models.ForeignKey(User, blank=False,
                    related_name="%(app_label)s_%(class)s_submitted_related")
    assigned = models.ManyToManyField(User, null=True, blank=True,
                    related_name="%(app_label)s_%(class)s_assigned_related")
    date = models.DateTimeField(auto_now_add=True)
    edit_user = models.ForeignKey(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_edituser_related")
    edit_date = models.DateTimeField(blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True)
    open_comments = models.BooleanField(default=True)
    comments = models.ManyToManyField(Comment, null=True, blank=True)
    def __unicode__(self):
        return self.name

PRIVATE_MESSAGE_TYPE = (('pm', 'Mensaje privado'),
                        ('nt', 'Notificación'),
                        )

class PrivateMessage(models.Model):
    '''
    Los mensajes privados son aquellos mensajes que
    tienen un único destinatario, y este, junto el
    emisor, son los únicos que conocen el contenido. Los
    mensajes privados también incluyen las notificaciones,
    las cuales son enviadas por el sistema ante ciertos
    acontecimientos automatizados.
    '''
    name = models.CharField(max_length=128, blank=False) # Title
    type = models.CharField(max_length=8, blank=False,
                            choices=PRIVATE_MESSAGE_TYPE)
    mfrom = models.ForeignKey(User, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_mfrom_related") # blank in notif.
    mto = models.ForeignKey(User, unique=True,
                    related_name="%(app_label)s_%(class)s_mto_related")
    text = models.CharField(max_length=2048, blank=False)
    view = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return '%s' % self.name

class UserProfile(models.Model):
    '''
    Enhancement of the User give the users the possibility
    to become fansubers.
    The adminfansub let's them be admin of a fansub and manage the releases
    although there is no need to be the admin to upload their releases.
    Power would be the admin level to admin the site.
    Karma will be used in the future as a troll-level to add
    a filter for the comments/threads.
    '''
    user = models.ForeignKey(User, unique=True)
    avatar = models.ForeignKey(Image, blank=True, null=True)
    groups = models.ManyToManyField(Group, blank=True, null=True)
    groups_status = models.CharField(max_length=32, blank=False,
                                     choices=GROUPS_STATUS)
    # Awards
    karma = models.FloatField(default=0.0)
    medals = models.ManyToManyField(Medal, blank=True, null=True)
    ensing = models.ForeignKey(Ensing, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_ensing_related")
    available_ensings = models.ManyToManyField(Ensing, blank=True, null=True,
                    related_name="%(app_label)s_%(class)s_availableensings_related")
    # IM
    jabber = models.EmailField(max_length=128, blank=True)
    msn = models.EmailField(max_length=128, blank=True, null=True)
    yahoo = models.EmailField(max_length=128, blank=True)
    icq = models.IntegerField(blank=True)
    aol = models.EmailField(max_length=128, blank=True)
    skype = models.CharField(max_length=64, blank=True)
    # Personal
    website = models.URLField(verify_exists=True, blank=True)
    description = models.CharField(max_length=256, blank=True)
    job = models.CharField(max_length=64, blank=True)
    country = models.ForeignKey(Country, blank=True)
    city = models.CharField(max_length=32, blank=True)
    # El sexo real. Se mostrará mediante un icono
    sex_icon = models.ForeignKey(Sex, blank=True, null=True)
    # Permite hacer "bromas" respecto el sexo, ya que es
    # un cuadro de texto.
    sex_text = models.CharField(max_length=16, blank=True)
    birthday = models.DateTimeField(blank=True)
    # Preferences
    theme = models.ForeignKey(Theme, blank=True, null=True)
    lang = models.ForeignKey(Language, blank=True, null=True)
    # Método de descarga favorito
    download_type = models.CharField(max_length=4, blank=False,
                                     choices=DOWNLOAD_TYPE)
    # Servidor de DD favorito
    dd_server = models.ForeignKey(DirectDownloadServer, blank=True, null=True)
    # Método de P2P favorito
    p2p_type = models.ForeignKey(P2PDownloadType, blank=True, null=True)
    # Proveedor (Tracker) de P2P favorito
    p2p_provider = models.ForeignKey(P2PDownloadProvider, blank=True, null=True)
    time_zone = models.ForeignKey(TimeZone, blank=True, null=True)
    show_email = models.BooleanField(default=False)
    # Mostrar por defecto mis notas en las listas de Títulos
    show_listttles_notes = models.BooleanField(default=False)
    # Data about user
    download_releases = models.ManyToManyField(Release, blank=True, null=True)
    list_titles = models.ManyToManyField(ListTitles, blank=True, null=True)
    def __unicode__(self):
        return '%s' % self.user

class WikiVersion(models.Model):
    '''
    Versión de un artículo de documentación. El
    funcionamiento es igual que es de las versiones
    en los Titles.
    '''
    name = models.CharField(max_length=128, blank=False)
    author = models.ForeignKey(User, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    # Igual que los comentarios del TitleVersion
    comments = models.ManyToManyField(Comment, blank=True, null=True)
    edit_reason = models.CharField(max_length=256, blank=True)
    wiki = models.ForeignKey('Wiki', null=True, blank=True)
    def __unicode__(self):
        return '%s' % self.name

class Wiki(models.Model):
    '''
    Artículo de documentación. Sirve para mostrar
    información sobre procedimiendo y el sitio web.
    Cualquiera puede editar el Wiki.
    '''
    accepted = models.ForeignKey(WikiVersion, null=True, blank=True,
                    related_name="%(app_label)s_%(class)s_accepted_related")
    open_comments = models.BooleanField(default=True)
    comments = models.ManyToManyField(Comment, null=True, blank=True)
    # Impedir cambios a usuarios normales.
    close = models.BooleanField(default=False)
    def __unicode__(self):
        return '%s' % self.accepted.name

class NewsCategory(models.Model):
    '''
    Categorías de las noticias de portada
    '''
    name = models.CharField(max_length=32, blank=False)
    image = models.ForeignKey(Image, null=True, blank=True)
    def __unicode__(self):
        return '%s' % self.name

class News(models.Model):
    '''
    Una noticia para mostrarse en portada
    '''
    name = models.CharField(max_length=128, blank=False)
    text = models.TextField()
    user = models.ManyToManyField(User)
    date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(blank=True)
    categories = models.ManyToManyField(NewsCategory, null=True, blank=True)
    open_comments = models.BooleanField(default=True)
    comments = models.ManyToManyField(Comment, null=True, blank=True)
    def __unicode__(self):
        return '%s' % self.name