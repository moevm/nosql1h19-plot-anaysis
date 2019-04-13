import os
from json import dumps
from flask import Flask, g, Response, request, render_template, send_from_directory

from neo4j import GraphDatabase, basic_auth

from app import app

password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver('bolt://localhost',auth=basic_auth("neo4j", password))


def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()


@app.route("/")
def get_index():
    return render_template('index.html')


def serialize_movie(movie):
    return {
        'id': movie['id'],
        'title': movie['title'],
        'plot': movie['plot'],
        'released': movie['released'],
        'genre': movie['genre'],
        'origin': movie['origin']
    }


def serialize_cast(cast):
    return {
        'name': cast[0],
        'job': cast[1],
        'role': cast[2]
    }


@app.route("/act_graph")
def get_act_graph():
    return render_template("act_graph.html")


@app.route("/dir_graph")
def get_dir_graph():
    return render_template("dir_graph.html")


@app.route("/import_page")
def get_import_page():
    return render_template("import_page.html")


@app.route("/graph")
def get_graph():
    db = get_db()
    results = db.run("MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) WHERE a.name<>'Unknown'"
             "RETURN m.title as movie,m.wiki as wiki, collect(a.name) as cast "
             "LIMIT {limit}", {"limit": request.args.get("limit", 100)})
    nodes = []
    rels = []
    i = 0
    for record in results:
        nodes.append({"title": record["movie"], "label": "movie","wiki":record["wiki"]})
        target = i
        i += 1
        for name in record['cast']:
            actor = {"title": name, "label": "actor"}
            try:
                source = nodes.index(actor)
            except ValueError:
                nodes.append(actor)
                source = i
                i += 1
            rels.append({"source": source, "target": target})
    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")


@app.route("/graph_dir")
def get_graph_dir():
    db = get_db()
    results = db.run("MATCH (m:Movie)<-[:DIRECTED]-(a:Person) WHERE a.name<>'Unknown'"
             "RETURN m.title as movie, m.wiki as wiki, collect(a.name) as cast "
             "LIMIT {limit}", {"limit": request.args.get("limit", 100)})
    nodes = []
    rels = []
    i = 0
    for record in results:
        nodes.append({"title": record["movie"], "label": "movie","wiki":record["wiki"]})
        target = i
        i += 1
        for name in record['cast']:
            director = {"title": name, "label": "director"}
            try:
                source = nodes.index(director)
            except ValueError:
                nodes.append(director)
                source = i
                i += 1
            rels.append({"source": source, "target": target})
    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")


@app.route("/search")
def get_search():
    try:
        q = request.args["q"]
    except KeyError:
        return []
    else:
        db = get_db()
        results = db.run("MATCH (movie:Movie) "
                 "WHERE movie.title =~ {title} "
                 "RETURN movie", {"title": "(?i).*" + q + ".*"}
        )
        return Response(dumps([serialize_movie(record['movie']) for record in results]),
                        mimetype="application/json")


@app.route("/movie/<title>")
def get_movie(title):
    db = get_db()
    results = db.run("MATCH (movie:Movie {title:{title}}) "
             "OPTIONAL MATCH (movie)<-[r]-(person:Person) "
             "RETURN movie.title as title,"
             "movie.plot as plot,"
             "collect([person.name, "
             "         head(split(lower(type(r)), '_')), r.roles]) as cast "
             "LIMIT 1", {"title": title})

    result = results.single();
    return Response(dumps({"title": result['title'],
                           "plot": result['plot'],
                           "cast": [serialize_cast(member)
                                    for member in result['cast']]}),
                    mimetype="application/json")


@app.route("/import")
def import_graph_data():
    db = get_db()
    db.run("MATCH ()-[r]->() DELETE r")
    db.run("MATCH (n) DELETE n")
    db.run(
"load csv with headers from 'file:///wiki_movie_plots_deduped.csv' as line "
"merge (n:Movie {title:line.Title, released:line.ReleaseYear, origin:line.Origin, genre:line.Genre, wiki:line.WikiPage, plot:line.Plot}) "
"FOREACH (actor in split(line.Cast, ',') | "
"merge (a:Person {name:replace(replace(replace(actor,'[',''),']',''),'\"','')}) merge (a)-[:ACTED_IN]->(n)) "
"FOREACH (director in split(line.Director, ',') | "
"FOREACH (dir in split(director,' and ') | "
"merge (d:Person {name:replace(replace(replace(dir,'[',''),']',''),'\"','')}) merge (d)-[:DIRECTED]->(n)))"
    )
  
    return Response(dumps({"message": "Import completed"}),
                    mimetype="application/json")


