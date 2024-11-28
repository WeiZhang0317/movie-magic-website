# As a theatre staff member, I want to log in and access the staff dashboard, so that I can perform my duties effectively.

# Criteria:
# Secure login.
# View my profile details
# View movie session times
# Check customer into their movie

from flask import Blueprint, render_template,request, redirect, url_for, session, flash,jsonify,json
import re
import bcrypt
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
from flask import session
import connect
from werkzeug.utils import secure_filename
from app.main_routes import getCursor


staff_blueprint = Blueprint('staff', __name__)

@staff_blueprint.route('/staff_dashboard')
def staff_dashboard():
    
    return render_template('staff_dashboard.html')

@staff_blueprint.route('/staff_select_session')
def staff_select_session():
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin', 'Staff']:
        # Paging parameters
        page = request.args.get('page', 1, type=int)
        per_page = 4

        # Retrieve search and filter parameters
        order = request.args.get('order', 'asc')
        search_query = request.args.get('search', '')
        filter_day = request.args.get('day', '')
        filter_cinema = request.args.get('cinema', '')

       #Basic query
        query = """
            SELECT s.ID, m.Title, c.Name, s.StartTime, s.Date, s.DayOfWeek 
            FROM Session s
            JOIN Movie m ON s.Movie = m.ID
            JOIN Cinema c ON s.Cinema = c.ID
            WHERE m.Title LIKE %s AND s.Date >= CURRENT_DATE
        """
        
       # Add filters 
        query_params = ["%" + search_query + "%"]
        if filter_day:
            query += " AND s.DayOfWeek = %s "
            query_params.append(filter_day)
        if filter_cinema:
            query += " AND c.Name = %s "
            query_params.append(filter_cinema)

        #Add sorting conditions
        order_direction = 'DESC' if order == 'desc' else 'ASC'
        query += " ORDER BY s.Date {0}, s.StartTime {0}".format(order_direction)

       # Get cursor
        cursor = getCursor(dictionary_cursor=True)

        # Calculate the total number of records that match the current filtering conditions
        count_query = query.replace("SELECT s.ID, m.Title, c.Name, s.StartTime, s.Date, s.DayOfWeek", "SELECT COUNT(*)")
        cursor.execute(count_query, query_params)
        total_sessions = cursor.fetchone()
        total_sessions=total_sessions['COUNT(*)'] 
        total_pages = (total_sessions + per_page - 1) // per_page

        # Add LIMIT and OFFSET to the query
        paginated_query = query + " LIMIT %s OFFSET %s"
        query_params.extend([per_page, (page - 1) * per_page])

      # Execute paging query
        cursor.execute(paginated_query, query_params)
        sessions = cursor.fetchall()
        # Format date and time for each session
        for session_item in sessions:
            # Check if the 'Date' and 'StartTime' keys exist in the session_item
            if 'Date' in session_item and 'StartTime' in session_item:
                # Format date from 'YYYY-MM-DD' to 'DD-MM-YYYY'
                session_item['Date'] = session_item['Date'].strftime('%d-%m-%Y')
                
                # Format time to 'HH:MM'
                total_minutes = session_item['StartTime'].total_seconds() // 60
                hours = total_minutes // 60
                minutes = total_minutes % 60
                session_item['StartTime'] = f"{int(hours):02d}:{int(minutes):02d}"
        # Get the list of cinemas as a filter
        cinema_sql = "SELECT * FROM Cinema;"
        cursor.execute(cinema_sql)
        cinemas = cursor.fetchall()
        
        cursor.close()
      
        return render_template('staff_select_session.html', sessions=sessions, total_pages=total_pages, current_page=page, cinemas=cinemas, order=order, search_query=search_query, filter_day=filter_day, filter_cinema=filter_cinema)
    else:
        return redirect(url_for('main.home'))
 

