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
    path = '/export'
    
    try:
        os.mkdir(path)
    except OSError:
        print('Создать директорию %s не удалось' % path)
    else:
        print('Успешно создана директория %s ' % path)

    db.run("CALL apoc.export.csv.query({query}, {path},  null)", {"query": movies_data, "path": os.getcwd() + "/export/movies.csv"})

    return send_from_directory(os.getcwd() + '/export', 'movies.csv', as_attachment=True, mimetype='text/csv', attachment_filename='movies.csv')
