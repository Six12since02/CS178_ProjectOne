from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flashk

app = Flask(__name__)

@app.route ('/')
def hello():
    return '<h2>Hello from Flask!</h2>'

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


@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT movie_id, title, release_date, revenue, runtime
                         FROM movie
                         LIMIT 500""")
    return display_html(rows)

@app.route("/pricequery/<price>")
def viewprices(price):
    rows = execute_query("""select ArtistId, Artist.Name, Track.Name, UnitPrice, Milliseconds
            from Artist JOIN Album using (ArtistID) JOIN Track using (AlbumID)
            where UnitPrice = %s order by Track.Name 
            Limit 500""", (str(price)))
    return display_html(rows) 

@app.route("/timequery/<time>")
def viewtime(time):
    rows = execute_query("""select ArtistId, Artist.Name, Track.Name, UnitPrice, Milliseconds
            from Artist JOIN Album using (ArtistID) JOIN Track using (AlbumID)
            where Milliseconds > %s order by Track.Name 
            Limit 500""", (str(time)))
    return display_html(rows) 

from flask import request

@app.route("/pricequerytextbox", methods = ['GET'])
def price_form():
  return render_template('textbox.html', fieldname = "Price")

@app.route("/pricequerytextbox", methods = ['POST'])
def price_form_post():
  text = request.form['text']
  return viewprices(text)

@app.route("/timequerytextbox", methods = ['GET'])
def time_form():
  return render_template('textbox.html', fieldname = "Time")

@app.route("/timequerytextbox", methods = ['POST'])
def time_form_post():
  text = request.form['text']
  return viewtime(text)

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