@staff_blueprint.route('/staff_checkin/<int:session_id>')
def staff_checkin(session_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin','Staff']:
        with getCursor(dictionary_cursor=True) as cursor:
            # get seat information
            cursor.execute("""
                SELECT 
                    ss.ID as SessionseatID,       
                    s.RowNumber,
                    s.SeatNumber,
                    ss.Available
            FROM Seat s
        INNER JOIN SessionSeat ss ON s.ID = ss.Seat
        WHERE ss.Session = %s AND s.Cinema = (SELECT Cinema FROM Session WHERE ID = %s);
                """, (session_id,session_id))
            seats = cursor.fetchall()
            #h get checked seats
            cursor.execute("""
                SELECT Booking.Session as SessionID, Ticket.Booking as BookingID,
                Ticket.SessionSeat as SessionSeatID, 
                Ticket.Checkin as Checkin
                FROM Ticket 
                Join Booking On
                Ticket.Booking=Booking.ID
                          Where
                  Booking.Session = %s and Ticket.Checkin=1;
                """, (session_id,))
            checkedseats=cursor.fetchall()

            # get booking information
            cursor.execute("""
                SELECT 
                      ss.Session, 
                    s.RowNumber, 
                    s.SeatNumber,
					DATE_FORMAT(Session.Date, '%d/%m/%Y') AS session_date,
					DATE_FORMAT(Session.StartTime, '%H:%i') AS session_time,
                    Session.DayOfWeek,
                    Movie.Title,
                    ss.ID as seatID, 
                    t.Booking as BookingID, 
                    u.Email as UserEmail,
                    COALESCE(c.FirstName, st.FirstName, mn.FirstName, ad.FirstName) AS FirstName,
                    COALESCE(c.LastName, st.LastName, mn.LastName, ad.LastName) AS LastName,
                    COALESCE(c.Mobile, st.Mobile, mn.Mobile, ad.Mobile) AS Mobile
                
                FROM 
                    Seat s
                JOIN 
                    SessionSeat ss ON s.ID = ss.Seat
                JOIN 
                   Ticket t ON t.SessionSeat=ss.ID
                JOIN
                   Booking b ON b.ID=t.Booking
                JOIN
				  User u ON  b.User=u.ID
                 JOIN
                 Session ON ss.Session=Session.ID
                 JOIN Movie on Session.Movie=Movie.ID
                 LEFT JOIN 
                    Customer c ON u.ID = c.UserID
                LEFT JOIN 
                    Staff st ON u.ID = st.UserID
                LEFT JOIN 
                    Manager mn ON u.ID = mn.UserID
                LEFT JOIN 
                    Admin ad ON u.ID = ad.UserID  
                WHERE 
                    ss.Available = 0 AND b.Status="paid" AND ss.Session = %s;
                """, (session_id,))
            bookings = cursor.fetchall()

            # get cinema type and capacity
            cursor.execute("SELECT cinema FROM Session WHERE ID = %s;", (session_id,))
            cinema_type_result = cursor.fetchone()
            cinema_type = cinema_type_result['cinema'] if cinema_type_result else None

        return render_template('staff_checkin.html', session_id=session_id, checkedseats=checkedseats, seats=seats, bookings=bookings, cinema_type=cinema_type)
    else:
        return redirect(url_for('main.home'))



@staff_blueprint.route('/confirm_checkin', methods=['POST'])
def confirm_checkin():
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin', 'Staff']:
        data = request.json
        session_id = data.get('session_id')
        booking_id = data.get('booking_id')
        sessionseat_id = data.get('sessionseat_id')  

        if not all([session_id, booking_id, sessionseat_id]):
            return jsonify({"message": "Invalid data"}), 400

        with getCursor() as cursor:
            #Check if the same SessionID and sessionSeatID combination already exists
            cursor.execute("""
                SELECT Booking.Session as SessionID, Ticket.Booking as BookingID,
                Ticket.SessionSeat as SessionSeatID, 
                Ticket.Checkin as Checkin
                FROM Ticket 
                Join Booking On
                Ticket.Booking=Booking.ID
                WHERE Booking.Session = %s AND Ticket.SessionSeat = %s AND Ticket.Checkin =1;
                """, (session_id, sessionseat_id))
            if cursor.fetchone():
                return jsonify({"message": "Seat already checked in"}), 409

           #Insert new record
            cursor.execute("""
           UPDATE Ticket
            JOIN Booking ON Ticket.Booking = Booking.ID
            SET Ticket.Checkin = 1
            WHERE Booking.Session =  %s
            AND Ticket.Booking =  %s
            AND Ticket.SessionSeat =  %s
            """, (session_id, booking_id, sessionseat_id))

        return jsonify({"message": "Check-in confirmed"}), 200
    else:
        return jsonify({"message": "Unauthorized"}), 401
    
