$(document).ready(function(){
    get_table_plot_dir();
    get_table_plot_genre();
    get_table_universal_words();

    $("#directors_but_plot").click(get_table_plot_dir);
    $("#genres_but_plot").click(get_table_plot_genre);

    function get_table_plot_dir() {
        $("#words_for_dir").css('display', 'none');
        $("#cube-loader.words_for_dir").css('display', 'block');
        $.get('/get_table_plot_dir', {
            dir: $('#plot_directors').val()
        }, function (data) {
            $("#words_for_dir").css('display', 'block');
            $("#cube-loader.words_for_dir").css('display', 'none');
            $("#tbody_dir_plot").empty();
            for (let i = 0; i < data.length; i++) {
                let tbody = document.getElementById('tbody_dir_plot');
                let row = document.createElement("TR");
                tbody.appendChild(row);

                let td1 = document.createElement("TD");
                let td2 = document.createElement("TD");

                row.appendChild(td1);
                row.appendChild(td2);
                td1.innerHTML = data[i][0];
                td2.innerHTML = data[i][1];
            }
        });
    }

    function get_table_plot_genre() {
        $("#words_for_genre").css('display', 'none');
        $("#cube-loader.words_for_genre").css('display', 'block');
        $.get('/get_table_plot_genre', {
            genre: $('#plot_genres').val()
        }, function (data) {
            $("#words_for_genre").css('display', 'block');
            $("#cube-loader.words_for_genre").css('display', 'none');
            $("#tbody_genre_plot").empty();
            for (let i = 0; i < data.length; i++) {
                let tbody = document.getElementById('tbody_genre_plot');
                let row = document.createElement("TR");
                tbody.appendChild(row);

                let td1 = document.createElement("TD");
                let td2 = document.createElement("TD");

                row.appendChild(td1);
                row.appendChild(td2);
                td1.innerHTML = data[i][0];
                td2.innerHTML = data[i][1];
            }
        });
    }

    function get_table_universal_words() {
        $("#universal_words").css('display', 'none');
        $("#cube-loader.universal_words").css('display', 'block');
        $.get('/get_table_universal_words', function (data) {
            $("#universal_words").css('display', 'block');
            $("#cube-loader.universal_words").css('display', 'none');
            $("#tbody_universal_words").empty();
            for (let i = 0; i < data.length; i++) {
                let tbody = document.getElementById('tbody_universal_words');
                let row = document.createElement("TR");
                tbody.appendChild(row);

                let td1 = document.createElement("TD");
                let td2 = document.createElement("TD");

                row.appendChild(td1);
                row.appendChild(td2);
                td1.innerHTML = data[i][0];
                td2.innerHTML = data[i][1];
            }
        });
    }
});