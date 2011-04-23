$(document.body).ready(function (){
    (function($) {
        $.fn.ajaxLoader = function() {
            var data = this;
            var default_ajax_enter = {'#content': {'to': '#content',
                                                   'action': 'replace',
                                                   'effect': 'instant'
                                                   },
                                      '#title': {'to': 'head title',
                                                     'action': 'replace',
                                                     'effect': 'instant'
                                                   }
                                      }
            var ajax_enter = jQuery.extend(default_ajax_enter, ajax_enter);
            $.each(ajax_enter, function(key, val){
                var from = $(data).filter(key).html();
                if(val['action']=='replace'){
                    $(val['to']).html(from)
                } else {
                    val['action'](data, key, val)
                }
            });
        }
    })(jQuery);
    
    gotlibs = new Array()
    getLibrary = function(url){
        if($.inArray(url, gotlibs)==-1){
            $.getScript(url);
            gotlibs.push(url)
        }
    }
    
    $(function() {
        $("#logs").dialog({width: 400, height: 200,
                           position: [$(document).width() - 450, 40]
        });
    });
    logging = function(){
        function print(mode, text){
            if(console.debug){
                console.debug(mode + '  ' + text);
            }
            var p = $('<p></p>')
            $(p).addClass(mode)
            $(p).text(text)
            $('#logs').append(p)
        }
        this.debug = function(text){
            print('DEBUG', text)
        }
        this.warning = function(text){
            print('WARNING', text)
        }
    }
    logging = new logging()
    
    // En los inputs y textareas, mostrar el texto de
    // ayuda solo si el campo está vacio
    $('input, textarea').live('focusin', function(){
        if($(this).attr('title')==$(this).val()){
            $(this).val('');
        }
    }).live('focusout', function(){
        if($(this).val()==''){
            $(this).val($(this).attr('title'));
        }
    });
    
    // Función para mostrar el texto de ayuda en todos
    // los inputs y textareas del documento
    inputTitle = function(){
        $.each($('input, textarea'), function(key, val){
            if($(this).is('textarea')){
                $(this).val = $(this).text
            }
            if($(val).attr('title')){
                if($(val).val()==''){
                    $(val).val($(val).attr('title'));
                }
            }
        });
    }
    
    // Cambiar los links estáticos por links del tipo
    // ajax (añadir #!)
    changeLinks = function(){
        $.each($('a.local'), function(key, val){
            if($(val).attr('href')[0]!='#'){
                $(val).attr('href', '#!' + $(val).attr('href'))
            }
        });
    }
    
    htmlAjax = function(hash, post){
        logging.debug('Cargando mediante Ajax ' + hash);
        if(post){
            var type = 'POST'
        } else {
            var type = 'GET'
        }
        $.ajax({
        url: hash + '?ajax=1',
        dataType: "html",
        type: type,
        data: post,
        success: function(data){
            eval($(data).filter('#prevscripts').html());
            $(data).ajaxLoader();
            // Se ha terminado de poner el contenido, se ejecutan
            // scripts de después
            eval($(data).filter('#scripts').html());
        }
        });
    }
    // Cargar el contenido mediante cambios en la URL
    // (del tipo Ajax)
    $.History.bind(function(hash){
        if(hash[0]!='!'){
            logging.warning('La petición mediante Ajax era incorrecta' +
                            'y se denegó. hash:' + hash);
            return
        }
        var hash = hash.substring(1, hash.length)
        htmlAjax(hash)
    });
    
    AutoComplete = function(input, selectinput, url){
        $(input).autocomplete({
            source: function(request, response) {
                $.ajax({
                    url: url,
                    dataType: "json",
                    data: {term: request.term},
                    success: function(data){
                        response($.map(data, function(item){
                            return {label: item[1],
                                    value: item[1],
                                    id: item[0]
                                    }
                        }));
                    }
                });
            },
            minLength: 2,
            select: function(event, ui){
                    $(selectinput).children('option').attr('value', ui.item.id)
                },
            open: function() {
                $(this).removeClass("ui-corner-all").addClass("ui-corner-top");
            },
            close: function() {
                $(this).removeClass("ui-corner-top").addClass("ui-corner-all");
            }
        });
    }
});