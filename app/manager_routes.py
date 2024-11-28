# As a theatre manager, I want a dashboard to manage various aspects of the theatre.

# Criteria:
# Secure login.
# View and manage my profile details
# View and manage staff profiles
# View and manage movie session times
# Assign movies to different sessions 
# View and manage promotions
# Manage ticket prices
# Generate the report

from flask import Blueprint, render_template,request, redirect, url_for, session, flash
import re
import bcrypt
from datetime import datetime, timedelta, date
import mysql.connector
from mysql.connector import FieldType
import connect
import hashlib
from werkzeug.utils import secure_filename
import os
from flask import current_app as app
import time
from app.main_routes import getCursor

manager_blueprint = Blueprint('manager', __name__)

#-----------------manager dashboard-------------------------------------

@manager_blueprint.route('/manager_dashboard')
def manager_dashboard():
    flash("Welcome to dashboard!", "info")
    return render_template('manager_dashboard.html')

#-----------------staff list view-------------------------------------
@manager_blueprint.route('/staff_list_view', methods=['GET'])
def staff_list_view():
    search_query = request.args.get('search', '')
    cursor = getCursor()
    
    # SQL query to get information from Staff
    sql_query = """
        SELECT *
        FROM Staff
        WHERE IsActive = 1 AND (FirstName LIKE %s OR LastName LIKE %s)
    """
    search_like = "%" + search_query + "%"
    cursor.execute(sql_query, (search_like, search_like))

    staff_list = cursor.fetchall()

    cursor.close()

    return render_template('staff_list_view.html', staff_list=staff_list, search_query=search_query)

#-----------------staff list edit-------------------------------------

@manager_blueprint.route('/staff_list_edit/<int:user_id>', methods=['GET', 'POST'])
def staff_list_edit(user_id):
    cursor = getCursor()

    # deal the form
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']

        # Check if email is unique
        email_query = """
            SELECT EXISTS (
                SELECT 1 FROM User 
                WHERE Email = %s AND ID != %s 
            )
        """
        cursor.execute(email_query, (email, user_id))
        if cursor.fetchone()[0]:
            flash('This email is already in use by another active user. Please enter a different email.', 'error')
            return redirect(url_for('manager.staff_list_edit', user_id=user_id))

        # Check if the mobile phone number is unique
        query = """
            SELECT EXISTS (
                SELECT 1 FROM (
                    SELECT Mobile FROM Customer WHERE IsActive = 1 AND Mobile = %s AND UserID != %s
                    UNION ALL
                    SELECT Mobile FROM Staff WHERE IsActive = 1 AND Mobile = %s AND UserID != %s
                    UNION ALL
                    SELECT Mobile FROM Admin WHERE IsActive = 1 AND Mobile = %s AND UserID != %s
                    UNION ALL
                    SELECT Mobile FROM Manager WHERE IsActive = 1 AND Mobile = %s AND UserID != %s
                ) AS combined 
            )
        """
        cursor.execute(query, (mobile, user_id, mobile, user_id, mobile, user_id, mobile, user_id))
        if cursor.fetchone()[0]:
            flash('Mobile number already in use! Please fill in another mobile phone number!', 'error')
            return redirect(url_for('manager.staff_list_edit', user_id=user_id))
        
        # update database if mobile phone is unique
        update_query = """
            UPDATE Staff 
            SET FirstName = %s, LastName = %s, Email = %s, Mobile = %s
            WHERE UserID = %s
        """
        cursor.execute(update_query, (first_name, last_name, email, mobile, user_id))
        
        flash('Staff details updated successfully!', 'success')
        
        return redirect(url_for('manager.staff_list_view'))

    # get the staff info
    cursor.execute("SELECT * FROM Staff WHERE UserID = %s", (user_id,))
    staff = cursor.fetchone()
    
    if staff:

        cursor.close()

        return render_template('staff_list_edit.html', staff=staff)
    else:
        flash('Staff not found!', 'error')
        return redirect(url_for('manager.staff_list_view'))
    
#-----------------staff delete-------------------------------------

