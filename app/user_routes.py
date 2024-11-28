from flask import Blueprint, render_template, url_for, request, redirect
from flask import Flask, session
from flask import Flask, flash
from datetime import date
import mysql.connector
import connect
import bcrypt
import re 
from datetime import datetime
from app.main_routes import getCursor


user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():

    connection = getCursor()
    error_message = {}

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        query = """
        SELECT ID, Email, Password, Role
        FROM User
        WHERE IsActive = TRUE AND Email = %s
        """

        connection.execute(query, (email,))
        user = connection.fetchone()

        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                session['loggedin'] = True
                session['user_id'] = user[0]
                session['email'] = user[1]
                session['role'] = user[3]
                # Determine the dashboard based on the user's role
                if session['role'] == 'Admin':
                    return redirect(url_for('admin.admin_dashboard')) # tested ok
                elif session['role'] == 'Staff':
                    return redirect(url_for('staff.staff_dashboard')) # tested ok
                elif session['role'] == 'Customer':
                    return redirect(url_for('customer.customer_dashboard')) # tested ok
                elif session['role'] == 'Manager':
                    return redirect(url_for('manager.manager_dashboard')) # pending
                else:
                    flash('Unknown role. Please contact support.', 'danger')
                
            else:
                 error_message['password'] = 'Incorrect password.'

        else:
                error_message['email'] = 'User does not exist.'
        
   
    return render_template('login.html', error_message=error_message)

@user_blueprint.route('/logout')
def logout():
    # delete session
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('role', None)

    flash('You have been logged out.', 'success')

    return redirect(url_for('main.home'))

@user_blueprint.route('/register', methods=['GET', 'POST']) 
def register():

    error_message = {}

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        date_of_birth = request.form.get('dob')
        plain_text_password = request.form.get('password')
        role = 'customer'  # Set a default role for registered users

        # Validate age (must be 12 years or older)
        if not is_valid_age(date_of_birth):
            error_message['dob'] = 'You must be 12 years or older to register.'        

        
        if email_exists(email):
            error_message['email'] = 'Email is already registered.'

        # Validate phone number (check if it's numeric and has at least 10 digits)
        if not is_valid_phone_number(phone_number):
            error_message['phone_number'] = 'Mobile Phone number shoule be at least 10 digits.'

        if not is_strong_password(plain_text_password):
            error_message['password'] = 'Password must be at least five characters.'

        if not error_message: 
            print("no error")   
            try:
                # hashed the plain text number
                hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
                connection = getCursor()
                # Insert into Users table
                connection.execute('INSERT INTO User (Email, Password, Role) VALUES (%s, %s, %s)',
                               (email, hashed_password, role))
                user_id = connection.lastrowid  # Get the auto-incremented user_id

                # Insert into Customer table
                connection.execute('INSERT INTO Customer (UserID, FirstName, LastName, Email, Mobile, DateOfBirth) VALUES (%s, %s, %s, %s, %s, %s)',
                               (user_id, first_name, last_name, email, phone_number, date_of_birth))

                flash('Registration successful!', 'success')
                return redirect(url_for('user.login'))


        
            except Exception as e:
                print("Registration failed. Error:", str(e))
                flash('Registration failed. Please try again.', 'danger')
                return redirect(url_for('user.register'))
    

    return render_template('register.html', error_message=error_message)
  
def is_valid_age(date_of_birth):
    # Calculate age based on current date and provided date of birth
    birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    # Check if age is 12 years or older
    return age >= 12
# Function to validate password strength
def is_strong_password(password):
    # Check if it has at least 5 characters
    return len(password) >= 5

# Function to check if email already exists in the database
def email_exists(email):
    connection = getCursor()
    query = "SELECT ID FROM User WHERE Email = %s"
    connection.execute(query, (email,))
    result = connection.fetchone()
    print(result)
    connection.close()
    return result is not None

# Function to validate phone number format
def is_valid_phone_number(phone_number):
    nz_phone_pattern = r"\d{2,3}\s*\d{3}\s*\d{3,4}"
    return re.match(nz_phone_pattern, phone_number)

@user_blueprint.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html')


@user_blueprint.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@user_blueprint.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

@user_blueprint.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')

#this is the function for all users to view their profile
@user_blueprint.route('/profile')
def profile():
    if session['loggedin'] :
        connection = getCursor()
        id = session['user_id']
        if request.method == 'GET':
            if session['role'] == 'Admin': 
                query = 'SELECT * FROM Admin WHERE UserID = %s;'
                # if user role is staff, get staff details
            elif session['role'] == 'Staff': 
                query = 'SELECT * FROM Staff WHERE UserID = %s;'
                # if user role is customer, get customer details
            elif session['role'] == 'Customer': 
                query = 'SELECT * FROM Customer WHERE UserID = %s;'
            else: 
                query = 'SELECT * FROM Manager WHERE UserID = %s;' 
            connection.execute(query,(id,))

            account = connection.fetchone()
            return render_template('profile.html',account=account)
        

