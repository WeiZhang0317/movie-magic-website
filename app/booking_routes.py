# As a customer,  I want to be able to choose session times, and then choose my seats in the hall based on the movie I chose, this way I can get the best viewing experience.

# Criteria:
# The ticket booking system should allow me to view session times for today and the next 7 days. After that, I can click to choose one from them.

# The ticket booking system should allow me to select seats based on the session I choose.

# A detailed seat map should be displayed, showing all available and occupied seats in real-time.

# Interactive Seat Selection: I should be able to click on available seats on the map to select them for my booking.

from flask import Blueprint, Flask, json, render_template, request, jsonify, session,redirect, url_for
import mysql.connector
import connect
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import time

# Create a Blueprint named 'booking' for handling booking-related routes
booking_blueprint = Blueprint('booking', __name__)

# Function to get a database cursor
def getCursor(dictionary_cursor=False):
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, database=connect.dbname, autocommit=True)
    cursor = connection.cursor(dictionary=dictionary_cursor)
    return cursor

# Route for viewing and selecting movie sessions
@booking_blueprint.route('/bookings', methods=['GET', 'POST'])
def bookings():     
    selected_movie_id = request.args.get('selected_movie_id')   

    cursor = getCursor(dictionary_cursor=True)
    movie_query = "SELECT * FROM Movie WHERE ID = %s"
    cursor.execute(movie_query, (selected_movie_id,))
    movie_details = cursor.fetchone()

    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        query = """
            SELECT Session.ID, Session.StartTime, Cinema.Name as CinemaName
            FROM Session
            INNER JOIN Cinema ON Session.Cinema = Cinema.ID
            WHERE Session.Movie = %s AND Session.Date = %s
        """
        cursor.execute(query, (selected_movie_id, selected_date))
        data = cursor.fetchall()
        sessions_info = [{'start_time': str(entry['StartTime']), 'session_id': entry['ID'], 'cinema_name': entry['CinemaName']} for entry in data]
        return jsonify({'sessions': sessions_info})
    
    cursor.close()
    connection.close()
    return render_template('booking/select_session.html',movie=movie_details)


# Route for selecting seats for a specific session
@booking_blueprint.route('/bookings/<int:session_id>', methods=['GET'])
def select_seats(session_id):
    cursor = getCursor()
    query = """
        SELECT s.RowNumber, s.SeatNumber, ss.Available
        FROM Seat s
        INNER JOIN SessionSeat ss ON s.ID = ss.Seat
        WHERE ss.Session = %s AND s.Cinema = (SELECT Cinema FROM Session WHERE ID = %s);
        """
    cursor.execute(query, (session_id,session_id,))
    seats = cursor.fetchall()

     # Fetch the Movie ID associated with the session
    movie_id_query = "SELECT Movie,Cinema FROM Session WHERE ID = %s"
    cursor.execute(movie_id_query, (session_id,))
    movie_id_result = cursor.fetchone() 

    if movie_id_result:
        selected_movie_id, selected_cinema_id = movie_id_result
    else:
        return "Session not found", 404
    
    # Get session information (date, time, movie name)
    cursor.execute("""
                SELECT DATE_FORMAT(s.Date, '%d/%m/%Y') AS session_date,
                    DATE_FORMAT(s.StartTime, '%H:%i') AS session_time,
                    m.Title,
                    m.image
                FROM Session s
                JOIN Movie m ON s.Movie = m.ID
                WHERE s.ID = %s
                GROUP BY s.ID;
        """, (session_id,))
    session_info = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('booking/select_seats.html', seats=seats, session_id=session_id, session_info=session_info, cinema=selected_cinema_id)

# Route for selecting tickets and food 
@booking_blueprint.route('/bookings/<int:session_id>/select_tickets',methods=['GET', 'POST'])
def select_tickets(session_id):
    cursor = getCursor()

    # Fetch ticket types
    query = "SELECT ID, TypeName, Price FROM TicketType"
    cursor.execute(query)
    ticket_types = cursor.fetchall()
    ticket_types = [(ticket[0], ticket[1], str(ticket[2])) for ticket in ticket_types]

    seat_info = request.args.get('seatInfo')
    session['selected_seats'] = seat_info

    # Fetch food combo types
    food_combo_query = "SELECT ID, Name, Price, Image, Description FROM FoodCombo"
    cursor.execute(food_combo_query)
    food_combos = cursor.fetchall()
    food_combos = [(combo[0], combo[1], str(combo[2]), combo[3], combo[4]) for combo in food_combos]


    # Fetch the Movie details
    movie_id_query = "SELECT Movie FROM Session WHERE ID = %s"
    cursor.execute(movie_id_query, (session_id,))
    movie_id_result = cursor.fetchone() 
    selected_movie_id = movie_id_result[0]

    movie_query = "SELECT * FROM Movie WHERE ID = %s"
    cursor.execute(movie_query, (selected_movie_id,))
    movie_details = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('booking/select_tickets.html',session_id=session_id, ticket_types=ticket_types, movie=movie_details,food_combos=food_combos)




