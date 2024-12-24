from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
import cloudinary
import os
from flask_login import LoginManager
import atexit # To register shutdown callback
from task import scheduler
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4" % quote("1234") #minh
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4" % quote("My123456") #my
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4" % quote("0420") #kiet

app.secret_key = 'aweut9n8*@$*djhfjsadhfsdqefsfgasedq23i'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 9
app.config["COMMENT_PAGE_SIZE"] = 4
app.config["BOOKING_DEADLINE_DAYS"] = 28
app.config["CHECK_INTERVAL_HOURS"] = 24

# Remove Flask's default log handler to prevent it from logging to the file
app.logger.handlers = []

# Set up logging to a file with rotation
log_handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=3)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the handler to the custom logger
logger = logging.getLogger("task_logger")  # Use a specific logger name for your tasks
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)


def clear_log_on_shutdown():
    log_file_path = 'app.log'  # Adjust the log file path as needed
    if os.path.exists(log_file_path):
        with open(log_file_path, 'w'):  # Open in write mode to truncate
            pass  # This will clear the file content


db = SQLAlchemy(app)

cloudinary.config(cloud_name='dhhpxhskj',
                  api_key='398599846358987',
                  api_secret='jNqe-OCxgo98G-K6_OAL0nuvyEk')

login = LoginManager(app)

from task import schedule_periodic_task

schedule_periodic_task()

atexit.register(lambda: scheduler.shutdown())
atexit.register(clear_log_on_shutdown)