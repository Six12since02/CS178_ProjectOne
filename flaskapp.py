from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

import pymysql
import creds

def get_conn():
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.password,
        db=creds.db,
        )
    return conn

def execute_query(query, args=()):
    cur = get_conn().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows


#display the sqlite query in a html table
def display_html(rows):
    html = ""
    html += """<table><tr><th>MovieID</th><th>Title</th><th>Release Date</th><th>Revenue</th><th>Run Time</th></tr>"""

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td><td>" + str(r[1]) + "</td><td>" + str(r[2]) + "</td><td>" + str(r[3]) + "</td><td>" + str(r[4]) + "</td></tr>"
    html += "</table></body>"
    return html

#display the results for a query
def query_html(rows, query):
    html = ""
    html += '<p><a href="/">Back to Home</a></p>'
    html += f"<h2>{query} Movies</h2>"
    html += "<table>"

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td></tr>"
    html += "</table></body>"
    return html

#display runtime query results
def runtime_html(rows, time):
    html = ""
    html += '<p><a href="/">Back to Home</a></p>'
    html += f"<h2>Movies shorter than {time} minuntes:</h2>"
    html += "<table>"

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td></tr>"
    html += "</table></body>"
    return html


@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT movie_id, title, release_date, revenue, runtime
                         FROM movie
                         """)
    return display_html(rows)

#I added all genres from the database into this list
from genres import genre_list

#### Start ChatGPT code ####
# ChatGPT code to chose genre

@app.route('/genrequery')
def genre_index():
    return render_template('select_genre.html', genres=genre_list)

@app.route('/redirect_genre', methods=['POST'])
def redirect_genre():
    selected_genre = request.form['genre']
    return redirect(url_for('genrequery', genre=selected_genre))

#### End ChatGPT code ####

@app.route("/genrequery/<genre>")
def genrequery(genre):
    rows = execute_query("""SELECT title
            FROM genre JOIN movie_genres USING (genre_id) JOIN movie USING (movie_id)
            WHERE genre_name = %s 
            ORDER BY title""", (str(genre)))
    return query_html(rows, genre) 

# List of languages stored in this python file
from languages import language_list

@app.route('/languagequery')
def language_index():
    return render_template('select_language.html', languages=language_list)

@app.route('/redirect_language', methods=['POST'])
def redirect_language():
    selected_language = request.form['language']
    return redirect(url_for('languagequery', language=selected_language))

@app.route("/languagequery/<language>")
def languagequery(language):
    rows = execute_query("""SELECT title
            FROM language JOIN movie_languages USING (language_id) JOIN movie USING (movie_id)
            WHERE language_name = %s 
            ORDER BY title""", (str(language)))
    return query_html(rows, language) 
    
@app.route('/runtimequery')
def runtime_index():
    return render_template('runtime_query.html')

@app.route("/redirect_runtime", methods=['POST'])
def redirect_runtime():
    time = request.form['time']
    return redirect(url_for('runtimequery', time=time))

@app.route("/runtimequery/<time>")
def runtimequery(time):
    rows = execute_query("""SELECT title
            FROM movie 
            WHERE runtime < %s 
            ORDER BY title""", (str(time)))
    return runtime_html(rows, time) 

@app.route("/pricequerytextbox", methods = ['GET'])
def price_form():
  return render_template('textbox.html', fieldname = "Price")

@app.route("/timequerytextbox", methods = ['GET'])
def time_form():
  return render_template('textbox.html', fieldname = "Time")

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