@app.route("/export")
def export_graph_data():
    db = get_db()
    movies_data = "match (n:Movie)<-[:ACTED_IN]-(p:Person), (n)<-[:DIRECTED]-(d:Person) return n.released as ReleaseYear, n.title as Title, n.origin as Origin,collect( distinct d.name) as Director, collect( distinct p.name) as Cast, n.genre as Genre, n.wiki as WikiPage, n.plot as Plot"
    path = 'export'
    
    try:
        os.mkdir(path)
    except OSError:
        print('Создать директорию %s не удалось' % path)
    else:
        print('Успешно создана директория %s ' % path)
    print(os.getcwd())
    db.run("CALL apoc.export.csv.query({query}, {path},  null)", {"query":movies_data,"path": os.getcwd() + "/export/movies.csv"})

    return send_from_directory(os.getcwd() + '/export', 'movies.csv', as_attachment=True, mimetype='text/csv', attachment_filename='movies.csv')

@app.route("/stats")
def get_stats_page():
    db = get_db()
    years = db.run("match (n) return tointeger(min(n.released)) as min,tointeger(max(n.released)) as max")
    years = years.single()
    years = [(x)for x in range(years['min'],years['max']+1)]
    genres=[]
    tmp = db.run("match(n:Movie) where n.genre <> 'unknown' and not n.genre contains ',' and not trim(n.genre) contains '/' return trim(n.genre) as genre, count(trim(n.genre)) as counts order by counts desc limit 20")
    for genre in tmp:
        genres.append(genre['genre'])
    return render_template("stats.html", years = years, genres = genres)

@app.route("/get_act_max_film_time", methods=['GET'])
def get_act_max_film_time():
    year_from = request.args["year_from"]
    year_to= request.args["year_to"]
    db = get_db()
    data=[]
    acts = db.run("match (n)-[r:ACTED_IN]-(p:Person) where n.released> {from} and n.released < {to} and p.name <> 'Unknown' return p.name as name,count(r) as counts order by counts desc limit 5",{'from':year_from,'to':year_to})
    for act in acts:
        data.append([act["name"],act["counts"]])
    return Response(dumps(data), mimetype="application/json")

@app.route("/get_dir_max_film_time")
def get_dir_max_film_time():
    year_from = request.args["year_from"]
    year_to= request.args["year_to"]
    db = get_db()
    data=[]
    dirs = db.run("match (n)-[r:DIRECTED]-(p:Person) where n.released> {from} and n.released < {to} and p.name <> 'Unknown' return p.name as name,count(r) as counts order by counts desc limit 5",{'from':year_from,'to':year_to})
    for dir in dirs:
        data.append([dir["name"],dir["counts"]])
    return Response(dumps(data), mimetype="application/json")


@app.route("/get_last_career")
def get_last_career():
    db = get_db()
    last_films=[]
    last_film = db.run("match (p:Person)-[:ACTED_IN]-(n:Movie) return p.name, collect(n.title)[-1] as last_f")
    for film in last_film:
        last_films.append(film["last_f"])
    last_films = db.run("with {data} as films unwind (films) as film return film as film,count(film) as count order by count desc limit 5",{'data':last_films})
    data =[]
    for film in last_films:
            data.append([film["film"],film["count"]])
    return Response(dumps(data), mimetype="application/json")


@app.route("/get_act_max_film_genre")
def get_act_max_film_genre():
    genre = request.args["genre"]
    db = get_db()
    data=[]
    acts = db.run("match (n)-[r:ACTED_IN]-(p:Person) where n.genre contains {genre} and p.name <> 'Unknown' return p.name as name,count(r) as counts order by counts desc limit 5",{'genre':genre})
    for act in acts:
        data.append([act["name"],act["counts"]])
    return Response(dumps(data), mimetype="application/json")

@app.route("/get_dir_max_film_genre")
def get_dir_max_film_genre():
    genre = request.args["genre"]
    db = get_db()
    data=[]
    dirs = db.run("match (n)-[r:DIRECTED]-(p:Person) where n.genre contains {genre} and p.name <> 'Unknown' return p.name as name,count(r) as counts order by counts desc limit 5",{'genre':genre})
    for dir in dirs:
        data.append([dir["name"],dir["counts"]])
    return Response(dumps(data), mimetype="application/json")


@app.route("/get_orig_perc_time")
def get_orig_perc_time():
    year_from = request.args["year_from"]
    year_to= request.args["year_to"]
    db = get_db()
    data=[]
    percs = db.run("match (n:Movie) WHERE n.released> {from} and n.released < {to} with count(n) as total match (l:Movie) WHERE l.released> {from} and l.released < {to} return l.origin as origin, tofloat(100.00*count(l)/total) as perc order by perc desc",{'from':year_from,'to':year_to})
    for perc in percs:
        data.append([perc["origin"],perc["perc"]])
    return Response(dumps(data), mimetype="application/json")

@app.route("/plot_analys")
def get_plot_analys_page():
    return render_template("plot_analys.html")