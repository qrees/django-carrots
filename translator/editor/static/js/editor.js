(function(){
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function setup_csrf(){
        var csrftoken = getCookie('csrftoken');
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }

    function ajax_post(data, callback) {
        $.ajax({
            'data': JSON.stringify(data),
            'dataType': 'json',
            'url': '/set_valid.json',
            'type': 'POST',
            'success': callback
        })
    }

    function set_valid($el){
        console.log($el);
        var target = $el.parents('[data-lang]');
        var target_hash = target.data('hash')
        var target_language = target.data('lang');
        var target_text = target.find('textarea').val();
        var source = target.parent().find("[data-is-source=True]");
        var source_hash = source.data('hash');
        var source_lang = source.data('lang');
        var data = {
            'source_hash': source_hash,
            'source_language': source_lang,
            'target_hash': target_hash,
            'target_language': target_language,
            'target_text': target_text
        }
        ajax_post(data, function (response_data) {
            target.
                find('.status-invalid, .status-valid').
                toggleClass('status-valid').
                toggleClass('status-invalid');
        })
    }
    window['set_valid'] = set_valid;

    function main(){
        setup_csrf();
        $('[data-onclick]').on('click', function(event){
            var target = $(event.currentTarget);
            var onclick = target.data('onclick');
            window[onclick](target);
        });
        console.log('ready');
    };

    $(document).ready(main);
})();
