$(document).ready(function(e) {
    $('img[usemap]').rwdImageMaps();  /* automatically size the image map on the card */
    $('div[data-role="page"]').on( "pagebeforeshow", function (event, ui) {
        slider = $(this).find('select');
        if (slider.val() == 'lezen' && $.cookie('spelen')) {
            slider.val('spelen').slider('refresh');
        };
        if (slider.val() == 'spelen' && ! $.cookie('spelen')) {
            slider.val('lezen').slider('refresh');
        }
    });
    $('select').on( "change", function(event, ui) {
        slider = $(this);
        if (slider.val() == 'lezen' && $.cookie('spelen')) {
            $.removeCookie('spelen',{ path: '/', expires: 1 });  /* need the options to match the cookie! */
            slider.val('lezen').slider('refresh');
        };
        if (slider.val() == 'spelen' && ! $.cookie('spelen')) {
            $.cookie('spelen', "true", { path: '/', expires: 1 });
            slider.val('spelen').slider('refresh');
            $('.spelregels').popup('open');
        }
    });
});
/*
 following section fixes flickering of page transitions on Android
 and must be imported between jQuery and jQuery Mobile
 */
$(document).bind("mobileinit", function()
{
   if (navigator.userAgent.indexOf("Android") != -1)
   {
     $.mobile.defaultPageTransition = 'none';
     $.mobile.defaultDialogTransition = 'none';
   }
});
