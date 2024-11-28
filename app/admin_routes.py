# As a system administrator, I want to log into the system, do all the system functions and manage settings.

# Criteria:
# Secure login.
# View and manage my profile details
# View and manage staff profiles
# View and manage all customer profiles
# View and manage movie session times, name, description, category, and ratings
# Assign movies to different sessions
# View and manage promotions
# Manage ticket prices
# The administrator can categorize movies by movie type and rating, place them into different category lists, and manage these category lists.  
# Generate the report

from flask import Blueprint, render_template,session,redirect,url_for,request, flash
from app.main_routes import getCursor
from app.user_routes import is_valid_age, is_strong_password, email_exists_registered, is_valid_phone_number, mobile_exists
admin_blueprint = Blueprint('admin', __name__)

import bcrypt


@admin_blueprint.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


#-----------------staff list view-------------------------------------
@admin_blueprint.route('/admin/staff_list_view')
def staff_list_view():
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        search_query = request.args.get('search', '')
        cursor = getCursor()

        sql_query = """SELECT
                                S.UserID,
                                S.FirstName,
                                S.LastName,
                                U.Email,
                                S.Mobile,
                                U.Role,
                                U.IsActive
                            FROM
                                Staff AS S
                            JOIN
                                User AS U ON S.UserID = U.ID
                            WHERE 
                            U.IsActive=1
                            AND
                            (S.FirstName LIKE %s OR S.LastName LIKE %s)

                            UNION ALL

                            SELECT
                                M.UserID,
                                M.FirstName,
                                M.LastName,
                                U.Email,
                                M.Mobile,
                                U.Role,
                                U.IsActive
                            FROM
                                Manager AS M
                            JOIN
                                User AS U ON M.UserID = U.ID
                            WHERE 
                            U.IsActive=1
                            AND
                            (M.FirstName LIKE %s OR M.LastName LIKE %s)

                            UNION ALL

                            SELECT
                                A.UserID,
                                A.FirstName,
                                A.LastName,
                                U.Email,
                                A.Mobile,
                                U.Role,
                                U.IsActive
                            FROM
                                Admin AS A
                            JOIN
                                User AS U ON A.UserID = U.ID
                            WHERE 
                                U.IsActive=1
                            AND
                            (A.FirstName LIKE %s OR A.LastName LIKE %s)
                            """
        search_like = "%" + search_query + "%"
        cursor.execute(sql_query, (search_like, search_like, search_like, search_like, search_like, search_like))
                                                
        staff_list = cursor.fetchall()
        return render_template('admin_staff_view_list.html', staff_list=staff_list)

#-----------------staff list edit-------------------------------------

