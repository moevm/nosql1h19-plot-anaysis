from string import punctuation
import os
import shutil
from json import dumps
from flask import Flask, g, Response, request, render_template, send_from_directory, abort

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
    db = get_db()
    actors=[]
    tmp = db.run("match(n:Movie)-[:ACTED_IN]-(p:Person) WHERE p.name<>'Unknown' return distinct p.name as name order by name")
    for act in tmp:
        actors.append(act['name'])
    return render_template("act_graph.html", actors=actors)


@app.route("/dir_graph")
def get_dir_graph():
    db = get_db()
    directors=[]
    tmp = db.run("match(n:Movie)-[:DIRECTED]-(p:Person) WHERE p.name<>'Unknown' return distinct p.name as name order by name")
    for dir in tmp:
        directors.append(dir['name'])
    return render_template("dir_graph.html", directors=directors)


@app.route("/import_page")
def get_import_page():
    return render_template("import_page.html")


@app.route("/graph")
def get_graph():
    db = get_db()
    results = db.run("MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) WHERE a.name<>'Unknown'"
             "RETURN m.title as movie,m.wiki as wiki, collect(a.name) as cast "
             "LIMIT {limit}", {"limit": request.args.get("limit", 200)})
    nodes,rels = for_graph(results,'actor')
    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")

@app.route("/graph_dir")
def get_graph_dir():
    db = get_db()
    results = db.run("MATCH (m:Movie)<-[:DIRECTED]-(a:Person) WHERE a.name<>'Unknown'"
             "RETURN m.title as movie, m.wiki as wiki, collect(a.name) as cast "
             "LIMIT {limit}", {"limit": request.args.get("limit", 200)})
    nodes,rels = for_graph(results,'director')
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


@app.route("/import", methods=['GET', 'POST'])
def import_graph_data():
    if request.method == 'POST':
        f = request.files.get('csv_import_file')
        if f:
            path = 'import'
            try:
                shutil.rmtree('./import')
            except FileNotFoundError:
                pass
            try:
                os.mkdir(path)
            except OSError:
                print('Создать директорию %s не удалось' % path)
                abort(500)
            else:
                print('Успешно создана директория %s ' % path)

            f.save(os.getcwd() + "/import/import.csv")

            return Response(dumps({"message": "File Loaded"}),
                            mimetype="application/json")
        else:
            abort(400)
    else:
        f_path = os.getcwd().replace("\\","/") + '/import/import.csv'
        f_path = f_path.replace(' ', '%20')
        db = get_db()
        db.run("MATCH ()-[r]->() DELETE r")
        db.run("MATCH (n) DELETE n")
        db.run(
        "load csv with headers from 'file:///{0}' as line ".format(f_path) +
        "merge (n:Movie {title:line.Title, released:line.ReleaseYear, origin:line.Origin, genre:line.Genre, wiki:line.WikiPage, plot:line.Plot}) "
        "FOREACH (actor in split(line.Cast, ',') | "
        "merge (a:Person {name:replace(replace(replace(actor,'[',''),']',''),'\"','')}) merge (a)-[:ACTED_IN]->(n)) "
        "FOREACH (director in split(line.Director, ',') | "
        "FOREACH (dir in split(director,' and ') | "
        "merge (d:Person {name:replace(replace(replace(dir,'[',''),']',''),'\"','')}) merge (d)-[:DIRECTED]->(n)))",
        {"path":f_path})
      
        return Response(dumps({"message": "Import completed"}),
                        mimetype="application/json")


@app.route("/export")
def export_graph_data():
    db = get_db()
    movies_data = "match (n:Movie)<-[:ACTED_IN]-(p:Person), (n)<-[:DIRECTED]-(d:Person) return n.released as ReleaseYear, n.title as Title, n.origin as Origin,collect( distinct d.name) as Director, collect( distinct p.name) as Cast, n.genre as Genre, n.wiki as WikiPage, n.plot as Plot"
    
    path = 'export'
    try:
        shutil.rmtree('./' + path)
    except FileNotFoundError:
        pass
    try:
        os.mkdir(path)
    except OSError:
        print('Создать директорию %s не удалось' % path)
    else:
        print('Успешно создана директория %s ' % path)

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
    acts = db.run("match (n)-[r:ACTED_IN]-(p:Person) where toInteger(n.released) >= {from} and toInteger(n.released) < {to} and p.name <> 'Unknown' return p.name as name,count(r) as counts order by counts desc limit 5",{'from':int(year_from),'to':int(year_to)})
    for act in acts:
        data.append([act["name"],act["counts"]])
    return Response(dumps(data), mimetype="application/json")

