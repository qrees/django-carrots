(function(){

    function toggle_valid($el){
        console.log($el);
        $.ajax({

        });
    }
    window['toggle_valid'] = toggle_valid;

    function main(){
        $('[data-onclick]').on('click', function(event){
            var target = $(event.currentTarget);
            var onclick = target.data('onclick');
            window[onclick](target);
        });
        console.log('ready');
    };

    $(document).ready(main);
})();