@manager_blueprint.route('/staff_delete/<int:user_id>', methods=['GET'])
def staff_delete(user_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        # update staff table - IsActive
        update_staff = """
            UPDATE Staff 
            SET IsActive = %s
            WHERE UserID = %s
        """
        cursor.execute(update_staff, (False, user_id))

        # update user table - IsActive
        update_user = """
            UPDATE User
            SET IsActive = %s
            WHERE ID = %s
        """
        cursor.execute(update_user, (False, user_id))

        flash('Staff deleted successfully!', 'success')

        cursor.close()

        return redirect(url_for('manager.staff_list_view'))
    
#-----------------staff add-------------------------------------
    

@manager_blueprint.route('/staff_add', methods=['POST','GET'])
def staff_add():
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        if request.method == 'POST':
            cursor = getCursor()

            # get info from the form
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            mobile = request.form['mobile']
            password = request.form['password']
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # hash password

            #check if email is unique
            cursor.execute("SELECT COUNT(*) FROM User WHERE Email = %s", (email,))
            if cursor.fetchone()[0] > 0:
                flash("This email already exists! Please enter another email.", "error")
                return redirect(url_for('manager.staff_list_view'))
            
            # Check if the mobile phone number is unique
            query = """
                SELECT EXISTS (
                    SELECT 1 FROM (
                        SELECT Mobile FROM Customer WHERE IsActive = 1
                        UNION ALL
                        SELECT Mobile FROM Staff WHERE IsActive = 1
                        UNION ALL
                        SELECT Mobile FROM Admin WHERE IsActive = 1
                        UNION ALL
                        SELECT Mobile FROM Manager WHERE IsActive = 1
                    ) AS combined 
                    WHERE combined.Mobile = %s
                )
            """
            cursor.execute(query, (mobile,))
            if cursor.fetchone()[0]:
                flash('Mobile number already in use! Please enter another mobile phone number!', 'error')
                return redirect(url_for('manager.staff_list_view'))

            # INSERT into user table if mobile phone is unique
            cursor.execute("""
                INSERT INTO User (Email, Password, Role, IsActive)
                VALUES (%s, %s, 'Staff', 1)
            """, (email, hashed_password))
            user_id = cursor.lastrowid #get the last id

            # INSERT into staff table
            cursor.execute("""
                INSERT INTO Staff (UserID, FirstName, LastName, Email, Mobile, IsActive)
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (user_id, first_name, last_name, email, mobile))

            flash("Staff added successfully!", "success")

            cursor.close()

            return redirect(url_for('manager.staff_list_view'))
        
#-----------------movie list view-------------------------------------
        
@manager_blueprint.route('/movie_list_view', methods=['GET'])
def movie_list_view():
    search_query = request.args.get('search', '').strip()  
    cursor = getCursor()

    if 'loggedin' in session and session['role'] in ['Manager', 'Admin','Staff']:

        base_query = """
            SELECT 
                Movie.ID, 
                Movie.Title, 
                Movie.Language, 
                Movie.Description, 
                Movie.ReleaseDate, 
                Movie.Image, 
                Movie.Bigposter, 
                Genre.Name as GenreName,
                Rating.Rating as MovieRating,
                Actor.Name as ActorName,
                Movie.Duration 
            FROM Movie
            INNER JOIN Genre ON Movie.Genre = Genre.ID
            INNER JOIN Rating ON Movie.Rating = Rating.ID
            INNER JOIN Actor ON Movie.Actor = Actor.ID
        """

        if search_query:  # If there is a search query
            search_query = "%" + search_query + "%"  # Prepare the search query for a LIKE statement
            base_query += " WHERE Movie.Title LIKE %s"
            cursor.execute(base_query, (search_query,))  # Execute the query with search parameter
        else:
            cursor.execute(base_query) # Execute the base query without search

        movies = cursor.fetchall()

        # Get cinema list
        cursor.execute("SELECT ID, Name FROM Cinema")
        cinemas = cursor.fetchall()

        # Get genre list
        cursor.execute("SELECT ID, Name FROM Genre")
        genres = cursor.fetchall()

        # Get rating list
        cursor.execute("SELECT ID, Rating FROM Rating")
        ratings = cursor.fetchall() 

        cursor.close()

        return render_template('movie_list_view.html', movies = movies, cinemas=cinemas,
                               genres=genres,ratings=ratings, user_role=session.get('role'))
    
    
#-----------------movie list edit-------------------------------------

@manager_blueprint.route('/movie_list_edit/<int:movie_id>', methods=['GET', 'POST'])
def movie_list_edit(movie_id):
    cursor = getCursor()
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:

        if request.method == 'POST':
            # Process the form data and update the movie details
            title = request.form['title']
            language = request.form['language']
            description = request.form['description']
            release_date = request.form['release_date']
            genre_id = request.form['genre']
            rating_id = request.form['rating']
            actor_id = request.form['actor']
            duration = request.form['duration']
            movie_poster = request.files.get('image')
            carousel_poster = request.files.get('carousel_poster')
            update_fields = []

            # check if user want to delete Carousel Poster
            delete_carousel = 'delete_carousel' in request.form
            if delete_carousel:
                # get file name of Carousel Poster 
                cursor.execute("SELECT Bigposter FROM Movie WHERE ID = %s", (movie_id,))
                current_carousel_filename = cursor.fetchone()[0]

                if current_carousel_filename:
                    # delete file
                    current_carousel_filepath = os.path.join(app.root_path, 'static', 'img', current_carousel_filename)
                    if os.path.exists(current_carousel_filepath):
                        os.remove(current_carousel_filepath)

                    # update database，SET Bigposter AS NULL
                    update_fields.append(("Bigposter", None))

            # Handle the file upload for the movie poster

            if movie_poster and movie_poster.filename != '':
                # Ensure the filename is safe
                filename = secure_filename(movie_poster.filename)
                # Define the path to save the file
                save_path = os.path.join(app.root_path, 'static', 'img', filename)
                # Save the file
                movie_poster.save(save_path)
                update_fields.append(("Image", filename))

            #deal Carousel Poster img upload
            if carousel_poster and carousel_poster.filename != '':
                carousel_filename = secure_filename(carousel_poster.filename)
                save_path = os.path.join(app.root_path, 'static', 'img', carousel_filename)
                carousel_poster.save(save_path)
                update_fields.append(("Bigposter", carousel_filename))

            update_fields.extend([
                ("Title", title),
                ("Language", language),
                ("Description", description),
                ("ReleaseDate", release_date),
                ("Genre", genre_id),
                ("Rating", rating_id),
                ("Actor", actor_id),
                ("Duration", duration)
            ])

            # Generate the SQL statement based on the fields to be updated
            update_sql = "UPDATE Movie SET " + ", ".join([f"{field} = %s" for field, _ in update_fields]) + " WHERE ID = %s"
            
            if update_fields:
                cursor.execute(update_sql, [value for _, value in update_fields] + [movie_id])
                flash('Movie updated successfully!', 'success')
            else:
                flash('No changes made.', 'info')

            return redirect(url_for('manager.movie_list_view'))
        
        else:
            # Fetch the current details of the movie to pre-fill the form
            cursor.execute("""
                SELECT 
                    Movie.ID, Movie.Title, Movie.Language, Movie.Description, Movie.ReleaseDate, 
                    Movie.Genre, Movie.Rating, Movie.Actor, Movie.Duration, 
                    Actor.Name as ActorName,
                    Genre.Name as GenreName,
                    Rating.Rating as MovieRating
                FROM Movie
                INNER JOIN Actor ON Movie.Actor = Actor.ID
                INNER JOIN Genre ON Movie.Genre = Genre.ID
                INNER JOIN Rating ON Movie.Rating = Rating.ID
                WHERE Movie.ID = %s
            """, (movie_id,))
            movie = cursor.fetchone()
            
            # Fetch additional details for dropdowns
            cursor.execute("SELECT ID, Name FROM Genre")
            genres = cursor.fetchall()
            cursor.execute("SELECT ID, Rating FROM Rating")
            ratings = cursor.fetchall()
            cursor.execute("SELECT ID, Name FROM Actor")
            actors = cursor.fetchall()

            cursor.close()
            
            return render_template('movie_list_edit.html', movie=movie, genres=genres, ratings=ratings, actors=actors)
    else:
        return redirect(url_for('login'))

#-----------------movie schedule view-------------------------------------

@manager_blueprint.route('/manager_movie_schedule_view', methods=['GET'])
def manager_movie_schedule_view():
    search_query = request.args.get('search', '')  # Get the search query from the URL parameter
    cursor = getCursor()
    
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin','Staff']:
        cursor = getCursor()

        # Get cinema list
        cursor.execute("SELECT ID, Name FROM Cinema")
        cinemas = cursor.fetchall()

        # Get genre list
        cursor.execute("SELECT ID, Name FROM Genre")
        genres = cursor.fetchall()

        # Get rating list
        cursor.execute("SELECT ID, Rating FROM Rating")
        ratings = cursor.fetchall()  

        #get movie info from database
        sql_query = """
            SELECT 
                M.ID as MovieID,       
                M.Title, 
                C.Name as CinemaName,  
                S.Date, 
                S.DayOfWeek, 
                S.StartTime,
                M. Duration,
                S.ID as SessionID
            FROM 
                Session S
            JOIN 
                Movie M ON S.Movie = M.ID
            JOIN
                Cinema C ON S.Cinema = C.ID
            WHERE 
                M.Title LIKE %s     
        """
        search_like = "%" + search_query + "%"
        cursor.execute(sql_query, (search_like,))

        rows = cursor.fetchall()

        movie_schedule = {}
        for row in rows:
            movie_id = row[0]
            title = row[1]
            cinema_name = row[2]
            date = row[3]
            day_of_week = row[4]
            start_time = row[5]
            duration = row[6]
            session_id = row[7]

            if isinstance(start_time, timedelta):
                # total seconds
                total_seconds = start_time.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
            
                # format start time to HH:MM
                formatted_start_time = f"{hours:02}:{minutes:02}"
            else:
                # if it's not timedelta，don't need to deal with
                formatted_start_time = start_time

            if title not in movie_schedule:
                movie_schedule[title] = []

            movie_schedule[title].append((movie_id,title, cinema_name, date, day_of_week, formatted_start_time, duration, session_id))

        cursor.close()
    
        return render_template('movie_schedule_view.html', movie_schedule = movie_schedule,cinemas=cinemas,
                               genres=genres,ratings=ratings, user_role=session.get('role'))
    
#-----------------is session conflict function----------------------------

def is_conflict_existing(cursor, cinema_id, date_str, start_datetime, end_datetime, excluding_session_id=None):
    """
    Checks if there is a conflict in the session times.

    :param cursor: Database cursor
    :param cinema_id: Cinema ID
    :param date_str: Date of the session in 'YYYY-MM-DD' format
    :param start_datetime: Start datetime of the new session
    :param end_datetime: End datetime of the new session
    :param excluding_session_id: Session ID to exclude from conflict check (useful when editing)
    :return: True if conflict exists, False otherwise
    """
    conflict_query = """
        SELECT S.ID FROM Session S
        JOIN Movie M ON S.Movie = M.ID
        WHERE S.Cinema = %s AND S.Date = %s
        AND ((S.StartTime < %s AND ADDTIME(S.StartTime, SEC_TO_TIME(M.Duration * 60)) > %s)
        OR (S.StartTime < %s AND ADDTIME(S.StartTime, SEC_TO_TIME(M.Duration * 60)) > %s))
    """

    params = [cinema_id, date_str, end_datetime.strftime('%H:%M:%S'), start_datetime.strftime('%H:%M:%S'),
              start_datetime.strftime('%H:%M:%S'), end_datetime.strftime('%H:%M:%S')]

    # Exclude the session itself if we're editing
    if excluding_session_id:
        conflict_query += " AND S.ID <> %s"
        params.append(excluding_session_id)

    cursor.execute(conflict_query, params)
    return cursor.fetchone() is not None
    
#-----------------movie schedule edit-------------------------------------
    
@manager_blueprint.route('/manager_movie_schedule_edit/<int:session_id>', methods=['GET', 'POST'])
def manager_movie_schedule_edit(session_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        # get movie title
        cursor.execute("SELECT Movie FROM Session WHERE ID = %s", (session_id,))
        movie_tuple = cursor.fetchone()
        movie = movie_tuple[0]
        
        print(movie)

        if request.method == 'POST':
            #get info from the form
            cinema_id = request.form.get('cinema')
            date_str = request.form.get('date')
            start_time_str = request.form.get('startTime')
            date_object = datetime.strptime(date_str, '%Y-%m-%d')
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            start_datetime = datetime.combine(date_object, start_time)

            # get duration
            cursor.execute("SELECT Duration FROM Movie WHERE ID = %s", (movie,))
            duration_result = cursor.fetchone()
            duration = duration_result[0] if duration_result else 0  # if didn't find the duration，set duration as 0

            end_datetime = start_datetime + timedelta(minutes=duration)
            day_of_week = date_object.weekday()

            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_of_week_str = day_names[day_of_week]
        
            #print(day_of_week)

            # check conflict
            if is_conflict_existing(cursor, cinema_id, date_str, start_datetime, end_datetime, excluding_session_id=session_id):
                flash("There is already a movie showing in this cinema at this time. Please select other cinemas or re-enter another Start Time!")
                return redirect(url_for('manager.manager_movie_schedule_edit', session_id=session_id))

            #update database if no conflict
            update_query = """
            UPDATE Session
            SET Cinema = %s, Date = %s, DayOfWeek = %s, StartTime = %s
            WHERE ID = %s
            """
            cursor.execute(update_query, (cinema_id, date_str, day_of_week_str, start_time, session_id))
            flash('Movie schedule updated successfully!', 'success')
            return redirect(url_for('manager.manager_movie_schedule_view'))

        cursor.execute("SELECT * FROM Cinema")
        cinemas = cursor.fetchall()

        cursor.execute("SELECT * FROM Session WHERE ID = %s", (session_id,))
        current_schedule = cursor.fetchone()

        cursor.close()

        return render_template('movie_schedule_edit.html', cinemas=cinemas, 
                               current_schedule=current_schedule, 
                               session_id=session_id)

    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
#-----------------Add New Movie-------------------------------------

@manager_blueprint.route('/add_movie', methods=['GET','POST'])
def add_movie():
    # verify the role
    if 'loggedin' not in session or session['role'] not in ['Manager', 'Admin']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':

        cursor = getCursor()

        # deal the form info
        movie_name = request.form.get('movieName')
        language = request.form.get('language')
        description = request.form.get('description')
        release_date = request.form.get('releaseDate')
        genre_id = request.form.get('genre')
        
        duration_str = request.form.get('duration')
        if duration_str is not None:
            duration = int(duration_str)  # change to INT
        else:
            # if duration_str is None or can't be changed into int 
            flash("Please provide the duration (INT)!")
            return redirect(url_for('manager.add_movie'))
        
        cinema_id = request.form.get('cinema')
        date_str = request.form.get('date')
        start_time_str = request.form.get('startTime')
        rating_id = request.form.get('rating')
        actor_name = request.form.get('actor')

        date_object = datetime.strptime(date_str, '%Y-%m-%d')
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        start_datetime = datetime.combine(date_object, start_time)
        end_datetime = start_datetime + timedelta(minutes=duration)
        day_of_week = date_object.weekday()

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_of_week_str = day_names[day_of_week]

        # check for session conflicts
        if is_conflict_existing(cursor, cinema_id, date_str, start_datetime, end_datetime):
            flash('There is already a movie showing in this cinema at this time. Please select other cinemas or re-enter another Start Time!')
            return redirect(url_for('manager.add_movie'))

        cursor.execute("INSERT INTO Actor (Name) VALUES (%s)", (actor_name,))
        actor_id = cursor.lastrowid

        # Handle the file upload for the movie poster
        movie_poster = request.files.get('moviePoster')
        if movie_poster and movie_poster.filename != '':
            filename = secure_filename(movie_poster.filename)
            # Use app.root_path for a more robust file path handling
            save_path = os.path.join(app.root_path, 'static', 'img', filename)
            movie_poster.save(save_path)

            # Insert new movie into movie table
            cursor.execute("INSERT INTO Movie (Title, language, Description, ReleaseDate, Genre, Duration, Image,Rating,Actor) VALUES (%s, %s,%s, %s,%s, %s,%s,%s,%s)", 
                        (movie_name, language, description, release_date, genre_id, duration, filename, rating_id, actor_id))
        else:
            # Handle case when no image is provided or error occurs
            filename  = None  # or some default image path
            
        movie_id = cursor.lastrowid  # Get the ID of the last inserted row

        # Insert new session into session table
        cursor.execute("INSERT INTO Session (Movie, Cinema, Date, DayOfWeek, StartTime) VALUES (%s, %s, %s, %s, %s)",
                       (movie_id, cinema_id, date_str, day_of_week_str, start_time))

        flash('New movie added successfully!', 'success')

        cursor.close()

        return redirect(url_for('manager.movie_list_view'))
    
    return redirect(url_for('manager.movie_list_view'))

#-----------------Add New Session-------------------------------------

@manager_blueprint.route('/add_session/<int:movie_id>', methods=['GET', 'POST'])
def add_session(movie_id):

    if 'loggedin' not in session or session['role'] not in ['Manager', 'Admin']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
    cursor = getCursor()
    # get movie title
    cursor.execute("SELECT Title FROM Movie WHERE ID = %s", (movie_id,))
    movie = cursor.fetchone()
    movie_title = movie[0] if movie else "Unknown Movie"

    if request.method == 'POST':
        # get info from form
        cinema_id = request.form.get('cinema')
        date_str = request.form.get('date')
        start_time_str = request.form.get('startTime')
        date_object = datetime.strptime(date_str, '%Y-%m-%d')
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        start_datetime = datetime.combine(date_object, start_time)

        # get duration
        cursor.execute("SELECT Duration FROM Movie WHERE ID = %s", (movie_id,))
        duration_result = cursor.fetchone()
        duration = duration_result[0] if duration_result else 0  # if didn't find the duration，set duration as 0

        end_datetime = start_datetime + timedelta(minutes=duration)
        day_of_week = date_object.weekday()

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_of_week_str = day_names[day_of_week]

        # check for session conflicts
        if is_conflict_existing(cursor, cinema_id, date_str, start_datetime, end_datetime):
            flash("There is already a movie showing in this cinema at this time. Please select other cinemas or re-enter another Start Time!")
            return redirect(url_for('manager.add_session', movie_id=movie_id))
        

        # Insert new session into session table if no conflict
        cursor.execute("INSERT INTO Session (Movie, Cinema, Date, DayOfWeek, StartTime) VALUES (%s, %s, %s, %s, %s)",
                       (movie_id, cinema_id, date_str, day_of_week_str, start_time))

        flash('New session added successfully!', 'success')

        return redirect(url_for('manager.manager_movie_schedule_view'))    
        
    # If it's GET，then render template add_session.html
    cursor = getCursor()
    cursor.execute("SELECT ID, Title FROM Movie")
    movies = cursor.fetchall()

    cursor.execute("SELECT ID, Name FROM Cinema")
    cinemas = cursor.fetchall()

    cursor.close()

    return render_template('add_session.html', movies=movies, movie_title=movie_title, movie_id=movie_id,cinemas=cinemas)

#-----------------Delete Session-------------------------------------

@manager_blueprint.route('/manager_movie_schedule_delete/<int:session_id>', methods=['POST'])
def manager_movie_schedule_delete(session_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        #if the session has bookings, show warning message the session can not be deleted
        cursor.execute("SELECT * FROM Booking WHERE Session = %s", (session_id,))
        booking = cursor.fetchone()
        if booking:
            flash('The session can not be deleted as it has bookings!Please contact customers if needed.', 'error')
            return redirect(url_for('manager.manager_movie_schedule_view'))
        
        #if the session has no bookings, delete the session
        else:
            
            delete_tickets_query = "DELETE FROM Ticket WHERE SessionSeat IN (SELECT ID FROM SessionSeat WHERE Session = %s)"
            cursor.execute(delete_tickets_query, (session_id,))

            #delete session seat first
            delete_sessionseat_query = "DELETE FROM SessionSeat WHERE Session = %s"
            cursor.execute(delete_sessionseat_query, (session_id,))

            # Delete the session from the database
            delete_session_query = "DELETE FROM Session WHERE ID = %s"
            cursor.execute(delete_session_query, (session_id,))

            flash('Movie session deleted successfully!', 'success')

            cursor.close()

            return redirect(url_for('manager.manager_movie_schedule_view'))
    else:
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('login'))
    

#-----------------Delete Movie-------------------------------------

@manager_blueprint.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        #if the movie has bookings, show warning message the movie can not be deleted
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM Booking 
                JOIN Session ON Booking.Session = Session.ID 
                WHERE Session.Movie = %s
            )
        """, (movie_id,))

        booking_exists = cursor.fetchone()[0]

        if booking_exists:
            # if has booking, show flash message
            flash('One or more sessions of this movie have bookings! This movie can not be deleted!', 'error')
            return redirect(url_for('manager.movie_list_view'))

        #if no bookings of this movie, delete the record from database
        # delete all sessionseat of this movie
        cursor.execute("DELETE FROM SessionSeat WHERE Session IN (SELECT ID FROM Session WHERE movie = %s)", (movie_id,))

        # delete it's session from database
        cursor.execute("DELETE FROM Session WHERE movie = %s", (movie_id,))

        # delete movie from database
        cursor.execute("DELETE FROM Movie WHERE id = %s", (movie_id,))

        # flash message
        flash('Movie and related sessions deleted successfully!')

        cursor.close()

        return redirect(url_for('manager.movie_list_view'))
    
    else:
        return redirect(url_for('login'))

#-----------------Ticket Price List-------------------------------------

@manager_blueprint.route('/ticket_price_list', methods=['GET','POST'])
def ticket_price_list ():
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        # Get ticket price list
        cursor.execute("SELECT ID, TypeName, Price FROM TicketType")
        tickets = cursor.fetchall()

        cursor.close()

        return render_template('ticket_price_list.html', tickets = tickets)

    else:
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('login'))
    
