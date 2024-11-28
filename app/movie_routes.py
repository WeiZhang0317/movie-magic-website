# As a customer, I want to search for movies on the website, so that I can find a movie I am interested in.

# Criteria:

# A search bar is prominently located at the top of the page.
# Users can search based on movie titles (allowing for partial text matches).
# Search results display movie posters and names.
# Clicking on a poster reviews details such as name, rating, session times (for today and the next 7 days), price, and a brief introduction.


# As a customer, I want to see the current and upcoming movie information on the website so that I can decide whether to watch a movie or not. I also want to know the brief of this theatre.

# Criteria:

# Presents 3 carousel images at the top of the homepage. They are the most popular recent movies.
# Movie list with movie posters, this list should include two sections- current movies and upcoming movies. 
# There is a tab to switch between current and upcoming movies.
# Posters need to be consistent in size and design 
# Each poster includes essential movie details like title, screening times, and cinema.
# A separate section called “About Us”, with the brief of this theatre, including the established year, each cinema’s name, and capacity.

from flask import Blueprint, render_template,request, session,jsonify
from datetime import date
import mysql.connector
import connect
from decimal import Decimal
from app.main_routes import getCursor


movie_blueprint = Blueprint('movie', __name__)


@movie_blueprint.route('/movie/<int:movie_id>')
def movies(movie_id):
    cursor = getCursor(dictionary_cursor=True)
    query = """
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
            a.Name as ActorName,
            MovieReview.ReviewScore as Score
        FROM 
            Movie m
        LEFT JOIN Genre g ON m.Genre = g.ID
        LEFT JOIN Rating r ON m.Rating = r.ID
        LEFT JOIN Actor a ON m.Actor = a.ID
        LEFT JOIN MovieReview ON m.MovieReview= MovieReview.ID
        WHERE
            m.ID =  %s;
    """
    cursor.execute(query, (movie_id,))
    movie_details = cursor.fetchone()
    
       # Check if user is logged in
    is_logged_in = 'loggedin' in session and session['loggedin']

    if movie_details and movie_details['ReleaseDate']:
        # Keep the original date for comparison
        original_date = movie_details['ReleaseDate']

        # Create a new key for the formatted date
        formatted_date = original_date.strftime('%d-%m-%Y')
        movie_details['FormattedReleaseDate'] = formatted_date

         # Include the original_date in the template context
        return render_template('movies.html', movie=movie_details, original_date=original_date, feb_end_date=date(2024, 2, 29),  is_logged_in=is_logged_in)

    # If ReleaseDate is not in movie_details, pass None for original_date
    return render_template('movies.html', movie=movie_details, original_date=None, feb_end_date=date(2024, 2, 29))


@movie_blueprint.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = request.json
    movie_id = data['movie_id']
    user_rating = float(data['user_rating'])

    cursor = getCursor(dictionary_cursor=True)

    # Retrieve the current average score and the number of ratings
    cursor.execute("SELECT ReviewScore, NumberOfRatings FROM MovieReview WHERE ID = %s", (movie_id,))
    review = cursor.fetchone()
    current_score = float(review['ReviewScore'])  # Convert Decimal to float
    number_of_ratings = review['NumberOfRatings']

    # Calculate the new average score
    new_average = ((current_score * number_of_ratings) + user_rating) / (number_of_ratings + 1)
    
    # Update the number of ratings
    number_of_ratings += 1

    # Make sure to convert the new_average to Decimal before updating the database
    new_average_decimal = Decimal(new_average)

    # Update the new average score in the database
    cursor.execute("UPDATE MovieReview SET ReviewScore = %s, NumberOfRatings = %s WHERE ID = %s", (new_average_decimal, number_of_ratings, movie_id))
    cursor.close()
    
    return jsonify(success=True, new_average=new_average)