@admin_blueprint.route('/admin/staff_list_edit/<int:user_id>', methods=['GET', 'POST'])
def staff_list_edit(user_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        # deal the form
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            mobile = request.form['mobile']
            role = request.form['role']
            
        #check if email is unique
            if email_exists_registered(email, user_id):
                flash('This email is already in use by another active user. Please enter a different email.', 'error')
                return redirect(url_for('admin.staff_list_edit', user_id=user_id))

            # Check if mobile is unique
            if mobile_exists(mobile, user_id):
                flash('Mobile number already in use! Please fill in another mobile phone number!', 'error')
                return redirect(url_for('admin.staff_list_edit', user_id=user_id))

            #chekck if mobile is valid number
            if not is_valid_phone_number(mobile):
                flash('Mobile number is invalid! Please fill in a valid mobile phone number!', 'error')
                return redirect(url_for('admin.staff_list_edit'))
            
            else:
                # update database as per role
                if role == 'Staff':
                    update_staff = """UPDATE Staff
                            SET FirstName = %s, LastName = %s, Email = %s, Mobile = %s
                            WHERE UserID = %s"""
                    cursor.execute(update_staff, (first_name, last_name, email, mobile, user_id))
            
                elif role == 'Manager':
                    update_manager = """UPDATE Manager
                            SET FirstName = %s, LastName = %s, Email = %s, Mobile = %s
                            WHERE UserID = %s"""
                    cursor.execute(update_manager, (first_name, last_name, email, mobile, user_id))

                elif role == 'Admin':
                    update_admin = """UPDATE Admin
                            SET FirstName = %s, LastName = %s, Email = %s, Mobile = %s
                            WHERE UserID = %s"""
                    cursor.execute(update_admin, (first_name, last_name, email, mobile, user_id))
                # update database to the User table
                update_user = """UPDATE User
                            SET Email = %s, Role = %s
                            WHERE ID = %s"""
                cursor.execute(update_user, (email, role, user_id))
                
                flash('Staff details updated successfully!', 'success')
                return redirect(url_for('admin.staff_list_view'))

        # get the staff info
        query = '''SELECT
                        S.UserID,
                        S.FirstName,
                        S.LastName,
                        U.Email,
                        S.Mobile,
                        U.Role,
                        U.IsActive
                    FROM
                        Staff AS S
                    JOIN
                        User AS U ON S.UserID = U.ID
                    WHERE 
                    U.IsActive=1
                    AND U.ID = %s

                    UNION ALL

                    SELECT
                        M.UserID,
                        M.FirstName,
                        M.LastName,
                        U.Email,
                        M.Mobile,
                        U.Role,
                        U.IsActive
                    FROM
                        Manager AS M
                    JOIN
                        User AS U ON M.UserID = U.ID
                    WHERE 
                    U.IsActive=1
                    AND U.ID = %s

                    UNION ALL

                    SELECT
                        A.UserID,
                        A.FirstName,
                        A.LastName,
                        U.Email,
                        A.Mobile,
                        U.Role,
                        U.IsActive
                    FROM
                        Admin AS A
                    JOIN
                        User AS U ON A.UserID = U.ID
                    WHERE 
                        U.IsActive=1
                    AND U.ID = %s
                    '''
        cursor.execute(query, (user_id, user_id, user_id))
        staff = cursor.fetchone()
        
        if staff:
            return render_template('admin_staff_list_edit.html', staff=staff)
        else:
            flash('Staff not found!', 'error')
            return redirect(url_for('admin.staff_list_view'))
    
#-----------------staff delete-------------------------------------

@admin_blueprint.route('/admin/staff_delete/<int:user_id>', methods=['GET'])
def staff_delete(user_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        # if selected role is staff update staff table - IsActive
        update_staff = """
            UPDATE Staff 
            SET IsActive = %s
            WHERE UserID = %s
        """
        cursor.execute(update_staff, (False, user_id))
    # if selected role is manager update manager table - IsActive
        update_manager = """
            UPDATE Manager 
            SET IsActive = %s
            WHERE UserID = %s
        """
        cursor.execute(update_manager, (False, user_id))
    # if selected role is admin update admin table - IsActive
        update_admin = """
            UPDATE Admin 
            SET IsActive = %s
            WHERE UserID = %s
        """
        cursor.execute(update_admin, (False, user_id))

        update_user = """
            UPDATE User
            SET IsActive = %s
            WHERE ID = %s
        """
        cursor.execute(update_user, (False, user_id))

        flash('Staff deleted successfully!', 'success')
        return redirect(url_for('admin.staff_list_view'))
    

#-----------------staff add-------------------------------------
@admin_blueprint.route('/admin/staff_add', methods=['POST'])
def staff_add():
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        # get info from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # hash password
        role = request.form['role']

        #Check if email is unique
        if email_exists_registered(email, 0):
            flash('This email is already in use by another active user. Please enter a different email.', 'error')
            return redirect(url_for('admin.staff_list_view'))
        
        #Check if mobile is unique
        if mobile_exists(mobile, 0):
            flash('Mobile number already in use! Please fill in another mobile phone number!', 'error')
            return redirect(url_for('admin.staff_list_view'))
        
        #chekck if mobile is valid number
        if not is_valid_phone_number(mobile):
            flash('Mobile number is invalid! Please fill in a valid mobile phone number!', 'error')
            return redirect(url_for('admin.staff_list_view'))
        
        #Check if password is strong
        if not is_strong_password(password):
            flash('Password must be at least 8 characters long and must contain at least one uppercase letter, one lowercase letter, one number and one special character!', 'error')
            return redirect(url_for('admin.staff_list_view'))
        
        else:
        # INSERT into user table
            cursor = getCursor()
            cursor.execute("""
                        INSERT INTO User (Email, Password, Role, IsActive)
                        VALUES (%s, %s, %s, 1)
                        """, (email, hashed_password,role))
            user_id = cursor.lastrowid #get the last id

            # INSERT into staff table if role is staff
            if role == 'Staff':
                cursor.execute("""
                    INSERT INTO Staff (UserID, FirstName, LastName, Email, Mobile, IsActive)
                    VALUES (%s, %s, %s, %s, %s, 1)
                """, (user_id, first_name, last_name, email, mobile))
            elif role == 'Manager':
                cursor.execute("""
                    INSERT INTO Manager (UserID, FirstName, LastName, Email, Mobile, IsActive)
                    VALUES (%s, %s, %s, %s, %s, 1)
                """, (user_id, first_name, last_name, email, mobile))
            elif role == 'Admin':
                cursor.execute("""
                    INSERT INTO Admin (UserID, FirstName, LastName, Email, Mobile, IsActive)
                    VALUES (%s, %s, %s, %s, %s, 1)
                """, (user_id, first_name, last_name, email, mobile))

            flash("Staff added successfully!", "success")
            return redirect(url_for('admin.staff_list_view'))
            

#-----------------customer list view-------------------------------------
@admin_blueprint.route('/admin/customer_list_view')
def customer_list_view():
    search_query = request.args.get('search', '')
    cursor = getCursor()
    sql_query = """
        SELECT *
        FROM Customer
        WHERE IsActive = 1 AND (FirstName LIKE %s OR LastName LIKE %s)
    """
    search_like = "%" + search_query + "%"
    cursor.execute(sql_query, (search_like, search_like))

    customer_list = cursor.fetchall()

    return render_template('admin_customer_list_view.html', customer_list=customer_list)


#-----------------customer list edit-------------------------------------
@admin_blueprint.route('/admin/customer_list_edit/<int:user_id>', methods=['GET', 'POST'])
def customer_list_edit(user_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        # deal the form
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            mobile = request.form['mobile']
            dob = request.form['dob']

            #check if email is unique
            if email_exists_registered(email, user_id):
                flash('This email is already in use by another active user. Please enter a different email.', 'error')
                return redirect(url_for('admin.customer_list_edit', user_id=user_id))

            # Check if mobile is unique
            if mobile_exists(mobile, user_id):
                flash('Mobile number already in use! Please fill in another mobile phone number!', 'error')
                return redirect(url_for('admin.customer_list_edit', user_id=user_id))

            #check if mobile is valid number
            if not is_valid_phone_number(mobile):
                flash('Mobile number is invalid! Please fill in a valid mobile phone number!', 'error')
                return redirect(url_for('admin.customer_list_edit'))
            
            #Check if age is valid
            if not is_valid_age(dob):
                flash('Customer must be at least 12 years old!', 'error')
                return redirect(url_for('admin.customer_list_edit'))
            
            else:
                # update database
                cursor = getCursor()
                update_customer = """UPDATE Customer 
                            SET FirstName = %s, LastName = %s,Email = %s,Mobile = %s,DateOfBirth = %s
                            WHERE UserID = %s"""
                cursor.execute(update_customer, (first_name, last_name, email, mobile, dob, user_id))
        

                flash('Customer details updated successfully!', 'success')
                return redirect(url_for('admin.customer_list_view'))

        # get the customer info
        cursor.execute("""SELECT * FROM Customer WHERE UserID = %s""", (user_id,))
        customer = cursor.fetchone()
        print(customer)
        
        if customer:
            return render_template('admin_customer_list_edit.html', customer=customer)
        else:
            flash('Customer not found!', 'error')
            return redirect(url_for('admin.customer_list_view'))
    

#-----------------customer delete-------------------------------------
@admin_blueprint.route('/admin/customer_delete/<int:user_id>', methods=['GET'])
def customer_delete(user_id):
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        cursor = getCursor()
        # update customer table - IsActive
        update_customer = """
                        UPDATE Customer 
                        SET IsActive = %s
                        WHERE UserID = %s
                        """
        cursor.execute(update_customer, (False, user_id))

        update_user = """
                        UPDATE User
                        SET IsActive = %s
                        WHERE ID = %s
                        """
        cursor.execute(update_user, (False, user_id))
        
        flash('Customer deleted successfully!', 'success')

        return redirect(url_for('admin.customer_list_view'))


#-----------------customer add-------------------------------------
@admin_blueprint.route('/admin/customer_add', methods=['POST'])
def customer_add():
    if 'loggedin' in session and session['role'] in ['Manager', 'Admin']:
        # get info from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']
        dob = request.form['dob']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        #Check if email is unique
        if email_exists_registered(email, 0):
            flash('This email is already in use by another active user. Please enter a different email.', 'error')
            return redirect(url_for('admin.customer_list_view'))
        
        #Check if mobile is unique
        if mobile_exists(mobile, 0):
            flash('Mobile number already in use! Please fill in another mobile phone number!', 'error')
            return redirect(url_for('admin.customer_list_view'))
        
        #check if mobile is valid number
        if not is_valid_phone_number(mobile):
            flash('Mobile number is invalid! Please fill in a valid mobile phone number!', 'error')
            return redirect(url_for('admin.customer_list_view'))
        
        #Check if password is strong
        if not is_strong_password(password):
            flash('Password must be at least 8 characters long and must contain at least one uppercase letter, one lowercase letter, one number and one special character!', 'error')
            return redirect(url_for('admin.customer_list_view'))
        
        #Check if age is valid
        if not is_valid_age(dob):
            flash('Customer must be at least 12 years old!', 'error')
            return redirect(url_for('admin.customer_list_view'))
        
        else:
            # INSERT into user table
            cursor = getCursor()
            cursor.execute("""
                        INSERT INTO User (Email, Password, Role, IsActive)
                        VALUES (%s, %s, 'Customer', 1)
                        """, (email, hashed_password))
            user_id = cursor.lastrowid

            # INSERT into customer table
            cursor.execute("""
                        INSERT INTO Customer (UserID, FirstName, LastName, Email, Mobile, DateOfBirth, IsActive)
                        VALUES (%s, %s, %s, %s, %s, %s, 1)
                        """, (user_id, first_name, last_name, email, mobile, dob))
            
            flash("Customer added successfully!", "success")
            return redirect(url_for('admin.customer_list_view'))
        
        
#-----------------Reprot generate-------------------------------------
        
@admin_blueprint.route('/reports/', methods=['GET', 'POST'])
def reports():
    if 'loggedin' in session and session['role'] in ['Manager','Admin']:
          if request.method == 'POST':
            reportType = request.form.get('reportType')
            return redirect(url_for('admin.reports_generate', reportType=reportType))
    return render_template('reports.html')
        
@admin_blueprint.route('/reports/<reportType>', methods=['GET', 'POST'])
def reports_generate(reportType):
    if 'loggedin' in session and session['role'] in ['Manager','Admin']:
        # Pass data to the template for monthly income report
        if reportType == 'monthly_income':
            monthly_income_data = get_monthly_income_data()
            # Initialize dictionary with all months and zero income
            all_months_income = {
                'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0,
                'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0
            }
            # Update dictionary with actual data
            for row in monthly_income_data:
                all_months_income[row[0]] = row[1]
            # Convert to list of dictionaries
            monthly_income = [{'Month': month, 'MonthlyIncome': income} for month, income in all_months_income.items()]
            totalIncome = sum(all_months_income.values())
            return render_template('monthly_income_report.html', reportType=reportType,monthly_income=monthly_income, 
                               monthly_income_data=monthly_income_data, totalIncome=totalIncome)
        
        # Pass data to the template for income by category report
        elif reportType == 'income_by_category':
            income_by_category_data = get_income_by_category()
            return render_template('income_by_category_report.html', reportType=reportType,
                                income_by_category_data=income_by_category_data)
        
        # Pass data to the template for income by week of date report
        elif reportType == 'week_of_date':
            income_by_day_of_week_data = get_income_by_day_of_week()
            return render_template('week_of_date_report.html', reportType=reportType,
                                income_by_day_of_week_data=income_by_day_of_week_data)
        
        # Pass data to the template for top movies report
        elif reportType == 'popularity':
            top_movies_data = get_top_movies_data()
            return render_template('popularity_report.html', reportType=reportType,
                                top_movies_data=top_movies_data)
        
        # Pass data to the template for payment methods report
        elif reportType == 'payment_methods':
            payment_methods_data = get_payment_methods_data()
            totalIncome = sum([row['income_per_paymentMethods'] for row in payment_methods_data])
            return render_template('payment_methods_report.html', reportType=reportType,
                                payment_methods_data=payment_methods_data, totalIncome=totalIncome)
        
        # Pass data to the template for ticket type report
        elif reportType == 'ticket_type':
            movie_sale_list_data = get_movie_sale_list_data()
            ticket_type_data = get_ticket_type_data()
            
            return render_template('ticket_type_report.html', reportType=reportType,
                                ticket_type_data = ticket_type_data, movie_sale_list_data=movie_sale_list_data)
        
        else:
            return render_template('reports.html', reportType=reportType)
    

#this function is to retrieve the monthly income data to JS in monthly_income_report.html
def get_monthly_income_data():
    cursor = getCursor()
    sql_query = """SELECT
                        DATE_FORMAT(S.Date, '%b') AS Month,
                        SUM(P.TotalAmount) AS MonthlyIncome
                    FROM
                        Payment P
                        JOIN Booking B ON P.BookingID = B.ID
                        JOIN Session S ON B.Session = S.ID
                    WHERE
                        S.Date BETWEEN '2024-01-01' AND '2024-12-31'
                    GROUP BY
                        Month
                    ORDER BY
                        STR_TO_DATE(CONCAT('2024-', Month, '-01'), '%Y-%b-%d');
                        """
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
    finally:
        cursor.close()
    return result


#this function is to retrieve the Genre data to JS in income_by_category_report.html
def get_income_by_category():
    cursor = getCursor()
    sql_query = """SELECT
                        G.ID AS GenreID,
                        G.Name AS GenreName,
                        COALESCE(SUM(TT.Price), 0) AS GenreIncome
                    FROM
                        Genre AS G
                    LEFT JOIN
                        Movie AS M ON G.ID = M.Genre
                    LEFT JOIN
                        Session AS S ON M.ID = S.Movie
                    LEFT JOIN
                        Booking AS B ON S.ID = B.Session
                    LEFT JOIN
                        Ticket AS T ON B.ID = T.Booking
                    LEFT JOIN
                        SessionSeat AS SS ON T.SessionSeat = SS.ID
                    LEFT JOIN
                        TicketType AS TT ON T.TicketType = TT.ID
                    GROUP BY
                        G.ID, G.Name;"""
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        formatted_result = [{'GenreID': row[0], 'GenreName': row[1], 'GenreIncome': float(row[2])} for row in result]
    finally:
        cursor.close()  
    #list to show the catagory name
    return formatted_result

#this function is to retrieve the day of week income to JS in week_of_date_report.html
def get_income_by_day_of_week():
    cursor = getCursor()
    sql_query = """
                SELECT
                    DaysOfWeek.DayOfWeek,
                    COALESCE(SUM(TT.Price), 0) AS DailyIncome
                FROM
                    (SELECT 'Monday' AS DayOfWeek UNION SELECT 'Tuesday' UNION SELECT 'Wednesday' UNION SELECT 'Thursday' 
                     UNION SELECT 'Friday' UNION SELECT 'Saturday' UNION SELECT 'Sunday') AS DaysOfWeek
                LEFT JOIN
                    Session S ON DaysOfWeek.DayOfWeek = DAYNAME(S.Date)
                LEFT JOIN
                    Booking B ON S.ID = B.Session
                LEFT JOIN
                    Ticket T ON B.ID = T.Booking
                LEFT JOIN
                    TicketType TT ON T.TicketType = TT.ID
                GROUP BY
                    DaysOfWeek.DayOfWeek;
                """
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        formatted_result = [{'DayOfWeek': row[0], 'DailyIncome': float(row[1])} for row in result]
    finally:
        cursor.close()
    return formatted_result
    

#this function is to retrieve the top movies data to JS in popularityreport.html
def get_top_movies_data():
    cursor = getCursor()
    sql_query = """
        SELECT 
            M.Title,
            COUNT(T.ID) as TotalTicketsSold,
            COALESCE(SUM(TT.Price), 0) AS TotalIncome
        FROM 
            Movie M
        JOIN 
            Session S ON M.ID = S.Movie
        JOIN 
            Booking B ON S.ID = B.Session
        JOIN 
            Ticket T ON B.ID = T.Booking
        JOIN 
            TicketType TT ON T.TicketType = TT.ID
        WHERE 
            YEAR(S.Date) = YEAR(CURDATE())
        GROUP BY 
            M.Title
        ORDER BY 
            TotalTicketsSold DESC
        LIMIT 5;
    """
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
    finally:
        cursor.close()
    return [{'movie_title': row[0], 'total_tickets_sold': row[1], 'total_income': row[2]} for row in result]


#this function is to retrieve the movie sale ticket type data to JS in tickettypereport.html
def get_ticket_type_data():
    cursor = getCursor()
    sql_query = """
                SELECT
                    TT.TypeName AS TicketType,
                    COUNT(T.ID) AS TicketsSold,
                    SUM(TT.Price) AS Income
                FROM
                    Ticket T
                JOIN
                    TicketType TT ON T.TicketType = TT.ID
                GROUP BY
                    TicketType;
                """
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
    finally:
        cursor.close()
    return [{'ticket_type': row[0], 'tickets_sold': row[1], 'income_per_ticketType': row[2]} for row in result]


#this fuction is to retrieve the movie sale list data as per ticket type to JS in tickettypereport.html
def get_movie_sale_list_data():
    cursor = getCursor()
    sql_query = """
                SELECT
                    M.Title AS MovieTitle,
                    SUM(CASE WHEN TT.TypeName = 'Children' THEN 1 ELSE 0 END) AS Children,
                    SUM(CASE WHEN TT.TypeName = 'Adult' THEN 1 ELSE 0 END) AS Adult,
                    SUM(CASE WHEN TT.TypeName = 'Senior' THEN 1 ELSE 0 END) AS Senior,
                    SUM(CASE WHEN TT.TypeName = 'Student' THEN 1 ELSE 0 END) AS Student,
                    COUNT(T.ID) AS TotalTicketsSold,
                    COALESCE(SUM(TT.Price), 0) AS TotalIncome
                FROM
                    Ticket T
                JOIN
                    TicketType TT ON T.TicketType = TT.ID
                JOIN
                    Booking B ON T.Booking = B.ID
                JOIN
                    Session S ON B.Session = S.ID
                JOIN
                    Movie M ON S.Movie = M.ID
                GROUP BY
                    MovieTitle;
                """
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
    finally:
        cursor.close()
        return result


#this function is to retrieve the payment methods data to JS in paymentmethodsreport.html
def get_payment_methods_data():
    cursor = getCursor()
    sql_query = """
                SELECT
                    CASE
                        WHEN PaymentMethod = 'internetBanking' THEN 'Internet Banking'
                        WHEN PaymentMethod = 'giftCard' THEN 'Gift Card'
                        WHEN PaymentMethod = 'creditCard' THEN 'Credit Card'
                        ELSE PaymentMethod
                    END AS DisplayPaymentMethod,
                    COUNT(DISTINCT Booking.ID) AS Bookings,
                    SUM(TotalAmount) AS Income
                FROM
                    Payment
                JOIN
                    Booking ON Payment.BookingID = Booking.ID
                GROUP BY
                    PaymentMethod;

                """
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
    finally:
        cursor.close()
    return [{'payment_method': row[0], 'bookings_per_paymentMethods': row[1], 'income_per_paymentMethods': row[2]} for row in result]

#--------------Category Management----------------------------
@admin_blueprint.route('/admin/movie_category', methods=['GET'])
def movie_category():
    if 'loggedin' in session and session['role'] in ['Admin']:
        cursor = getCursor()
        cursor.execute("SELECT * FROM Genre")
        genre_list = cursor.fetchall()
        cursor.execute("SELECT * FROM Rating")
        rating_list = cursor.fetchall()

        return render_template('movie_category.html', genre_list=genre_list, rating_list=rating_list)


# Route to add a new genre or rating
@admin_blueprint.route('/admin/movie_category/add_category', methods=['POST'])
def add_category():
    if 'loggedin' in session and session['role'] in ['Admin']:
        cursor = getCursor()
        if request.method == 'POST':
            category = request.form['category']  
            new_category = request.form['newCategory']
            #check if the category is valid     
            if category == 'genre':
                if new_category == '':
                    flash('Please enter a valid Genre', 'error')
                    return redirect(url_for('admin.movie_category'))
                #check if the input is more than 10 characters and characters only
                if len(new_category) > 10 or len(new_category) < 2 or not new_category.isalpha():
                    flash('Genre must be less than 10 characters, more than 2 characters and Alphabet only', 'error')
                    return redirect(url_for('admin.movie_category'))
                new_category_capitalized = new_category.capitalize()
                if category_exists(category, new_category_capitalized):
                    flash(f'"{new_category_capitalized}" already exists as Genre', 'error')
                    return redirect(url_for('admin.movie_category'))
                cursor = getCursor()
                cursor.execute("INSERT INTO Genre (Name) VALUES (%s)", (new_category_capitalized,))
                flash(f'"{new_category_capitalized}" added as Genre successfully', 'success')
         

            elif category == 'rating':
                if new_category == '':
                    flash('Please enter a valid Rating', 'error')
                    return redirect(url_for('admin.movie_category'))
                #check if the input is more than 10 characters
                if new_category.isdigit() or len(new_category) > 10 :
                    flash('Rating must be less than 10 characters and must not be just numbers', 'error')
                    return redirect(url_for('admin.movie_category'))
                new_category_upper = new_category.upper()
                if category_exists(category, new_category_upper):
                    flash(f'"{new_category_upper}" already exists as Rating', 'error')
                    return redirect(url_for('admin.movie_category'))
                cursor = getCursor()
                cursor.execute("INSERT INTO Rating (Rating) VALUES (%s)", (new_category_upper,))
                flash(f'"{new_category_upper}" added as Rating successfully', 'success')
            return redirect(url_for('admin.movie_category'))
        
        
#function to add validation to check if the category is valis enter and if it is already exists
def category_exists(category, new_category):
    if category == 'genre':
        cursor = getCursor()
        new_category_capitalized = new_category.capitalize()
        cursor.execute("SELECT * FROM Genre WHERE Name = %s", (new_category_capitalized,))
        genre = cursor.fetchone()
        if genre:
            return True
        else:
            return False
    elif category == 'rating':
        cursor = getCursor()
        new_category_upper = new_category.upper()
        cursor.execute("SELECT * FROM Rating WHERE Rating = %s", (new_category_upper,))
        rating = cursor.fetchone()
        if rating:
            return True
        else:
            return False

# route to delete a genre or rating when there is no movie associated with it
@admin_blueprint.route('/admin/movie_category/delete_category', methods=['GET', 'POST'])
def delete_category():
    if 'loggedin' in session and session['role'] in ['Admin']:
        cursor = getCursor()
        if request.method == 'POST':
            category = request.form['category']
            #check if the category is genre or rating
            if category == 'genre':
                category_id = request.form['genreToDelete']
                cursor.execute("SELECT * FROM Movie WHERE Genre = %s", (category_id,))
                movie = cursor.fetchone()
                if movie:
                    flash('Cannot delete Genre as it has movies associated with it', 'error')
                    return redirect(url_for('admin.movie_category'))
                else:
                    cursor.execute("DELETE FROM Genre WHERE ID = %s", (category_id,))
                    flash('Genre deleted successfully', 'success')
                    return redirect(url_for('admin.movie_category'))
                
            elif category == 'rating':
                category_id = request.form['ratingToDelete']
                cursor.execute("SELECT * FROM Movie WHERE Rating = %s", (category_id,))
                movie = cursor.fetchone()
                if movie:
                    flash('Cannot delete Rating as it has movies associated with it', 'error')
                    return redirect(url_for('admin.movie_category'))
                else:
                    cursor.execute("DELETE FROM Rating WHERE ID = %s", (category_id,))
                    flash('Rating deleted successfully', 'success')
                    return redirect(url_for('admin.movie_category'))
        
    else:
        return redirect(url_for('login'))

        