#-----------------Edit Ticket Price -------------------------------------
    
@manager_blueprint.route('/update_ticket_price/<int:ticket_id>', methods=['POST'])
def update_ticket_price(ticket_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        new_price = request.form.get('new_price')
        cursor = getCursor()

        # update ticket price into database
        update_query = "UPDATE TicketType SET Price = %s WHERE ID = %s"
        cursor.execute(update_query, (new_price, ticket_id))

        flash('Ticket price updated successfully!', 'success')

        cursor.close()

        return redirect(url_for('manager.ticket_price_list'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))


#-----------------Promotion List-------------------------------------

@manager_blueprint.route('/promotion_list', methods=['GET','POST'])
def promotion_list ():
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        
        cursor.execute("SELECT ID, Code, Discount,CouponImage,Title,Description FROM Coupon")
        coupons = cursor.fetchall()

        cursor.execute("SELECT ID, DayOfWeek, DiscountPercent, DiscountImage,Title, Description FROM WeeklyDiscounts")
        weekly_discounts = cursor.fetchall()

        cursor.close()

        return render_template('promotion_list.html', coupons = coupons, weekly_discounts=weekly_discounts, user_role=session.get('role'))
        
    else:
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('login'))

#-----------------Food & Drinks List-------------------------------------

@manager_blueprint.route('/foodcombo_list', methods=['GET','POST'])
def foodcombo_list ():
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        search_term = request.args.get('search_term', '')
        if search_term:
            search_term = f"%{search_term}%"
            cursor.execute("SELECT ID, Name, Price,Image,Description FROM FoodCombo WHERE Name LIKE %s", (search_term,))
        else:
            cursor.execute("SELECT ID, Name, Price, Image, Description FROM FoodCombo")
        foodcombos = cursor.fetchall()

        cursor.close()

        return render_template('foodcombo_list.html', foodcombos = foodcombos, user_role=session.get('role'))
        
    else:
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('login'))
    
