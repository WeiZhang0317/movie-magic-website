# As a registered customer, I want to manage my profile, booking history and gift card balance.

# Criteria:
# The dashboard allows users to view and edit their profiles, 
# View booking history.
# View gift card balance
# View my eligibility for promotions.
# Changes to personal information are updated immediately in the system.
# The dashboard is user-friendly and accessible on various screen sizes.
from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
import connect
from collections import defaultdict
from app.main_routes import getCursor

customer_blueprint = Blueprint('customer', __name__)

@customer_blueprint.route('/customer_dashboard')
def customer_dashboard():
    if 'loggedin' in session and session['role'] == 'Customer':
        return render_template('customer_dashboard.html')
    else:
        return redirect(url_for('main.home'))
    
@customer_blueprint.route('/booking_details/<int:booking_id>')
def booking_details(booking_id):
    # Fetch additional information related to the booking (tickets, seat, food) from the database
    # Use the booking_id parameter to query the database and get the required information
    # Render a new HTML template to display the details
    details = get_booking_details(booking_id)
    return render_template('booking_details.html', booking_id=booking_id, details=details)

def get_booking_details(booking_id):
    # Implement the database query to fetch details related to tickets, seat, and food
    # Return the details in a format that can be used by the template
    details = {
        'tickets': get_ticket_and_seat_for_booking(booking_id),
        'food_combos': get_food_combos_for_booking(booking_id),
        'food_quantity': get_food_quantity(get_food_combos_for_booking(booking_id))
    }
    return details

def get_food_quantity(food_combos):
    # Create a defaultdict to store the quantity of each food item
    food_quantity = defaultdict(int)

    # Count the quantity of each food item
    for food_name, _ in food_combos:
        food_quantity[food_name] += 1

    return food_quantity

def get_ticket_and_seat_for_booking(booking_id):
    cursor = getCursor()
    query = """
        SELECT TicketType.TypeName, TicketType.Price, 
               CHAR(Seat.RowNumber + 64) AS SeatRowLetter, Seat.SeatNumber
        FROM Ticket
        JOIN TicketType ON Ticket.TicketType = TicketType.ID
        JOIN SessionSeat ON Ticket.SessionSeat = SessionSeat.ID
        JOIN Seat ON SessionSeat.Seat = Seat.ID
        WHERE Ticket.Booking = %s
    """
    cursor.execute(query, (booking_id,))
    ticket_and_seat_info = cursor.fetchall()
    cursor.close()
    return ticket_and_seat_info


def get_food_combos_for_booking(booking_id):
    cursor = getCursor()
    query = """
        SELECT FoodCombo.Name, FoodCombo.Price
        FROM BookingFoodCombo
        JOIN FoodCombo ON BookingFoodCombo.FoodComboID = FoodCombo.ID
        WHERE BookingFoodCombo.BookingID = %s
    """
    cursor.execute(query, (booking_id,))
    food_combos = cursor.fetchall()
    cursor.close()
    return food_combos

@customer_blueprint.route('/customer_booking_history')
def customer_booking_history():
    if 'loggedin' in session and session['role'] == 'Customer':
    
        user_id = session['user_id']
        cursor = getCursor()

        cursor.execute("""
    SELECT
        Booking.ID AS booking_id,
        Movie.Title AS movie_title,
        DATE_FORMAT(Session.Date, '%d/%m/%Y') AS session_date,
        Session.DayOfWeek AS session_day,
        TIME_FORMAT(Session.StartTime, '%h:%i') AS session_time,
        TIME_FORMAT(Session.StartTime + INTERVAL Movie.Duration MINUTE, '%h:%i') AS session_end_time,
        Cinema.Name AS cinema_name
    FROM
        Booking
    JOIN
        Session ON Booking.Session = Session.ID
    JOIN
        Movie ON Session.Movie = Movie.ID
    JOIN
        Cinema ON Session.Cinema = Cinema.ID
    WHERE
        Booking.User = %s
        AND Booking.Status = 'paid'
    ORDER BY
        Session.Date DESC
""", (user_id,))

        booking_history = cursor.fetchall()
        print(booking_history)

        return render_template('customer_booking_history.html', booking_history=booking_history)
    else:
        return redirect(url_for('main.home'))

@customer_blueprint.route('/customer_gift_cards')
def customer_gift_cards():
    if 'loggedin' in session and session['role'] == 'Customer':
        user_id = session['user_id']
        print(user_id)
        cursor = getCursor()

        # Fetch user email using user_id
        cursor.execute("""
            SELECT Email
            FROM User
            WHERE ID = %s
        """, (user_id,))

        user_email_result = cursor.fetchone()
        user_email = user_email_result[0]
        print(user_email)
        cursor.execute("""
            SELECT Number, Balance, Type, ImgPath
            FROM GiftCard
            WHERE Email = %s
        """, (user_email,))
        gift_cards = cursor.fetchall()
        print(gift_cards)


        return render_template('customer_gift_cards.html', gift_cards=gift_cards)
    
    else:
        return redirect(url_for('main.home'))
    
@customer_blueprint.route('/buy_gift_card')
def gift_cards():
    return render_template('gift_card.gift_cards.html')

@customer_blueprint.route('/customer_support')
def customer_support():
    return render_template('customer_support.html')

@customer_blueprint.route('/customer_profile')
def customer_profile():
    if 'loggedin' in session and session['role'] == 'Customer':
        return render_template('customer_profile.html')
    else:
        return redirect(url_for('main.home'))
