$(document).ready(function() {
    $(".butt_menu_components").click(menu_show);
    let menu_show_flag = false;
    function menu_show() {
        if (menu_show_flag == false) {
            $('.butt_menu_components').animate({'margin-right': '260px'});
			$('.show').text('Close menu panel for search on graph');
            $('.solo_components_menu').animate({'margin-right': '0px'});
        }
        else {
            $('.butt_menu_components').animate({'margin-right': '0px'});
			$('.show').text('Show menu panel for search on graph');
            $('.solo_components_menu').animate({'margin-right': '-260px'});
        }
        menu_show_flag = !menu_show_flag;
    }
});