#-----------------Edit Weekly Discount -------------------------------------
@manager_blueprint.route('/edit_discount/<int:discount_id>', methods=['POST','GET'])
def edit_discount(discount_id):

    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        if request.method == 'GET':
            # Fetch the current discount details
            cursor.execute("SELECT ID, DayOfWeek, DiscountPercent, DiscountImage, Title, Description FROM WeeklyDiscounts WHERE ID = %s", (discount_id,))
            discount = cursor.fetchone()

            if discount:
                # Render the edit page with discount details
                return render_template('discount_edit.html', discount=discount,discount_id=discount_id)
            else:
                # Discount not found
                flash('Discount not found.', 'danger')
                return redirect(url_for('manager.promotion_list'))

        elif request.method == 'POST':
            # Get form data
            new_title = request.form['title']
            new_day_of_week = request.form['dayOfWeek']
            new_discount_percent = request.form['discountPercent']
            new_description = request.form['description']
            
            # Update the discount in the database
            update_query = """
                UPDATE WeeklyDiscounts SET 
                Title = %s, 
                DayOfWeek = %s, 
                DiscountPercent = %s, 
                Description = %s
                WHERE ID = %s
            """ 
            update_values = (new_title, new_day_of_week, new_discount_percent, new_description, discount_id)

            # Check if a new image has been uploaded
            discount_image = request.files.get('discountImage')
            if discount_image and discount_image.filename != '':
                filename = secure_filename(discount_image.filename)
                # Construct the path to the 'static/img' directory
                save_path = os.path.join('static', 'img', filename)
                # Full path to save the file
                full_save_path = os.path.join(app.root_path, save_path)
                discount_image.save(full_save_path)

                # Include the DiscountImage in the update
                cursor.execute("""
                    UPDATE WeeklyDiscounts 
                    SET Title = %s, DayOfWeek = %s, DiscountPercent = %s, Description = %s, DiscountImage = %s
                    WHERE ID = %s
                """, (new_title, new_day_of_week, new_discount_percent, new_description, filename, discount_id))

            cursor.execute(update_query, update_values)

            cursor.close()

            flash('Discount updated successfully!', 'success')
            return redirect(url_for('manager.promotion_list'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    

#-----------------Edit Food & Drinks -------------------------------------
    
@manager_blueprint.route('/edit_foodcombo/<int:foodcombo_id>', methods=['POST','GET'])
def edit_foodcombo(foodcombo_id):

    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        if request.method == 'GET':
            # get current foodcombo info
            cursor.execute("SELECT * FROM FoodCombo WHERE ID = %s", (foodcombo_id,))
            foodcombos = cursor.fetchone()
            return render_template('foodcombo_edit.html', foodcombos=foodcombos, foodcombo_id=foodcombo_id)
        
        elif request.method == 'POST':
            # check if this foodcombo has been ordered
            cursor.execute("SELECT * FROM BookingFoodCombo WHERE FoodComboID = %s", (foodcombo_id,))
            if cursor.fetchall():
                # if it's been ordered, can't be updated
                flash('Cannot update because this Food & Drinks already has order information. If necessary, please contact the customer.', 'danger')
                cursor.close()
                return redirect(url_for('manager.foodcombo_list', foodcombo_id=foodcombo_id))

            # get info from the form
            new_name = request.form.get('name')
            new_price = request.form.get('price')  
            new_description = request.form.get('description')

            update_query = """
                UPDATE FoodCombo
                SET Name = %s, Price = %s, Description = %s
                WHERE ID = %s
            """
            update_values = (new_name, new_price, new_description, foodcombo_id)

            # Check if a new image has been uploaded
            foodcombo_image = request.files.get('FoodcomboImage')
            if foodcombo_image and foodcombo_image.filename != '':
                filename = secure_filename(foodcombo_image.filename)
                # Construct the path to the 'static/img' directory
                save_path = os.path.join('static', 'img', filename)
                # Full path to save the file
                full_save_path = os.path.join(app.root_path, save_path)
                foodcombo_image.save(full_save_path)

                # Include the Image in the update
                cursor.execute("""
                    UPDATE FoodCombo 
                    SET Name = %s, Price = %s, Description = %s, Image = %s
                    WHERE ID = %s
                """, (new_name, new_price, new_description, filename, foodcombo_id))

            cursor.execute(update_query, update_values)

            cursor.close()
                
            flash('Food & Drinks updated successfully!', 'success')
            return redirect(url_for('manager.foodcombo_list'))
        
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))


