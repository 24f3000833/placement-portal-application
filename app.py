from flask import Flask , render_template , request, redirect,url_for,session , flash , Response
from models import db , Admin , Company , Student , PlacementDrive, Application
from werkzeug.security import generate_password_hash , check_password_hash
from werkzeug.utils import secure_filename
import os


app= Flask(__name__)
app.config["SECRET_KEY"]="placementportaljan26"  #USed to encrypt session data and keeps login into safe
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///placement.db"  #CReate placement.db file and store all 5 tables 
app.config["SQLALCHEMY_TRACK_MODIFICATION"]=False  #Removes unneccessary features and saves memory anbd time
app.config["UPLOAD_FOLDER"]="static/upload"  #Stores the uploaded file (certificate and resumnes)
app.config["MAX_CONTENT_LENGTH"]=16*1024*1024   #Max file upload size = 16MB


db.init_app(app)
