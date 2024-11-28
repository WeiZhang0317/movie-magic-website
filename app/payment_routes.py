# As a customer, I want to make swift and hassle-free payments on the website, so that I can efficiently complete the transaction.

# Criteria:

# Provide options to select ticket types (children, students, adults, seniors) for varied pricing.
# The number of tickets I can select must match my chosen seats; otherwise, the system will prompt an error.
# A field to enter promotion codes and gift card numbers with an immediate display of the discounted price. 

from flask import Blueprint, Flask, json, render_template, request, jsonify, session,redirect, url_for
import mysql.connector
import connect
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import threading
import time

payment_blueprint = Blueprint('payment', __name__)

# Function to get a database cursor
def getCursor(dictionary_cursor=False):
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, database=connect.dbname, autocommit=True)
    cursor = connection.cursor(dictionary=dictionary_cursor)
    return cursor

# Route for applying a promotion code
@payment_blueprint.route('/apply_promotion', methods=['GET'])
def apply_promotion():
    promotion_code = request.args.get('code')
    promoid = validate_and_check_promotion(promotion_code)
    if promoid is None:
       return jsonify({'error': 'Invalid or used promotion code'})
    cursor = getCursor()
    cursor.execute('SELECT Discount FROM Coupon WHERE ID =  %s', (promoid,))
    discount = cursor.fetchone()
    discount = discount[0]
    cursor.close()
    connection.close()
    return jsonify({'success': True, 'discount': discount})

# Function to validate and check a promotion code
def validate_and_check_promotion(promotion_code):
    try:
        cursor = getCursor()
        cursor.execute('SELECT ID FROM Coupon WHERE Code = %s', (promotion_code,))
        promoid = cursor.fetchone()
        if promoid:
            user_id = session.get('user_id')
            promoid = promoid[0]
            cursor.execute('SELECT ID FROM UserCouponUsage WHERE User = %s AND Coupon = %s', (user_id, promoid))         
            existing_record = cursor.fetchone()
            if existing_record:
                return None  # Promotion code already used
            else:
                session['promoid'] = promoid
                return promoid
                
    finally:
        cursor.close()  # Close cursor

    return None  # Invalid promotion code