@app.route("/get_dir_max_film_time")
def get_dir_max_film_time():
    year_from = request.args["year_from"]
    year_to= request.args["year_to"]
    db = get_db()
    data=[]
    dirs = db.run("match (n)-[r:DIRECTED]-(p:Person) where toInteger(n.released) >= {from} and toInteger(n.released) < {to} and p.name <> 'Unknown' return p.name as name,count(r) as counts order by counts desc limit 5",{'from':int(year_from),'to':int(year_to)})
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
    percs = db.run("match (n:Movie) WHERE toInteger(n.released)>= toInteger({from}) and toInteger(n.released) < toInteger({to}) with count(n) as total match (l:Movie) WHERE toInteger(l.released) >= toInteger({from}) and toInteger(l.released) < toInteger({to}) return l.origin as origin, tofloat(100.00*count(l)/total) as perc order by perc desc",{'from':year_from,'to':year_to})
    for perc in percs:
        data.append([perc["origin"],perc["perc"]])
    return Response(dumps(data), mimetype="application/json")

@app.route("/plot_analys")
def get_plot_analys_page():
    dirs=[]
    db = get_db()
    tmp = db.run("match (p:Person)-[:DIRECTED]-(n:Movie) where p.name <> 'Unknown' return  p.name as name,count(n) as count order by count desc limit 50")
    for dir in tmp:
        dirs.append(dir['name'])
    genres=[]
    tmp = db.run("match(n:Movie) where n.genre <> 'unknown' and not n.genre contains ',' and not trim(n.genre) contains '/' return trim(n.genre) as genre, count(trim(n.genre)) as counts order by counts desc limit 20")
    for genre in tmp:
        genres.append(genre['genre'])
    return render_template("plot_analys.html", dirs=dirs,genres=genres)

def get_stop_words():
    return ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re","s", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

@app.route("/get_table_plot_dir")
def get_table_plot_dir():
    dir = request.args["dir"]
    stop_words = get_stop_words()
    db = get_db()
    data, words_with_count=[],[]
    texts = db.run("match (n:Movie)-[:DIRECTED]-(p:Person) where p.name = {dir} return split(toLower(n.plot),' ') as plot",{'dir':dir})
    for text in texts:
        tokens = [token for token in text['plot'] if token.replace('.','').replace(',','').replace('\"','').replace('\'',' ').replace(':','').replace(';','') not in stop_words and token != ' ']
        for token in tokens:
            data.append(token.replace('.','').replace(',','').replace('\"','').replace('\'',' ').replace(':','').replace(';',''))
    words = db.run('with {data} as words unwind (words) as word return word as word,count(word) as count order by count desc limit 25',{'data':data})
    for word in words:
        words_with_count.append([word["word"],word["count"]])
    return Response(dumps(words_with_count), mimetype="application/json")

@app.route("/get_table_plot_genre")
def get_table_plot_genre():
    genre = request.args["genre"]
    stop_words = get_stop_words()
    db = get_db()
    data, words_with_count=[],[]
    texts = db.run("match (n:Movie) where n.genre contains {genre} return split(toLower(n.plot),' ') as plot",{'genre':genre})
    for text in texts:
        tokens = [token for token in text['plot'] if token.replace('.','').replace(',','').replace('\"','').replace('\'',' ').replace(':','').replace(';','') not in stop_words and token != ' ']
        for token in tokens:
            data.append(token.replace('.','').replace(',','').replace('\"','').replace('\'',' ').replace(':','').replace(';',''))
    words = db.run('with {data} as words unwind (words) as word return word as word,count(word) as count order by count desc limit 25',{'data':data})
    for word in words:
        words_with_count.append([word["word"],word["count"]])
    return Response(dumps(words_with_count), mimetype="application/json")

