# As a customer, I want to see offers and promotions, so that I can take advantage of special discounts and deals.

# Criteria:

# A dedicated section for offers and promotions
# An introduction about “Tuesday Daytime Discount” (high-light): “50% for all Tuesday Daytime session movies. “
# An introduction about the New customer promotion code: “If you are a new customer, enter the code when checking out to get 15$ off the total price.”
 
# An introduction about discount conjunction “When check out, all Tuesday daytime sessions should automatically display a 50% discount, which can be used in conjunction with the promotion code and gift card. The total amount will display the discounted amount. “

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

promotion_blueprint = Blueprint('promotion', __name__)

def getCursor():
    global dbconn
    global cursor
    cursor = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = cursor.cursor()
    return dbconn

@promotion_blueprint.route('/promotions')
def promotions():
    cursor = getCursor()

    cursor.execute("SELECT * FROM Coupon" )  
    coupon = cursor.fetchall()

    cursor.execute("SELECT * FROM WeeklyDiscounts" ) 
    discount = cursor.fetchall()

    cursor.close()
    return render_template('promotions.html', coupon=coupon, discount=discount)

