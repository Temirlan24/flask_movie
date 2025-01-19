import sqlite3
from flask import *
import requests

url = "https://movie-info-api.p.rapidapi.com/movie-info"

headers = {
	"x-rapidapi-key": "a345e934b7msh773fb9ca77ce585p1a80b1jsn17b8c2334434",
	"x-rapidapi-host": "movie-info-api.p.rapidapi.com"
}

app = Flask(__name__)

def init_db():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS favourites 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, year TEXT, description TEXT, poster TEXT, rating INTEGER)''')
    connection.commit()
    connection.close()

@app.route('/', methods=['GET','POST'])
def index():
    init_db()
    return render_template('index.html')

@app.route('/movies', methods=['GET', 'POST'])
def submit():
    movie = request.form.get('movie')
    querystring = {"title": movie, "lang": "en-US", "max_results": "10"}
    response = requests.get(url, headers=headers, params=querystring)
    movies = response.json()
    return render_template('index.html', movies=movies)

@app.route('/movie/<title>', methods=['GET', 'POST'])
def get_movie_by_id(title):
    querystring = {"title": title, "lang": "en-US", "max_results": "1"}
    print(title)
    response = requests.get(url, headers=headers, params=querystring)
    movie_by_title = response.json()
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM favourites WHERE title=?", (movie_by_title[0]['title'], ))
    result = cursor.fetchone()
    is_favourite = True if result else False
    connection.close()

    return render_template('movie.html', movie_by_title=movie_by_title[0], is_favourite=is_favourite)


@app.route('/favourites', methods=['POST'])
def add_to_favourites():
    data = request.json
    print(data)
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute('''INSERT INTO favourites (title, year, description, poster, rating)
                      VALUES (?, ?, ?, ?, ?)''',
                   (data['title'], data['year'], data['description'], data['poster'], data['rating']))
    connection.commit()
    connection.close()

    return jsonify({"message": "Movie added to favourites!"}), 201

@app.route('/favourites', methods=['GET'])
def favourites():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM favourites")
    favourite_movies = cursor.fetchall()
    print(favourite_movies)
    connection.close()

    return render_template('favourites.html', favourites=favourite_movies)


@app.route('/remove_favourite', methods=['POST'])
def remove_favourite():
    data = request.json
    print('remove', data)
    movie_title = data.get('title')

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM favourites WHERE title = ?", (movie_title,))
    connection.commit()
    connection.close()

    return jsonify({"message": f"Фильм '{movie_title}' был удаен из избранного"}), 200


@app.route('/clear_favourites', methods=['POST'])
def clear_favourites():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM favourites")
    connection.commit()
    connection.close()

    return redirect(url_for('favourites'))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)