@app.route("/get_table_universal_words")
def get_table_universal_words():
    stop_words = get_stop_words()
    db = get_db()
    data, words_with_count=[],[]
    texts = db.run("match (n:Movie) return split(toLower(n.plot),' ') as plot")
    for text in texts:
        tokens = [token for token in text['plot'] if token.replace('.','').replace(',','').replace('\"','').replace('\'',' ').replace(':','').replace(';','') not in stop_words and token != ' ']
        for token in tokens:
            data.append(token.replace('.','').replace(',','').replace('\"','').replace('\'',' ').replace(':','').replace(';',''))
    words = db.run('with {data} as words unwind (words) as word return word as word,count(word) as count order by count desc limit 25',{'data':data})
    for word in words:
        words_with_count.append([word["word"],word["count"]])
    return Response(dumps(words_with_count), mimetype="application/json")

solo_comps_act = []
@app.route("/count_components_act")
def count_components_act():
    db = get_db()
    solo_comps_act.clear()
    comps = db.run("call algo.unionFind.stream(null,'ACTED_IN',{}) yield nodeId, setId return distinct setId, collect(algo.getNodeById(nodeId).title) as fragId order by setId, fragId")
    for comp in comps:
        if len(comp['fragId'])>0:
            solo_comps_act.append([comp['setId'],comp['fragId']])
    return Response(dumps(len(solo_comps_act)), mimetype="application/json")

@app.route("/components_show_act")
def components_show_act():
    comp_id = int(request.args["comp_id"])
    db = get_db()
    results = db.run("MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) WHERE a.name<>'Unknown' and m.title in {comps}"
             "RETURN m.title as movie, m.wiki as wiki, collect(a.name) as cast ", {'comps':solo_comps_act[comp_id][1]})
    nodes,rels = for_graph(results,'actor')
    return Response(dumps({"nodes": nodes, "links": rels}), mimetype="application/json")

solo_comps_dir = []
@app.route("/count_components_dir")
def count_components_dir():
    db = get_db()
    solo_comps_dir.clear()
    comps = db.run("call algo.unionFind.stream(null,'DIRECTED',{}) yield nodeId, setId return distinct setId, collect(algo.getNodeById(nodeId).title) as fragId order by setId, fragId")
    for comp in comps:
        if len(comp['fragId'])>0:
            solo_comps_dir.append([comp['setId'],comp['fragId']])
    return Response(dumps(len(solo_comps_dir)), mimetype="application/json")

@app.route("/components_show_dir")
def components_show_dir():
    comp_id = int(request.args["comp_id"])
    db = get_db()
    results = db.run("MATCH (m:Movie)<-[:DIRECTED]-(a:Person) WHERE a.name<>'Unknown' and m.title in {comps}"
             "RETURN m.title as movie, m.wiki as wiki, collect(a.name) as cast ", {'comps':solo_comps_dir[comp_id][1]})
    nodes,rels = for_graph(results,'director')
    return Response(dumps({"nodes": nodes, "links": rels}), mimetype="application/json")

def for_graph(results,label):
    nodes = []
    rels = []
    i = 0
    for record in results:
        nodes.append({"title": record["movie"], "label": "movie","wiki":record["wiki"]})
        target = i
        i += 1
        for name in record['cast']:
            person = {"title": name, "label": label}
            try:
                source = nodes.index(person)
            except ValueError:
                nodes.append(person)
                source = i
                i += 1
            rels.append({"source": source, "target": target})
    return [nodes,rels]

@app.route("/specific_actor_graph")
def specific_actor_graph():
    name = request.args["actor"]
    db = get_db()
    results = db.run("MATCH (m:Movie)-[:ACTED_IN]-(a:Person) WHERE a.name={name}"
             "RETURN m.title as movie, m.wiki as wiki, collect(a.name) as cast ", {'name':name})
    nodes,rels = for_graph(results,'actor')
    return Response(dumps({"nodes": nodes, "links": rels}), mimetype="application/json")

@app.route("/specific_director_graph")
def specific_director_graph():
    name = request.args["director"]
    db = get_db()
    results = db.run("MATCH (m:Movie)-[:DIRECTED]-(a:Person) WHERE a.name={name}"
             "RETURN m.title as movie, m.wiki as wiki, collect(a.name) as cast ", {'name':name})
    nodes,rels = for_graph(results,'director')
    return Response(dumps({"nodes": nodes, "links": rels}), mimetype="application/json")