# Route for checking gift card balance
@payment_blueprint.route('/check_giftcardBalance', methods=['GET'])
def check_giftcard_balance():
    try:
        cursor = getCursor()
        giftcard_number = request.args.get('number')       
        print(giftcard_number)
        query = "SELECT Balance FROM GiftCard WHERE Number = %s"
        cursor.execute(query, (giftcard_number,))
        result = cursor.fetchone()
        print(result)

        if result:
            balance = result[0] 
            print(balance)
            return {"success": True, "balance": balance}
        else:
            return {"success": False, "error": "Gift card not found"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()  # Close cursor


# Route for processing ticket bookings
@payment_blueprint.route('/bookings/<int:session_id>/process_tickets', methods=['POST'])
def process_tickets(session_id):

    selected_seats = session.get('selected_seats')
    # Retrieve selected ticket information from the form data
    ticket_ids = request.form.getlist('ticket_id[]')
    ticket_counts = request.form.getlist('ticket_count[]')
    ticket_prices = request.form.getlist('ticket_price[]')

    selected_tickets = []

    for ticket_id, ticket_count, ticket_price in zip(ticket_ids, ticket_counts, ticket_prices):
        ticket_id = int(ticket_id)
        ticket_count = int(ticket_count)
        ticket_price_decimal = Decimal(str(ticket_price))
        ticket_price = ticket_price_decimal.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        

        # Execute SQL query to get TypeName based on ID
        cursor = getCursor()
        cursor.execute("SELECT TypeName FROM TicketType WHERE ID = %s", (ticket_id,))
        result = cursor.fetchone()

        if result:
            typename = result[0]
            selected_tickets.append({
                'typename': typename,
                'count': ticket_count,
                'price': ticket_price
            })

    # Retrieve selected food information from the form data
    food_ids = request.form.getlist('food_id[]')
    food_counts = request.form.getlist('food_count[]')
    food_prices = request.form.getlist('food_price[]')

    selected_food_combos = []

    for food_id, food_count, food_price in zip(food_ids, food_counts, food_prices):
        food_id = int(food_id)
        food_count = int(food_count)
        food_price_decimal = Decimal(str(food_price))
        food_price = food_price_decimal.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)


        # Get food name based on ID
        cursor.execute("SELECT Name FROM FoodCombo WHERE ID = %s", (food_id,))
        result = cursor.fetchone()

        if result:
            food_name = result[0]
            selected_food_combos.append({
                'food_id': food_id,
                'count': food_count,
                'price': food_price,
                'food_name': food_name
            })


    # Get session information (date, time, movie name)
    cursor.execute("""
        SELECT s.Date, s.StartTime, m.Title, m.image
        FROM Session s
        JOIN Movie m ON s.Movie = m.ID
        WHERE s.ID = %s
        GROUP BY s.ID
    """, (session_id,))
    session_info = cursor.fetchone()

    session_date, session_time, movie_name, movie_img = session_info

    day_of_week = session_date.strftime("%A") 
    cursor.execute("SELECT DiscountPercent FROM WeeklyDiscounts WHERE DayOfWeek = %s", (day_of_week,))
    weeklydiscount_result = cursor.fetchone()
    cursor.close()
    connection.close()
    weeklydiscount_percent = float(weeklydiscount_result[0]) if weeklydiscount_result else 0
    weeklydiscount_percent = Decimal(weeklydiscount_percent)
    

    formatted_date = session_date.strftime("%d/%m/%Y")
    formatted_time = str(session_time)[:-3]

    user_id = session.get('user_id')

    total_food_price = sum(food['count'] * food['price'] for food in selected_food_combos)

    total_ticket_price = sum(ticket['count'] * ticket['price'] for ticket in selected_tickets)
    total_ticket_price = total_ticket_price * (1 - (weeklydiscount_percent / 100))
    
    total_price = total_ticket_price + total_food_price
    total_price = Decimal(str(total_price)).quantize(Decimal('0.00'))


    book_seat(user_id, selected_seats, session_id)
    booking_id = session.get('booking_id')
    


    return render_template('booking/payment.html', session_id=session_id, selected_tickets=selected_tickets,
                           selected_food_combos=selected_food_combos,
                            total_price=total_price,discount_message=get_discount_message(day_of_week, weeklydiscount_percent),
                            session_date=formatted_date, session_time=formatted_time,
                            movie_name=movie_name, movie_img=movie_img, selected_seats=selected_seats,booking_id=booking_id)

  

# Function to get a discount message based on the day of the week    
def get_discount_message(day_of_week, discount_percent):
    if discount_percent > 0:
        return f"{day_of_week} Discount: {discount_percent}% off for ticket price."
    else:
        return " "

# Function to check and update booking status with a delayed task    
def check_and_update_booking_status(booking_id, sessionseats):
    cursor = getCursor()
    cursor.execute("SELECT Status FROM Booking WHERE ID = %s", (booking_id,))
    current_status = cursor.fetchone()[0]

    if current_status == 'pending':
        print(f"Updating status for Booking ID {booking_id} from 'pending' to 'cancel'")
        cursor.execute("UPDATE Booking SET Status = 'canceled' WHERE ID = %s", (booking_id,))

        for session_seat_id in sessionseats:
            cursor.execute("UPDATE SessionSeat SET Available = TRUE WHERE ID = %s", (session_seat_id,))
    cursor.close()
    connection.close()

# Function to start a delayed task for updating booking status
def start_delayed_task(booking_id, delay_seconds, sessionseats):
    threading.Timer(delay_seconds, check_and_update_booking_status, args=[booking_id, sessionseats]).start()
    
# Function to book seats
def book_seat(user_id, selected_seats, session_id):
    cursor = getCursor()
    sessionseat_ids = []

    # new booking
    booking_query = "INSERT INTO Booking (User, Session, CreatedTime, Status) VALUES (%s, %s, CURRENT_TIMESTAMP, 'pending')"
    cursor.execute(booking_query, (user_id, session_id))

    booking_id = cursor.lastrowid
    session['booking_id'] = booking_id

    # loop through all seats
    for seat in selected_seats.split(','):
        row_number, seat_number = parse_seat(seat)  

        cinema_query = "SELECT Cinema FROM Session WHERE ID = %s"
        cursor.execute(cinema_query, (session_id,))
        cinema_id = cursor.fetchone()[0]

        seat_query = "SELECT ID FROM Seat WHERE RowNumber = %s AND SeatNumber = %s AND Cinema = %s"
        cursor.execute(seat_query, (row_number, seat_number, cinema_id))
        seat_id = cursor.fetchone()[0]

        session_seat_query = "SELECT ID FROM SessionSeat WHERE Session = %s AND Seat = %s"
        cursor.execute(session_seat_query, (session_id, seat_id))       
        session_seat_id = cursor.fetchone()[0]
        sessionseat_ids.append(session_seat_id)
        

        # update SessionSeat record，change status to reserved.
        session_seat_update_query = "UPDATE SessionSeat SET Available = FALSE WHERE ID = %s"
        cursor.execute(session_seat_update_query, (session_seat_id,))

    cursor.close() 
    connection.close()
    session['sessionseats'] = sessionseat_ids
    delay_seconds = 600
    start_delayed_task(booking_id, delay_seconds,sessionseat_ids)

     
