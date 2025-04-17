from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

from dbCode import *

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = "Reviews"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

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

@app.route("/add_review", methods=["GET", "POST"])
def add_review_redirect():
    if request.method == "GET":
        return render_template("ask_username.html")
    
    elif request.method == "POST":
        username = request.form.get("username")
        if username:
            return redirect(url_for("add_review", username=username))
        else:
            return render_template("review_error.html", error="Username is required")

@app.route("/add_review/<username>", methods=["GET", "POST"])
def add_review(username):
    try:
        # Check if the user exists in DynamoDB
        response = table.get_item(Key={"username": username})

        if "Item" not in response:
            return render_template("review_error.html", error="User not found")

        if request.method == "GET":
            return render_template("add_review.html", username=username)

        elif request.method == "POST":
            title = request.form.get("title")
            rating = request.form.get("rating")
            review_text = request.form.get("review_text")
            spoiler = request.form.get("spoiler") == "yes"

            if not all([title, rating, review_text]):
                return render_template("review_error.html", error="Missing fields")

            # Check if movie exists in SQL
            result = execute_query("SELECT 1 FROM movie WHERE title = %s", (title,))
            if not result:
                return render_template("review_error.html", error="Movie not found")

            # Construct new review
            new_review = {
                "M": {
                    "title": {"S": title},
                    "rating": {"N": str(rating)},
                    "review_text": {"S": review_text},
                    "spoiler": {"BOOL": spoiler}
                }
            }

            # Append to user's reviews
            table.update_item(
                Key={"username": username},
                UpdateExpression="SET reviews = list_append(if_not_exists(reviews, :empty), :r)",
                ExpressionAttributeValues={
                ":r": [new_review],
                ":empty": []
                },
    ReturnValues="UPDATED_NEW"
)
            return render_template("review_success.html", username=username, title=title)

    except ClientError as e:
        return render_template("review_error.html", error=e.response["Error"]["Message"])
    except Exception as e:
        return render_template("review_error.html", error=str(e))

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