#-----------------Edit Coupon -------------------------------------
    
@manager_blueprint.route('/edit_coupon/<int:coupon_id>', methods=['POST','GET'])
def edit_coupon(coupon_id):

    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        if request.method == 'GET':
            # get current coupon info
            cursor.execute("SELECT * FROM Coupon WHERE ID = %s", (coupon_id,))
            coupon = cursor.fetchone()
            return render_template('coupon_edit.html', coupon=coupon, coupon_id=coupon_id)
        
        elif request.method == 'POST':
            # get info from the form
            new_title = request.form.get('title')
            new_discount = request.form.get('discount')  
            new_code = request.form.get('coupon_code')
            new_description = request.form.get('description')

            update_query = """
                UPDATE Coupon
                SET Title = %s, Code = %s, Discount = %s, Description = %s
                WHERE ID = %s
            """
            update_values = (new_title, new_code, new_discount, new_description, coupon_id)

            # Check if a new image has been uploaded
            coupon_image = request.files.get('couponImage')
            if coupon_image and coupon_image.filename != '':
                filename = secure_filename(coupon_image.filename)
                # Construct the path to the 'static/img' directory
                save_path = os.path.join('static', 'img', filename)
                # Full path to save the file
                full_save_path = os.path.join(app.root_path, save_path)
                coupon_image.save(full_save_path)

                # Include the CouponImage in the update
                cursor.execute("""
                    UPDATE Coupon 
                    SET Title = %s, Code = %s, Discount = %s, Description = %s, CouponImage = %s
                    WHERE ID = %s
                """, (new_title, new_code, new_discount, new_description, filename, coupon_id))

            cursor.execute(update_query, update_values)
            cursor.close()
                
            flash('Coupon updated successfully!', 'success')
            return redirect(url_for('manager.promotion_list'))
        
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    