# Helper function to parse seat information
def parse_seat(seat):
    row_letter, seat_number = seat.split('-')
    row_number = ord(row_letter.upper()) - ord('A') + 1  
    return row_number, int(seat_number)

# Route for handling payment success
@payment_blueprint.route('/payment_successful', methods=['POST'])
def payment_successful():

    payment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  

    booking_id = session.get('booking_id')
    sessionseats = session.get('sessionseats')

    total_amount = request.form.get('totalPrice') 
    ticket_type_names = request.form.getlist('ticketTypeName[]')
    discount = request.form.get('discount') 
    payment_method = request.form.get('paymentMethod') 


    total_amount = float(total_amount) - float(discount)

    cursor = getCursor()

    # Check if foods are selected
    food_combos = request.form.getlist('foodComboId[]')
    if food_combos:
        food_combo_query = "INSERT INTO BookingFoodCombo (BookingID, FoodComboID) VALUES (%s, %s)"
        for food_combo in food_combos:
            cursor.execute(food_combo_query, (booking_id, food_combo))

    booking_query = "UPDATE Booking SET Status = 'paid' WHERE ID = %s"
    cursor.execute(booking_query, (booking_id,))


    ticket_query = """
        INSERT INTO Ticket (Booking, SessionSeat, TicketType)
        VALUES (%s, %s, (SELECT ID FROM TicketType WHERE TypeName = %s))
    """

    for session_seat_id, ticket_type_name in zip(sessionseats, ticket_type_names):
        cursor.execute(ticket_query, (booking_id, session_seat_id, ticket_type_name))

    # Check if a gift card is used for payment
    gift_card_number = request.form.get('giftCardNumber')
    if gift_card_number:
        giftcard_query = "SELECT Balance FROM GiftCard WHERE Number = %s"
        cursor.execute(giftcard_query, (gift_card_number,))
        result = cursor.fetchone()
        balance = float(result[0])

         # Calculate the gift card amount used for payment
        giftcardamount = min(total_amount, balance)
        other_payment_amount = total_amount - balance
        new_balance = max(0, balance - total_amount)

        update_query = "UPDATE GiftCard SET Balance = %s WHERE Number = %s"
        cursor.execute(update_query, (new_balance, gift_card_number))

        giftcard_payment_query = "INSERT INTO Payment (BookingID, PaymentTime, PaymentMethod, TotalAmount) VALUES (%s, %s, 'giftcard', %s)"
        cursor.execute(giftcard_payment_query, (booking_id, payment_time, giftcardamount))

        if other_payment_amount > 0:
            other_payment_query = "INSERT INTO Payment (BookingID, PaymentTime, PaymentMethod, TotalAmount) VALUES (%s, %s, %s, %s)"
            cursor.execute(other_payment_query, (booking_id, payment_time, payment_method, other_payment_amount))

    else:
        payment_query = "INSERT INTO Payment (BookingID, PaymentTime, PaymentMethod, TotalAmount) VALUES (%s, %s, %s, %s)"
        cursor.execute(payment_query, (booking_id, payment_time, payment_method, total_amount))

    # Check if a promotion code is used and insert usage record into the database
    if 'promoid' in session and session['promoid'] is not None and float(discount) > 0:
        user_id = session.get('user_id')
        coupon_id = session.get('promoid')

        cursor.execute('INSERT INTO UserCouponUsage (User, Coupon) VALUES (%s, %s)', (user_id, coupon_id))



    session.pop('promoid', None)
    cursor.close()
    connection.close()

    return render_template('booking/payment_successful.html')
