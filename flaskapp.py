from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Displays the home page
@app.route('/')
def home():
    return render_template('home.html')

# Connect to the MySQL/RDS instance
from dbCode import *

# Connect to the DynamoDB database
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = "Reviews"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

# function to display all movies
def display_html(rows):
    html = ""
    html += '<p><a href="/">Back to Home</a></p>'
    html += """<table><tr><th>Title</th><th>Release Date</th><th>Revenue</th><th>Run Time</th><th>Budget</th><tr>"""

    for r in rows:
        html += "<tr><td style='text-align:center'>" + str(r[0]) + "</td><td>" + str(r[1]) + "</td><td>" + str(r[2]) + "</td><td>" + str(r[3]) + "</td><td>" + str(r[4]) + "</td></tr>"
    html += "</table></body>"
    return html

# function to display the results for a query
def query_html(rows, query):
    html = ""
    html += '<p><a href="/">Back to Home</a></p>'
    html += f"<h2>{query} Movies</h2>"
    html += "<table>"

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td></tr>"
    html += "</table></body>"
    return html

# funtion to display runtime query results
def runtime_html(rows, time):
    html = ""
    html += '<p><a href="/">Back to Home</a></p>'
    html += f"<h2>Movies shorter than {time} minuntes:</h2>"
    html += "<table>"

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td></tr>"
    html += "</table></body>"
    return html

# Displays a list of all movies and some attributes
@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT title, release_date, revenue, runtime, budget
                         FROM movie ORDER BY title""")
    return display_html(rows)

# List of genres stored in this python file
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

# Displays all movies of the chosen genre
@app.route("/genrequery/<genre>")
def genrequery(genre):
    rows = execute_query("""SELECT DISTINCT title
            FROM genre JOIN movie_genres USING (genre_id) JOIN movie USING (movie_id)
            WHERE genre_name = %s 
            ORDER BY title""", (str(genre)))
    return query_html(rows, genre) 

# List of languages stored in this python file
from languages import language_list

# Displays the language selection form
@app.route('/languagequery')
def language_index():
    return render_template('select_language.html', languages=language_list)

# Redirects to the results page
@app.route('/redirect_language', methods=['POST'])
def redirect_language():
    selected_language = request.form['language']
    return redirect(url_for('languagequery', language=selected_language))

# Displays all movies of the chosen language
@app.route("/languagequery/<language>")
def languagequery(language):
    rows = execute_query("""SELECT DISTINCT title
            FROM language JOIN movie_languages USING (language_id) JOIN movie USING (movie_id)
            WHERE language_name = %s 
            ORDER BY title""", (str(language)))
    return query_html(rows, language) 

# Displays the runtime selection page    
@app.route('/runtimequery')
def runtime_index():
    return render_template('runtime_query.html')

# Redirects to the results page
@app.route("/redirect_runtime", methods=['POST'])
def redirect_runtime():
    time = request.form['time']
    return redirect(url_for('runtimequery', time=time))

# Displays all movies shorter than the given runtime
@app.route("/runtimequery/<time>")
def runtimequery(time):
    rows = execute_query("""SELECT DISTINCT title
            FROM movie 
            WHERE runtime < %s 
            ORDER BY title""", (str(time)))
    return runtime_html(rows, time) 

# Imports all code for the reviews system
from reviewscode import *

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
