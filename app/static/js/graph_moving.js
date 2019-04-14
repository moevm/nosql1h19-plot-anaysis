
$(document).ready(function(){
    var change_size = 2000;
    var vbox_x = -300;
    var vbox_y = -300;
    $('svg').bind('mousewheel', function(e){
        if(e.originalEvent.wheelDelta /120 > 0) {
            //console.log('scrolling up !'+change_size);
            if (change_size > 200)
                change_size -= 150;
                vbox_x += 75;
                vbox_y += 30;
        }
        else{
            //console.log('scrolling down !'+change_size);
            change_size += 150;
            vbox_x -= 75;
            vbox_y -= 30;
        }
        $('svg').attr('viewBox',`${vbox_x} ${vbox_y} ${change_size} ${change_size}`)
    });
    $('svg').bind('mousedown', function(e){
        //console.log('ke!');
        document.onmousemove = function(k){
            vbox_x+=(k.pageX-e.pageX)/100;
            vbox_y+=(k.pageY-e.pageY)/100;
           // console.log(vbox_x,vbox_y)
            $('svg').attr('viewBox',`${vbox_x} ${vbox_y} ${change_size} ${change_size}`)
        }
    });
    $('svg').bind('mouseup', function(e){
        //console.log('wke!');
        document.onmousemove = null
    });




    $('#zoom-out-btn').on('click', function() {
        change_size = 5000
        vbox_x = -2000;
        vbox_y = -800;
        $('svg').attr('viewBox',`${vbox_x} ${vbox_y} ${change_size} ${change_size}`)
    })
});