#-----------------Add Foodcombo -------------------------------------
@manager_blueprint.route('/add_foodcombo', methods=['POST'])
def add_foodcombo():

    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        # get info from the form
        name = request.form['Name']
        price = request.form['price']
        description = request.form['description']  
        image = request.files['Image']

        # Check if the food item already exists in the database
        cursor.execute("SELECT * FROM FoodCombo WHERE Name = %s", (name,))
        if cursor.fetchone():
            # If the food item exists, flash a message and redirect to the foodcombo list page
            flash('This food item already exists, please enter a different food name.', 'warning')
            return redirect(url_for('manager.foodcombo_list'))

        # deal the img
        if image and image.filename !='':
            filename = secure_filename(image.filename)
            save_path = os.path.join(app.root_path,'static','img', filename)
            image.save(save_path)

            #INSERT into database
            cursor.execute("INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES (%s,%s,%s,%s)",
                           (name, price, filename, description))
            
            flash('New Food & Drinks added successfully!','success')

            cursor.close()

            return redirect(url_for('manager.foodcombo_list'))
        
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
    
#-----------------Add Coupon -------------------------------------
@manager_blueprint.route('/add_coupon', methods=['POST'])
def add_coupon():

    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        # get info from the form
        title = request.form['CouponTitle']
        code = request.form['code']
        description = request.form['description']
        discount = request.form['discount']  
        coupon_image = request.files['CouponImage']

        # deal the img
        if coupon_image and coupon_image.filename !='':
            filename = secure_filename(coupon_image.filename)
            save_path = os.path.join(app.root_path,'static','img', filename)
            coupon_image.save(save_path)

            #INSERT into database
            cursor.execute("INSERT INTO Coupon (Code, Discount, CouponImage, Title, Description) VALUES (%s,%s,%s,%s,%s)",
                           (code, discount, filename, title, description))
            
            cursor.close()
            
            flash('New coupon added successfully!','success')

            return redirect(url_for('manager.promotion_list'))
        
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    

