$(document).ready(function(){

    $("#but_search_directors").click(function (){
        $("#butt_next_comp_dir").css("display",'none')
        $("#butt_prev_comp_dir").css("display",'none')
        $("#butt_all_again").css("display",'none')
        $("#butt_comps").css("display",'block')
        $("#but_search_directors_return").css("display",'block')
        $("#but_search_directors").css("width",'78px')
        show_this_director();
    });
    $("#but_search_directors_return").click(function (){
        $("#butt_next_comp_dir").css("display",'none')
        $("#butt_prev_comp_dir").css("display",'none')
        $("#butt_all_again").css("display",'none')
        $("#butt_comps").css("display",'block')
        $("#but_search_directors_return").css("display",'none')
        $("#but_search_directors").css("width",'190px')
        show_all();
    });

    $("#butt_comps").click(function () {
        show_comp_next()
        $("#butt_next_comp_dir").css("display",'block')
        $("#butt_prev_comp_dir").css("display",'block')
        $("#butt_all_again").css("display",'block')
        $("#butt_comps").css("display",'none')
        $("#but_search_directors_return").css("display",'none')
        $("#but_search_directors").css("width",'190px')
    });
    $("#butt_next_comp_dir").click(show_comp_next);
    $("#butt_prev_comp_dir").click(show_comp_prev);

    $("#butt_all_again").click(function () {
        show_all()
        $("#butt_next_comp_dir").css("display",'none')
        $("#butt_prev_comp_dir").css("display",'none')
        $("#butt_all_again").css("display",'none')
        $("#butt_comps").css("display",'block')
        $("#but_search_directors_return").css("display",'none')
        $("#but_search_directors").css("width",'190px')
    });
    let comp_id = 0;
    let count_comps=1;

    var width = 800, height = 800;

    var force = d3.layout.force()
        .charge(-200).linkDistance(30).size([width, height]);

    show_all()

    $.get('/count_components_dir', function (data) {
        count_comps=data;
        $('#count_comps_dir').text("Quantity: "+data);
        $('#butt_comps').prop('disabled',false);
    });

    function show_comp_next() {
        comp_id=(comp_id+1)%count_comps;
        show_comp()
    }
    function show_comp_prev() {
        comp_id=(comp_id-1)%count_comps;
        show_comp()
    }

    function show_comp() {
        d3.select("#graph").selectAll("*").remove()
        var svg = d3.select("#graph").append("svg")
            .attr('viewBox', `-300 -300 2000 2000`)
            .attr("pointer-events", "all");
        $.get("/components_show_dir", {comp_id: comp_id}, function (graph) {
            create_dir_graph(force,svg,graph);
        });
        mouswheel_bind();
    }

    function show_all() {
        d3.select("#graph").selectAll("*").remove()
        var svg = d3.select("#graph").append("svg")
            .attr('viewBox',`-300 -300 2000 2000`)
            .attr("pointer-events", "all");

        d3.json("/graph_dir", function(error, graph) {
            if (error) return;
            create_dir_graph(force,svg,graph);
        });
        mouswheel_bind();
    }

    function  show_this_director() {
        d3.select("#graph").selectAll("*").remove()
        var svg = d3.select("#graph").append("svg")
            .attr('viewBox',`-300 -300 2000 2000`)
            .attr("pointer-events", "all");
        $.get('/specific_director_graph', {director: $('#dirs_for_search').val()}, function (graph) {
            create_dir_graph(force,svg,graph);
        });
        mouswheel_bind();
    }
});

function create_dir_graph(force,svg,graph) {
    force.nodes(graph.nodes).links(graph.links).start();

    var link = svg.selectAll(".link")
        .data(graph.links).enter()
        .append("line").attr("class", "link");
    var node = svg.selectAll(".node")
        .data(graph.nodes).enter()
        .append("a")
        .attr("href", function (data) { return data.wiki })
        .attr("target","_blank")
        .append("circle")

        .attr("class", function (d) { return "node "+d.label })
        .attr("r", 10)
        .call(force.drag);

    // html title attribute
    node.append("title")
        .text(function (d) { return d.title; })
    // force feed algo ticks
    force.on("tick", function() {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
    });
}