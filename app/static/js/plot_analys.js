$(document).ready(function(){
    get_table_plot_dir();
    get_table_plot_genre();
    get_table_universal_words();

    $("#directors_but_plot").click(get_table_plot_dir);
    $("#genres_but_plot").click(get_table_plot_genre);

    function get_table_plot_dir() {
        $.get('/get_table_plot_dir', {
            dir: $('#plot_directors').val()
        }, function (data) {
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
        $.get('/get_table_plot_genre', {
            genre: $('#plot_genres').val()
        }, function (data) {
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
        $.get('/get_table_universal_words', function (data) {
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