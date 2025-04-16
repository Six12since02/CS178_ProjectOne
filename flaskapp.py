from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


@app.route ('/about')
def about():
    return '<h2>An about page!</h2>'

"""
from flask import render_template

@app.route("/hello/<username>/")
def hello_user(username):
    return render_template('layout.html', name=username)

@app.route('/repeat/<var>')
def repeater(var):
    result= ""
    for i in range(10):
        result += var
    return result

@app.route("/numchar/<var>")
def numchar(var):
    count = len(var)
    return str(count)

@app.route("/numvowels/<var>")
def numvowels(var):
    count = 0
    for i in var.lower():
        if i in ['a','e','i','o','u']:
            count += 1
    return str(count)
"""
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

#display the results from the genres query
def genres_html(rows, genre):
    html = ""
    html += '<p><a href="/">Back to Home</a></p>'
    html += f"<h2>{genre} Movies</h2>"
    html += "<table>"

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td></tr>"
    html += "</table></body>"
    return html


@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT movie_id, title, release_date, revenue, runtime
                         FROM movie
                         LIMIT 500""")
    return display_html(rows)

#### Start ChatGPT code ####
# ChatGPT code to chose genre

# I added all genres from the database into this list
genre_list = [ "Adventure", "Fantasy", "Animation", "Drama", "Horror", "Action", "Comedy", "History", "Western", "Thriller", "Crime", "Documentary", "Science Fiction", "Mystery", "Music", "Romance", "Family", "War", "Foreign", "TV Movie" ]

@app.route('/genrequery')
def index():
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
    return genres_html(rows, genre) 

@app.route("/pricequerytextbox", methods = ['GET'])
def price_form():
  return render_template('textbox.html', fieldname = "Price")

@app.route("/timequerytextbox", methods = ['GET'])
def time_form():
  return render_template('textbox.html', fieldname = "Time")

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
