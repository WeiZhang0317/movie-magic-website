#Routing of main functions (homepage, about us, etc.)

from flask import Blueprint, render_template,request, session
from datetime import date
import mysql.connector
import connect


main_blueprint = Blueprint('main', __name__)

connection = None  # Global variable to store the connection

def getCursor(dictionary_cursor=False):
    global connection

    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(
            user=connect.dbuser,
            password=connect.dbpass,
            host=connect.dbhost,
            database=connect.dbname,
            autocommit=True)
        
    cursor = connection.cursor(dictionary=dictionary_cursor)
    return cursor

    #connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, database=connect.dbname, autocommit=True)
    #cursor = connection.cursor(dictionary=dictionary_cursor)
    #return cursor



@main_blueprint.route('/', methods=['GET', 'POST'])
def home():
    cursor = getCursor(dictionary_cursor=True)
    #get all information from movie/actor/rating/genre tables
    query1= """
    SELECT 
        m.ID, 
        m.Title, 
        m.Language, 
        m.Description, 
        m.ReleaseDate, 
        m.Image, 
        m.Bigposter, 
        g.Name as GenreName, 
        r.Rating as MovieRating,
        a.Name as ActorName
    FROM 
        Movie m
    LEFT JOIN Genre g ON m.Genre = g.ID
    LEFT JOIN Rating r ON m.Rating = r.ID
    LEFT JOIN Actor a ON m.Actor = a.ID
    """
    #bigposter for main page
    query2 =  query1 +"""
    WHERE 
        m.Bigposter IS NOT NULL;
    """
    # current movie 
    query3 =  query1 + """ WHERE
    m.ReleaseDate <= '2024-02-29'
    """
     # upcoming movie 
    query4 =  query1 + """ WHERE
    m.ReleaseDate > '2024-02-29'
    """
    cursor.execute(query2)
    bigposters = cursor.fetchall()
    cursor.execute(query3)
    currentmovies= cursor.fetchall()
    cursor.execute(query4)
    upcomingmovies= cursor.fetchall()
    # Check if user is logged in
    is_logged_in = 'loggedin' in session and session['loggedin']

    return render_template('home.html', bigposters=bigposters, currentmovies=currentmovies,upcomingmovies=upcomingmovies, is_logged_in=is_logged_in)

@main_blueprint.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('searchQuery') 
    print("Search Query:", search_query)
    cursor = getCursor(dictionary_cursor=True)
    

    search_sql = """
    SELECT 
        m.ID, 
        m.Title, 
        m.Language, 
        m.Description, 
        m.ReleaseDate, 
        m.Image, 
        m.Bigposter, 
        g.Name as GenreName, 
        r.Rating as MovieRating,
        a.Name as ActorName
    FROM 
        Movie m
    LEFT JOIN Genre g ON m.Genre = g.ID
    LEFT JOIN Rating r ON m.Rating = r.ID
    LEFT JOIN Actor a ON m.Actor = a.ID
    WHERE 
        m.Title LIKE %s OR 
        a.Name LIKE %s OR 
        g.Name LIKE %s
    """


    cursor.execute(search_sql, ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    search_results = cursor.fetchall()
    

    cursor.close()
    connection.close()
   
    
    return render_template('search_results.html', search_results=search_results, search_query=search_query or "No query provided",  feb_end_date=date(2024, 2, 29))



@main_blueprint.route('/cinema')
def cinema():
    cursor = getCursor(dictionary_cursor=True)
    cinema_sql="""SELECT * FROM Cinema;"""
    cursor.execute(cinema_sql)
    cinema= cursor.fetchall()
    return render_template('cinema.html', cinema=cinema)


@main_blueprint.route('/fooddrinks')
def fooddrinks():
    cursor = getCursor(dictionary_cursor=True)
    fooddrinks_sql="""SELECT * FROM FoodCombo;"""
    cursor.execute(fooddrinks_sql)
    foodcombos= cursor.fetchall()
    return render_template('food_and_drinks.html',foodcombos =foodcombos)
