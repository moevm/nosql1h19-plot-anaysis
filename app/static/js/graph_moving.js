
$(document).ready(function(){
    var change_size=2000;
    var vbox_x = -300;
    var vbox_y = -300;
    $('svg').bind('mousewheel', function(e){
        if(e.originalEvent.wheelDelta /120 > 0) {
            //console.log('scrolling up !'+change_size);
            if (change_size > 200)
                change_size-=100;
        }
        else{
            //console.log('scrolling down !'+change_size);
            change_size+=100;
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
});