#-----------------Add Weekly Discount -------------------------------------

@manager_blueprint.route('/add_discount', methods=['POST'])
def add_discount():

    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()

        # get info from the form
        title = request.form['DiscountTitle']
        day_of_week = request.form['DayOfWeek']
        description = request.form['description']
        discount_percent = request.form['DiscountPercent']  
        discount_image = request.files['DiscountImage']

        # deal the img
        if discount_image and discount_image.filename !='':
            filename = secure_filename(discount_image.filename)
            save_path = os.path.join(app.root_path,'static','img', filename)
            discount_image.save(save_path)

            #INSERT into database
            cursor.execute("INSERT INTO WeeklyDiscounts (DayOfWeek, DiscountPercent, DiscountImage, Title, Description) VALUES (%s,%s,%s,%s,%s)",
                           (day_of_week, discount_percent, filename, title, description))
            
            cursor.close()
            
            flash('New Weekly Discount added successfully!','success')

            return redirect(url_for('manager.promotion_list'))
        
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
#-----------------Delete Coupon -------------------------------------
@manager_blueprint.route('/delete_coupon/<int:coupon_id>', methods=['POST'])
def delete_coupon(coupon_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        try:
            cursor.execute("DELETE FROM Coupon WHERE ID = %s", (coupon_id,))
            flash('Coupon deleted successfully!', 'success')
        except Exception as e:
            flash('Failed to delete coupon. Error: {}'.format(str(e)), 'danger')
        finally:
            cursor.close()

        cursor.close()

        return redirect(url_for('manager.promotion_list'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
    
#-----------------Delete Discount -------------------------------------
@manager_blueprint.route('/delete_discount/<int:discount_id>', methods=['POST'])
def delete_discount(discount_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        try:
            cursor.execute("DELETE FROM WeeklyDiscounts WHERE ID = %s", (discount_id,))
            flash('Weekly discount deleted successfully!', 'success')
        except Exception as e:
            flash('Failed to delete weekly discount. Error: {}'.format(str(e)), 'danger')
        finally:
            cursor.close()

        cursor.close()

        return redirect(url_for('manager.promotion_list'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
#-----------------Delete Food & Drinks -------------------------------------
@manager_blueprint.route('/delete_foodcombo/<int:foodcombo_id>', methods=['POST'])
def delete_foodcombo(foodcombo_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        # check if this foodcombo has been ordered
        try:
            cursor.execute("SELECT * FROM BookingFoodCombo WHERE FoodComboID = %s", (foodcombo_id,))
            booking = cursor.fetchall()
            if booking:
                # if has order information, can't be deleted
                flash('Cannot delete because this Food & Drinks already has order information. If necessary, please contact the customer.', 'danger')
                return redirect(url_for('manager.foodcombo_list'))
            # if don't have any order information, continue delete
            cursor.execute("DELETE FROM FoodCombo WHERE ID = %s", (foodcombo_id,))
            flash('Food & Drinks deleted successfully!', 'success')
        except Exception as e:
            flash('Failed to delete Food & Drinks. Error: {}'.format(str(e)), 'danger')
        finally:
            cursor.close()

        return redirect(url_for('manager.foodcombo_list'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
