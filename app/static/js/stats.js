$(document).ready(function(){
    let ctx1 = document.getElementById('myChart').getContext('2d');
    let ctx2 = document.getElementById('myChart2').getContext('2d');
    let ctx3 = document.getElementById('myChart3').getContext('2d');
    let ctx4 = document.getElementById('myChart4').getContext('2d');
    let ctx5 = document.getElementById('myChart5').getContext('2d');
    let ctx6 = document.getElementById('myChart6').getContext('2d');

    let myChart1 = new chart(ctx1,'horizontalBar',[],'',[]);
    let myChart2 = new chart(ctx2,'horizontalBar',[],'',[]);
    let myChart3 = new chart(ctx3,'horizontalBar',[],'',[]);
    let myChart4 = new chart(ctx4,'horizontalBar',[],'',[]);
    let myChart5 = new chart(ctx5,'horizontalBar',[],'',[]);
    let myChart6 = new chart(ctx6,'horizontalBar',[],'',[]);

    get_stats_time();
    get_stats_genre();
    get_last_career();

    $("#years_but").click(get_stats_time);
    $("#genres_but").click(get_stats_genre);


    function get_stats_time(){
        get_act_max_film_time();
        get_dir_max_film_time();
        get_orig_perc_time()
    }


    function get_stats_genre(){
        get_dir_max_film_genre();
        get_act_max_film_genre();
    }


    setInterval(function () {
        if ($('#years_from').val() >= $('#years_to').val()){
            $('#years_but').prop('disabled', true);
        }
        else {
            $('#years_but').prop('disabled', false);
        }
    },100);


    function get_act_max_film_time() {
        $("#myChart").css('display', 'none');
        $("#cube-loader.myChart").css('display', 'block');

        $.get('/get_act_max_film_time', {
            year_from: $('#years_from').val(),
            year_to: $('#years_to').val()
        }, function (data) {
            $("#myChart").css('display', 'block');
            $("#cube-loader.myChart").css('display', 'none');

            myChart1.destroy()
            let labels = []
            let values = []
            for (i = 0; i < data.length; i++) {
                labels.push(data[i][0])
                values.push(data[i][1])
            }
            myChart1 = chart(ctx1, 'horizontalBar', labels, 'Кол-во фильмов с актёром за выбранный период', values);

        });
    }


    function get_dir_max_film_time() {
        $("#myChart2").css('display', 'none');
        $("#cube-loader.myChart2").css('display', 'block');

        $.get('/get_dir_max_film_time', {
            year_from: $('#years_from').val(),
            year_to: $('#years_to').val()
        }, function (data) {
            $("#myChart2").css('display', 'block');
            $("#cube-loader.myChart2").css('display', 'none');

            myChart2.destroy()
            let labels = []
            let values = []
            for (i = 0; i < data.length; i++) {
                labels.push(data[i][0])
                values.push(data[i][1])
            }
            myChart2 = chart(ctx2, 'horizontalBar', labels, 'Кол-во фильмов у режиссёра за выбранный период', values);
        });
    }


    function get_orig_perc_time() {
        $("#myChart3").css('display', 'none');
        $("#cube-loader.myChart3").css('display', 'block');

        $.get('/get_orig_perc_time', {
            year_from: $('#years_from').val(),
            year_to: $('#years_to').val()
        }, function (data) {
            $("#myChart3").css('display', 'block');
            $("#cube-loader.myChart3").css('display', 'none');

            myChart3.destroy()
            let labels = []
            let values = []
            for (i = 0; i < data.length; i++) {
                labels.push(data[i][0])
                values.push(data[i][1])
            }
            if (labels.length && values.length) {
                myChart3 = chart(ctx3, 'pie', labels, 'Процент фильмов за выбранный период', values, 'Процент фильмов за выбранный период');
            } else {
                ctx3.fillStyle = "#00F";
                ctx3.font = "italic 10pt Arial";
                ctx3.fillText("Фильмы за выбранный период отсутствуют", 20, 50);
            }
        });
    }


    function get_last_career() {
        $("#myChart4").css('display', 'none');
        $("#cube-loader.myChart4").css('display', 'block');

        $.get('/get_last_career', function (data) {
            $("#myChart4").css('display', 'block');
            $("#cube-loader.myChart4").css('display', 'none');

            myChart4.destroy()
            let labels = []
            let values = []
            for (i = 0; i < data.length; i++) {
                labels.push(data[i][0])
                values.push(data[i][1])
            }
            myChart4 = chart(ctx4, 'horizontalBar', labels, 'Кол-во актёров, закончивших карьеру на фильме', values);
        });
    }
    

    function get_act_max_film_genre() {
        $("#myChart5").css('display', 'none');
        $("#cube-loader.myChart5").css('display', 'block');

        $.get('/get_act_max_film_genre', {
            genre: $('#genres').val()
        }, function (data) {
            $("#myChart5").css('display', 'block');
            $("#cube-loader.myChart5").css('display', 'none');

            myChart5.destroy()
            let labels = []
            let values = []
            for (i = 0; i < data.length; i++) {
                labels.push(data[i][0])
                values.push(data[i][1])
            }
            myChart5 = chart(ctx5, 'horizontalBar', labels, 'Кол-во фильмов с актёром в выбранном жанре', values);
        });
    }
    

    function get_dir_max_film_genre() {
        $("#myChart6").css('display', 'none');
        $("#cube-loader.myChart6").css('display', 'block');

        $.get('/get_dir_max_film_genre', {
            genre: $('#genres').val()
        }, function (data) {
            $("#myChart6").css('display', 'block');
            $("#cube-loader.myChart6").css('display', 'none');

            myChart6.destroy()
            let labels = []
            let values = []
            for (i = 0; i < data.length; i++) {
                labels.push(data[i][0])
                values.push(data[i][1])
            }
            myChart6 = chart(ctx6, 'horizontalBar', labels, 'Кол-во фильмов у режиссёра в выбранном жанре', values);
        });
    }


    function chart(ctx,type,labels,label,values, title) {
        let myChart = new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: values,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                title: {
                    display: Boolean(title),
                    text: title
                }
            }
        });
        return myChart;
    }
});