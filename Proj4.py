import requests
import json
import secrets
import time
import sqlite3
import csv
import sys
import plotly.plotly as py
import plotly.graph_objs as go

class movie_by_key_word:
    def __init__(self, movie_id,title,release_date, popularity_score, vote_average, vote_count):
        self.movie_id = movie_id
        self.title = title
        self.release_date = release_date
        self.popularity_score = popularity_score
        self.vote_average = vote_average
        self.vote_count = vote_count

CACHE_FNAME = 'movie_cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def make_request_using_cache_tmbd_keyword(movie_keyword):
    movie_keyword = str(movie_keyword)
    tmdb_baseurl = 'https://api.themoviedb.org/3/search/movie'
    unique_ident = tmdb_baseurl + "/" + movie_keyword
    if unique_ident in CACHE_DICTION:
        print("Getting Movie DB cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new Movie DB data...")
        new_resp = {}
        for i in [1,2,3,4,5,6]:
            params = {"api_key":secrets.movie_db_api_key, "query":movie_keyword, "page":i}
            resp = requests.get(tmdb_baseurl, params = params)
            new_resp[i]=resp.text
        CACHE_DICTION[unique_ident] = new_resp
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


def get_results_for_movie(key_word):
    movie_items = []
    movie_list = []
    list_of_ids = []
    movie_data = make_request_using_cache_tmbd_keyword(key_word)
    for key, value in movie_data.items():
        data = json.loads(value)
        for x in data['results']:
            movie_id = x.get("id")
            list_of_ids.append(movie_id)
            title = x.get("title")
            release_date= x.get("release_date")[:4]
            popularity_score = x.get("popularity")
            vote_average = x.get("vote_average")
            vote_count = x.get("vote_count")
            movie_list.append([movie_id,title,release_date, popularity_score, vote_average, vote_count])
            movie_items.append(movie_by_key_word(movie_id,title,release_date, popularity_score, vote_average, vote_count))
    return (movie_items, movie_list, list_of_ids)

