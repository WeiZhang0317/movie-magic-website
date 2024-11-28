# As a customer, I want to view and purchase gift cards of different values, so that I can give them to other people as a gift. The gift card can be used by entering a card number.

# Criteria:

# A special catalogue or section called “gift shop”
# Three different types of gift cards available, they are: value$25, value$50, value$100
# customer can choose the number of gift cards to purchase

#   Rules for using gift cards:
#  When checking out, customer can choose to enter the gift card number to use the balance of the gift card. If the gift card balance is insufficient to cover the full amount, the remaining sum to be paid will be displayed.
# Can be used in conjunction with a promotion code and gift card. The total amount will display the discounted amount. 

from flask import Flask, Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask import render_template
import mysql.connector
import connect
import uuid
from decimal import Decimal


app = Flask(__name__)
gift_card_blueprint = Blueprint('gift_card', __name__)
user_blueprint = Blueprint('user', __name__)

def getCursor(dictionary_cursor=False):
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, database=connect.dbname, autocommit=True)
    cursor = connection.cursor(dictionary=dictionary_cursor)
    return cursor

@gift_card_blueprint.route('/gift_cards')
def gift_cards():
    return render_template('gift_cards.html')

@gift_card_blueprint.route('/gift_cards_choose')
def gift_cards_choose():
    # Check if the user is logged in
    if 'user_id' in session:
        # Process logic for users who are logged in
        return render_template('gift_cards_choose.html')
    else:
        # Redirect to the login page for users who are not logged in
        return redirect(url_for('user.login', login_source='gift_cards'))

@gift_card_blueprint.route('/gift_cards_payment', methods=['POST'])
def gift_cards_payment():

    selected_image = request.form.get('selectedImage') 
    card_style = request.form.get('cardStyle')
    card_type = request.form.get('cardType')
    quantity = int(request.form.get('quantity'))

    your_name = request.form.get('yourName')
    recipients_name = request.form.get('recipientsName')
    recipients_email = request.form.get('recipientsEmail')
    special_message = request.form.get('specialMessage')

    


    total_price = int(card_type) * quantity


    return render_template('gift_cards_payment.html', selected_image=selected_image, your_name=your_name, recipients_name=recipients_name,
                           recipients_email=recipients_email, special_message=special_message,
                           card_style=card_style, card_type=card_type, quantity=quantity,
                           total_price=total_price)


@gift_card_blueprint.route('/gift_cards_payment-success', methods=['GET', 'POST'])
def payment_success():
    if request.method == 'POST':
        # Get data from the form submission
        img_path = request.form.get('selected_image')
        email = request.form.get('recipients_email')
        card_type = request.form.get('card_type')
        quantity = int(request.form.get('quantity'))

        # Insert data into the GiftCard table
        cursor = getCursor()
        query = "INSERT INTO GiftCard (Number, Email, Balance, Type, ImgPath) VALUES (%s, %s, %s, %s, %s)"
        for _ in range(quantity):
            values = (generate_card_number(), email, calculate_balance(card_type), card_type, img_path)
            cursor.execute(query, values)
        cursor.close()
        connection.close()


    return render_template('gift_cards_payment-success.html')


def generate_card_number():
    # Generate a unique card number using UUID
    return str(str(uuid.uuid4().int)[:9])

def calculate_balance(card_type):
    # Convert card type to decimal for balance
    return Decimal(card_type)



if __name__ == '__main__':
    app.secret_key = 'your_secret_key'  
    app.register_blueprint(gift_card_blueprint)
    app.run(debug=True)
