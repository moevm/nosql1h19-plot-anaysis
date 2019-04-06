$(function () {
    function showMovie(title) {
        $.get("/movie/" + encodeURIComponent(title),
            function (data) {
                if (!data) return;
                $("#title").text(data.title);
                $("#plot").text(data.plot);
                var $list = $("#crew").empty();
                data.cast.forEach(function (cast) {
                    $list.append($("<li>" + cast.name + "</li>"));
                });
            }, "json");
        return false;
    }
    function search() {
        var query=$("#search").find("input[name=search]").val();
        $.get("/search?q=" + encodeURIComponent(query),
            function (data) {
                var t = $("table#results tbody").empty();
                if (!data || data.length == 0) return;
                data.forEach(function (movie) {
                    $("<tr><td class='movie'>" + movie.title + "</td><td>" + movie.released + "</td><td>" + movie.origin + "</td><td>" + movie.genre + "</td></tr>").appendTo(t)
                        .click(function() { showMovie($(this).find("td.movie").text());})
                });
                showMovie(data[0].title);
            }, "json");
        return false;
    }
    $("#search").submit(search);
    search();
})