MOVIE_SPECIFIC_CACHE_FNAME = 'diff_cache.json'
try:
    cache_file = open(MOVIE_SPECIFIC_CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DIC = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DIC= {}


def make_request_using_cache_tmbd_id(movie_id):
    tmdb_baseurl = 'https://api.themoviedb.org/3/movie'
    unique_ident = tmdb_baseurl + "/" + str(movie_id)
    if unique_ident in CACHE_DIC:
        print("Getting Movie Specific cached data...")
        return CACHE_DIC[unique_ident]

    else:
        print("Making a request for new Specific Movie data...")
        params = {"api_key":secrets.movie_db_api_key}
        resp = requests.get(unique_ident, params = params)
        CACHE_DIC[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DIC)
        fw = open(MOVIE_SPECIFIC_CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DIC[unique_ident]


def get_info_for_movie(key_word):
    movie_data = get_results_for_movie(key_word)
    movie_items,list_of_movies,list_of_ids = movie_data
    specifics_movie_list = []
    for movie_id in list_of_ids:
        dic = {}
        movie_data = make_request_using_cache_tmbd_id(movie_id)
        new_movie_data =json.loads(movie_data)
        # for key, value in new_movie_data.items():
        movie_id = movie_id
        genres = new_movie_data.get("genres")
        if len(genres) == 3:
            genre_1 = genres[0]["name"]
            genre_2 = genres[1]["name"]
            genre_3 = genres[2]["name"]
        elif len(genres) == 2:
            genre_1 = genres[0]["name"]
            genre_2 = genres[1]["name"]
            genre_3 = None
        elif len(genres) == 1:
            genre_1 = genres[0]["name"]
            genre_2 = None
            genre_3 = None
        else:
            genre_1 = None
            genre_2 = None
            genre_3 = None
        overview = new_movie_data.get("overview")
        budget = new_movie_data.get("budget")
        revenue = new_movie_data.get("revenue")
        runtime = new_movie_data.get("runtime")
        tagline = new_movie_data.get("tagline")
        # print(str(counter) + "." + str(runtime))
        # counter += 1
        specifics_movie_list.append([movie_id,overview, tagline,genre_1, genre_2, genre_3, revenue, budget, runtime])
        time.sleep(.3)
    return specifics_movie_list
#
def create_csv_file_movie_keyword(key_word):
    movie_tuple = get_results_for_movie(key_word)
    movie_items,list_of_movies,list_of_ids = movie_tuple
    with open('movie_info.csv','w', newline = "") as f:
        a = csv.writer(f, delimiter = ",")
        a.writerows(list_of_movies)

def create_csv_file_movie_id(key_word):
    list_of_movies = get_info_for_movie(key_word)
    with open('movie_specific_info.csv','w', newline = "") as f:
        a = csv.writer(f, delimiter = ",")
        a.writerows(list_of_movies)

DBNAME = 'movies.db'
MOVIECSV = 'movie_info.csv'
INFOMOVIECSV = 'movie_specific_info.cvs'

def init_data():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)

    statement = '''
        DROP TABLE IF EXISTS 'List_of_Movies';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Movie_Info';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'List_of_Movies' (
            'Id' INTEGER PRIMARY KEY,
            'Title' TEXT,
            'Release_date' INTEGER,
            'Popularity_score' INTEGER,
            'Vote_average' INTEGER

        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Movie_Info' (
                'Movie_Id' INTEGER,
                'Overview' TEXT,
                'Tagline' TEXT,
                'Genre_1' TEXT,
                'Genre_2' TEXT,
                'Genre_3' TEXT,
                'Revenue' INTEGER,
                'Budget' INTEGER,
                'Runtime'INTEGER

        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()

def add_list_of_movies():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    csvlistmovies = open(MOVIECSV, "r")
    csvnewlistmovies = csv.reader(csvlistmovies)
    for movie in csvnewlistmovies:
        insertion = (movie[0],movie[1],movie[2],movie[3],movie[4])
        statement = 'INSERT INTO "List_of_Movies" '
        statement += 'VALUES (?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)
        conn.commit()
    conn.close()
    csvlistmovies.close()


def add_movies_specifics():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    csvlistmovies = open("movie_specific_info.csv", "r")
    csvnewlistmovies = csv.reader(csvlistmovies)
    # q = cur.execute("SELECT Id FROM List_of_Movies").fetchall()
    for movie in csvnewlistmovies:
        insertion = (movie[0],movie[1],movie[2],movie[3],movie[4],movie[5],movie[6],movie[7], movie[8])
        statement = 'INSERT INTO "Movie_Info" '
        statement += 'VALUES (?, ?, ?, ?, ?, ? , ? , ? ,?)'
        cur.execute(statement, insertion)
        conn.commit()
    conn.close()
    csvlistmovies.close()

def popularity_score_by_genre(genre_1, genre_2):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    SELECT Popularity_score, Vote_average
    FROM List_of_Movies
    JOIN Movie_Info
    ON List_of_Movies.Id = Movie_Info.Movie_Id
    WHERE Genre_1 = "{}" and Genre_2 = "{}" or  Genre_1 = "{}" and Genre_2 = "{}" '''.format(genre_1, genre_2, genre_2, genre_1)
    cur.execute(statement)
    rows = cur.fetchall()
    x_items = []
    y_items = []
    for row in rows:
        x_items.append(row[0])
        y_items.append(row[1])

    trace1 = go.Scatter(
    x = x_items,
    y = y_items,
    mode = 'markers',
    marker = dict(
    color='blue',
    size=10))
    data = [trace1]
    layout = go.Layout(
        title= "Vote Average By Popularity Score for Genres {} and {}".format(genre_1,genre_2),
        xaxis = dict(
            range=[0, 25]
        ),
        yaxis = dict(
            range=[0, 25]
        ),
        height=300,
        width=900
    )

    fig = go.Figure(data = data, layout = layout)
    py.plot(fig, filename = 'basic-scatter')


def runtime_by_popularity_score():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    SELECT Popularity_score, Runtime
    FROM List_of_Movies
    JOIN Movie_Info
    ON List_of_Movies.Id = Movie_Info.Movie_Id
    WHERE Runtime > 0'''
    cur.execute(statement)
    rows = cur.fetchall()
    x_items = []
    y_items = []
    for row in rows:
        x_items.append(row[0])
        y_items.append(row[1])

    trace1 = go.Scatter(
    x = x_items,
    y = y_items,
    mode = 'markers',
    marker = dict(
    color='yellow',
    size=9))
    data = [trace1]
    layout = go.Layout(
        title = "Runtime by Popularity",
        xaxis = dict(
            range=[0, 25]
        ),
        yaxis = dict(
            range=[0, 250]
        ),
        height=600,
        width=900
    )

    fig = go.Figure(data = data, layout = layout)
    py.plot(fig, filename = 'basic-scatter')

def runtime_by_main_genre():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    SELECT Runtime, Genre_1
    FROM List_of_Movies
    JOIN Movie_Info
    ON List_of_Movies.Id = Movie_Info.Movie_Id
    GROUP BY Genre_1'''
    cur.execute(statement)
    rows = cur.fetchall()
    x_items = []
    y_items = []
    bar_colors = ["blue", "pink", "yellow", "green", "purple","navy", "orange", "violet", "red" , "gold", "brown", "maroon", "grey", "hot pink" ]
    for row in rows:
        x_items.append(row[0])
        y_items.append(row[1])

    trace1 = go.Bar(
    x = y_items,
    y = x_items,
    marker = dict(
    color= bar_colors,
    line = dict(
        width = 1.5,
    )))
    data = [trace1]
    layout = go.Layout(
        title = "Runtime by Main Genre",
        xaxis = dict(
            range=[0, 25]
        ),
        yaxis = dict(
            range=[0, 250]
        ),
        height=600,
        width=900
    )

    fig = go.Figure(data = data, layout = layout)
    py.plot(fig, filename = 'basic-bar')

def runtime_by_year():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    SELECT Release_date, Vote_average
    FROM List_of_Movies
    WHERE Vote_average > 0 GROUP BY Release_date '''
    cur.execute(statement)
    rows = cur.fetchall()
    x_items = []
    y_items = []
    for row in rows:
        x_items.append(row[0])
        y_items.append(row[1])

    trace1 = go.Scatter(
    x = x_items,
    y = y_items,
    mode = 'lines+markers',
    line = dict(
    color='red',
    width = 5))
    data = [trace1]
    layout = go.Layout(
        title = "Average Runtime by Year",
        xaxis = dict(title = "Release Year",
            range=[1920, 2020]
        ),
        yaxis = dict(title = "Vote Average",
            range=[0, 10]
        ),
        height=600,
        width=900
    )

    fig = go.Figure(data = data, layout = layout)
    py.plot(fig, filename = 'styled-line')

def process_command(command):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    split_command = command.split()
    list_genre = ["Action", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Family", "History", "Horror", "Music", "Romance", "Thriller"]
    if split_command[0].lower() == "genre":
        if split_command[1].lower() == "sort":
            # if len(split_command) < 4 or split_command[2] not in list_genre or split_command[3] not in list_genre:
            #     print("Command not recognized: {}".format(command))
            #     split_command = input('Enter a valid command with two valid genres: ')
            # else:
            popularity_score_by_genre(split_command[2], split_command[3])
        elif split_command[1].lower() == "runtime":
            runtime_by_main_genre()
        else:
            print("Command not recognized: {}".format(command))
            command = input('Enter a valid command with two valid arguments: ')
    elif split_command[0].lower == "runtime":
        # if len(split_command) < 2 or len(split_command) > 2:
        #     print("Command not recognized: {}".format(split_command))
        #     split_command = input('Enter a valid command with two arguments: ')
        if split_command[1].lower == "year":
            runtime_by_year()
        elif split_command[1].lower == "popularity":
            runtime_by_popularity_score()

def interactive_prompt():
    response = input('Enter a Single Keyword: ')
    while response != 'exit':
        if len(response.split()) < 1 or len(response.split()) > 1:
            print("Command not recognized: {}".format(response))
            response = input('Enter a Single Keyword: ')
            continue
        else:
            get_results_for_movie(response)
            get_info_for_movie(response)
            create_csv_file_movie_keyword(response)
            create_csv_file_movie_id(response)
            init_data()
            add_list_of_movies()
            add_movies_specifics()
            response = input('Enter a command: ')
            commands_allowed = ["genre", "runtime", "help"]
            while response != 'exit':
                if len(response.split()) < 2 or response.lower().split()[0] not in commands_allowed:
                    print("Command not recognized: {}".format(response))
                    response = input('Enter a valid command: ')
                    continue
                else:
                    given_command = process_command(response)
                # response = input('Enter a command: ')
            print("Bye")
if __name__=="__main__":
    interactive_prompt()
# get_results_for_movie("love")
# get_info_for_movie("love")
# create_csv_file_movie_keyword("love")
# create_csv_file_movie_id("love")
# init_data()
# add_list_of_movies()
# add_movies_specifics()
# popularity_score_by_genre("Comedy", "Romance")
# runtime_by_popularity_score()
# runtime_by_main_genre()
# runtime_by_year()