#this is the fuction for all users to update their email address
@user_blueprint.route('/profile/update_email', methods=['GET', 'POST'])
def update_email():
    if session['loggedin'] :
        if request.method == 'GET':
            return render_template('update_email.html')
        if request.method == 'POST':
            connection = getCursor(dictionary_cursor=False)
            connection.execute('select * from User where ID = %s',(session['user_id'],))
            user = connection.fetchone()
            updated_email = request.form.get('email')
            # if user role is admin, update email address in admin table
            if email_exists_registered(updated_email, session['user_id']):
                print("already")
                return render_template('update_email.html', msg = 'Email is already registered.')
            if session['role'] == 'Admin': #test ok
                connection= getCursor(dictionary_cursor=False)
                query = f'''UPDATE Admin SET Email = "{updated_email} "'''
                connection.execute(query)
                updated_query =  f'''select * from Admin WHERE UserID = {session['user_id']}'''
            # if user role is staff, update email address in staff table
            elif session['role'] == 'Staff': #pending
                connection= getCursor(dictionary_cursor=False)
                query = f'''UPDATE Staff SET Email = "{updated_email}"'''
                connection.execute(query)
                updated_query = f'''select * from Staff WHERE UserID = {session['user_id']}'''
            # if user role is customer, update email address in customer table
            elif session['role'] == 'Customer': #pending
                connection= getCursor(dictionary_cursor=False)
                query = f'''UPDATE Customer SET Email = "{updated_email}"'''
                connection.execute(query)
                updated_query = f'''select * from Customer WHERE UserID = {session['user_id']}'''
            # if user role is manager, update email address in manager table
            else: #pending
                connection= getCursor(dictionary_cursor=False)
                query = f'''UPDATE Manager SET Email = "{updated_email}"'''
                connection.execute(query)
                updated_query = f'''select * from Manager WHERE UserID = {session['user_id']}'''

            connection.execute(updated_query)
            account = connection.fetchone()
            flash('Email updated successfully!', 'success')
            return render_template('profile.html', account=account, user=user)

    
#this is the fuction for all users to update their mobile    
@user_blueprint.route('/profile/update_mobile', methods=['GET', 'POST'])
def update_mobile():
    if session['loggedin'] :
        if request.method == 'GET':
            return render_template('update_mobile.html')
        if request.method == 'POST':
            connection = getCursor(dictionary_cursor=False)
            connection.execute('select * from User where ID = %s',(session['user_id'],))
            user = connection.fetchone()
            updated_mobile = request.form.get('mobile')
            if mobile_exists(updated_mobile, session['user_id']):
                return render_template('update_mobile.html', msg = 'Mobile number is already registered.')
            if not is_valid_phone_number(updated_mobile):
                return render_template('update_mobile.html', msg = 'Mobile Phone number should be at least 10 digits.')
            else:
            # if user role is admin, update mobile number in admin table
                if session['role'] == 'Admin': #test ok
                    connection= getCursor(dictionary_cursor=False)
                    query = f'''UPDATE Admin SET Mobile = "{updated_mobile}"'''
                    connection.execute(query)
                    updated_query = f'''select * from Admin WHERE UserID = {session['user_id']}'''
                # if user role is staff, update mobile number in staff table
                elif session['role'] == 'Staff': #pending
                    connection= getCursor(dictionary_cursor=False)
                    query = f'''UPDATE Staff SET Mobile = "{updated_mobile}"'''
                    connection.execute(query)
                    updated_query = f'''select * from Staff WHERE UserID = {session['user_id']}'''
                # if user role is customer, update mobile number in customer table
                elif session['role'] == 'Customer': #pending
                    connection= getCursor(dictionary_cursor=False)
                    query = f'''UPDATE Customer SET Mobile = "{updated_mobile}"'''
                    connection.execute(query)
                    updated_query = f'''select * from Customer WHERE UserID = {session['user_id']}'''
                # if user role is manager, update mobile number in manager table
                else: #pending
                    connection= getCursor(dictionary_cursor=False)
                    query = f'''UPDATE Manager SET Mobile = "{updated_mobile}"'''
                    connection.execute(query)
                    updated_query = f'''select * from Manager WHERE UserID = {session['user_id']}'''

                connection.execute(updated_query)
                account = connection.fetchone()
                flash('Mobile phone number updated successfully!', 'success')
                return render_template('profile.html', account=account, user=user)


#this is the fuction for all users to change their password
@user_blueprint.route('/profile/change_password', methods=['GET', 'POST'])
def change_password():
    if session['loggedin'] :
        if request.method == 'GET':
            return render_template('change_password.html')
        if request.method == 'POST':
            ID = session['user_id']
            old_password = request.form.get('old_password')
            #check old password
            if not check_credentials(ID=ID, password=old_password):
                return render_template('change_password.html', msg='Old password is incorrect')
            #check both new passwords are the same

            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not is_strong_password(new_password):
                return render_template('change_password.html', msg='Password must be at least five characters.')

            if new_password == old_password:
                return render_template('change_password.html', msg='New password cannot be the same as old password.')
            
            if new_password != confirm_password:
                return render_template('change_password.html', msg='New passwords do not match')
            #hash new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            connection = getCursor(dictionary_cursor=False)
            connection.execute(f'UPDATE User SET Password = "{hashed_password.decode()}" WHERE ID = {ID}')
            return render_template('change_password.html', msg='Change password successfully')


#check credentials function
#this function is used to check if the user input the correct password
def check_credentials(ID, password):
    connection = getCursor(dictionary_cursor=False)
    connection.execute(f'SELECT * FROM User WHERE ID = {ID}')
    user = connection.fetchone()
    if user is not None:
        if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return True
    return False


#function to check if mobile exists
def mobile_exists(mobile,user_id):
    cursor = getCursor()
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
            ) AS mobile_exists
        """
    cursor.execute(query, (mobile, user_id, mobile, user_id, mobile, user_id, mobile, user_id))
    result = cursor.fetchone()
    cursor.close()
    return result[0] == 1

def email_exists_registered(email, user_id):
    cursor = getCursor()
    query = """SELECT EXISTS (SELECT 1 FROM User WHERE IsActive = 1 AND Email = %s AND ID != %s) AS email_exists"""
    cursor.execute(query, (email, user_id))
    result = cursor.fetchone()
    cursor.close()
    return result[0] == 1
