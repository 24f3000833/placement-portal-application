from app import app , db
from models import Admin
from werkzeug.security import generate_password_hash
import os 
from dotenv import load_dotenv

load_dotenv()

with app.app_context():
    db.create_all()

    admin = Admin.query.filter_by(username=os.environ.get("ADMIN_USERNAME")).first()

    if not admin:
        hashed_pass=generate_password_hash(os.environ.get("ADMIN_PASSWORD"))
        admin=Admin(username=os.environ.get("ADMIN_USERNAME"), password=hashed_pass) #Stores admin detail in admin table
        db.session.add(admin)
        db.session.commit()
        print("Databse created Successfully...\nPrint Admin account created..")
    else:
        print("Database already exist..\nAdmin Already exist!!")
    